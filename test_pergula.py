#!/usr/bin/env python3
"""Tests for pergula.

Standard library only, like the thing it tests: pergula's whole premise is that
it depends on nothing, and a test suite that needs pytest installed would be the
first crack in that.

    python3 test_pergula.py

The bias here is toward what fails *silently*. The incremental parse keeps a byte
offset and can duplicate or drop messages without ever raising; the 204
short-circuit can quietly serve a stale response; a translation key can go
missing and merely render as its own name. Those get the most attention. Code
that fails loudly needs less help.
"""

import importlib.machinery
import importlib.util
import json
import re
import tempfile
import unittest
import xml.etree.ElementTree as ElementTree
from pathlib import Path
from urllib.parse import unquote

loader = importlib.machinery.SourceFileLoader("pergula", str(Path(__file__).parent / "pergula"))
spec = importlib.util.spec_from_loader("pergula", loader)
pergula = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pergula)


def record(text, role="user", stamp="2026-01-01T00:00:00.000Z", **extra):
    """One conversation line, in the shape the CLI writes."""
    body = {"type": role, "timestamp": stamp, "message": {"role": role, "content": text}}
    body.update(extra)
    return json.dumps(body) + "\n"


class TempTranscript(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.path = self.dir / "session.jsonl"
        pergula._MESSAGE_CACHE.clear()
        pergula._META_CACHE.clear()

    def texts(self, path=None):
        return [m["text"] for m in pergula.parse_transcript(path or self.path)]


class IncrementalParse(TempTranscript):
    """The offset bookkeeping. Every failure here is silent."""

    def test_reads_every_message(self):
        self.path.write_text("".join(record(f"m{i}") for i in range(5)))
        self.assertEqual(self.texts(), [f"m{i}" for i in range(5)])

    def test_append_adds_only_the_new_lines(self):
        self.path.write_text("".join(record(f"m{i}") for i in range(3)))
        self.texts()

        with self.path.open("a") as handle:
            handle.write("".join(record(f"m{i}") for i in range(3, 6)))

        self.assertEqual(self.texts(), [f"m{i}" for i in range(6)])

    def test_append_does_not_duplicate(self):
        self.path.write_text("".join(record(f"m{i}") for i in range(3)))
        self.texts()

        with self.path.open("a") as handle:
            handle.write(record("m3"))

        found = self.texts()
        self.assertEqual(len(found), len(set(found)))

    def test_partial_line_is_ignored_until_complete(self):
        """A live session is mid-write; half a line must not be parsed."""
        self.path.write_text(record("m0"))
        self.texts()

        with self.path.open("a") as handle:
            handle.write('{"type":"user","message":{"role":"user","conte')
        self.assertEqual(self.texts(), ["m0"])

        with self.path.open("a") as handle:
            handle.write('nt":"m1"},"timestamp":"t"}\n')
        self.assertEqual(self.texts(), ["m0", "m1"])

    def test_shrinking_file_invalidates_the_cache(self):
        self.path.write_text("".join(record(f"m{i}") for i in range(5)))
        self.texts()

        self.path.write_text(record("only"))
        self.assertEqual(self.texts(), ["only"])

    def test_unchanged_file_reuses_the_cache(self):
        self.path.write_text(record("m0"))
        first = pergula.parse_transcript(self.path)
        self.assertIs(first, pergula.parse_transcript(self.path))

    def test_cache_evicts_least_recently_used(self):
        paths = []
        for i in range(pergula.MESSAGE_CACHE_LIMIT + 3):
            path = self.dir / f"s{i}.jsonl"
            path.write_text(record(f"m{i}"))
            pergula.parse_transcript(path)
            paths.append(path)

        self.assertEqual(len(pergula._MESSAGE_CACHE), pergula.MESSAGE_CACHE_LIMIT)
        self.assertNotIn(str(paths[0]), pergula._MESSAGE_CACHE)
        self.assertIn(str(paths[-1]), pergula._MESSAGE_CACHE)

    def test_touching_a_cached_file_saves_it_from_eviction(self):
        paths = []
        for i in range(pergula.MESSAGE_CACHE_LIMIT):
            path = self.dir / f"s{i}.jsonl"
            path.write_text(record(f"m{i}"))
            pergula.parse_transcript(path)
            paths.append(path)

        pergula.parse_transcript(paths[0])

        overflow = self.dir / "new.jsonl"
        overflow.write_text(record("new"))
        pergula.parse_transcript(overflow)

        self.assertIn(str(paths[0]), pergula._MESSAGE_CACHE)


class Noise(unittest.TestCase):
    """What the CLI injects and nobody typed."""

    def test_strips_system_reminder(self):
        text = "before<system-reminder>hidden</system-reminder>after"
        self.assertEqual(pergula.strip_noise(text), "beforeafter")

    def test_strips_across_newlines(self):
        text = "a<system-reminder>one\ntwo\nthree</system-reminder>b"
        self.assertEqual(pergula.strip_noise(text), "ab")

    def test_strips_command_wrappers(self):
        text = "<command-name>/clear</command-name>real words"
        self.assertEqual(pergula.strip_noise(text), "real words")

    def test_leaves_ordinary_prose_alone(self):
        self.assertEqual(pergula.strip_noise("  plain text  "), "plain text")

    def test_a_message_that_was_only_noise_disappears(self):
        directory = Path(tempfile.mkdtemp())
        path = directory / "s.jsonl"
        pergula._MESSAGE_CACHE.clear()
        path.write_text(record("<system-reminder>x</system-reminder>") + record("kept"))
        self.assertEqual([m["text"] for m in pergula.parse_transcript(path)], ["kept"])


class StateToken(TempTranscript):
    """The token decides whether a poll costs a full parse or nothing."""

    def test_changes_when_the_file_grows(self):
        self.path.write_text(record("m0"))
        before = pergula.state_token(self.path, 400)

        with self.path.open("a") as handle:
            handle.write(record("m1"))

        self.assertNotEqual(before, pergula.state_token(self.path, 400))

    def test_changes_with_the_limit(self):
        self.path.write_text(record("m0"))
        self.assertNotEqual(
            pergula.state_token(self.path, 400),
            pergula.state_token(self.path, 100),
        )

    def test_is_stable_while_nothing_happens(self):
        self.path.write_text(record("m0"))
        self.assertEqual(
            pergula.state_token(self.path, 400),
            pergula.state_token(self.path, 400),
        )

    def test_does_not_read_the_file(self):
        """It must answer from stat() alone — that is the whole optimisation."""
        self.path.write_text(record("m0"))
        pergula.state_token(self.path, 400)
        self.assertEqual(pergula._MESSAGE_CACHE, {})


class Windowing(TempTranscript):
    """build_state resolves a session through PROJECTS, so point that at a
    temporary tree rather than the real ~/.claude."""

    def setUp(self):
        super().setUp()
        self.original_projects = pergula.PROJECTS
        pergula.PROJECTS = self.dir / "projects"
        self.project = pergula.PROJECTS / "a-project"
        self.project.mkdir(parents=True)
        self.path = self.project / "session.jsonl"

    def tearDown(self):
        pergula.PROJECTS = self.original_projects

    def test_sends_the_tail_and_reports_the_whole(self):
        self.path.write_text("".join(record(f"m{i}") for i in range(50)))
        state = pergula.build_state(None, self.path.stem, 10)

        self.assertEqual(state["total"], 50)
        self.assertEqual(len(state["messages"]), 10)
        self.assertEqual(state["messages"][-1]["text"], "m49")

    def test_short_session_is_sent_whole(self):
        self.path.write_text("".join(record(f"m{i}") for i in range(3)))
        state = pergula.build_state(None, self.path.stem, 400)
        self.assertEqual(len(state["messages"]), 3)

    def test_missing_session_is_empty_not_an_error(self):
        state = pergula.build_state(None, "does-not-exist", 400)
        self.assertEqual(state["messages"], [])
        self.assertIsNone(state["session"])

    def test_the_newest_session_is_picked_when_none_is_named(self):
        older = self.project / "older.jsonl"
        older.write_text(record("old"))
        self.path.write_text(record("new"))

        state = pergula.build_state(None, None, 400)
        self.assertEqual(state["messages"][0]["text"], "new")


class SessionTitle(TempTranscript):
    """Later records win, and a custom title beats a generated one."""

    def test_custom_title_wins_over_ai_title(self):
        self.path.write_text(
            record("hello")
            + json.dumps({"type": "ai-title", "aiTitle": "generated"}) + "\n"
            + json.dumps({"type": "custom-title", "customTitle": "mine"}) + "\n"
        )
        meta = pergula.session_meta(self.path)
        self.assertEqual(meta["title"], "mine")
        self.assertTrue(meta["renamed"])

    def test_ai_title_used_when_there_is_no_custom_one(self):
        self.path.write_text(
            record("hello") + json.dumps({"type": "ai-title", "aiTitle": "generated"}) + "\n"
        )
        meta = pergula.session_meta(self.path)
        self.assertEqual(meta["title"], "generated")
        self.assertFalse(meta["renamed"])

    def test_falls_back_to_the_opening_prompt(self):
        self.path.write_text(record("the first thing said"))
        self.assertEqual(pergula.session_meta(self.path)["title"], "the first thing said")

    def test_last_custom_title_wins(self):
        self.path.write_text(
            record("hello")
            + json.dumps({"type": "custom-title", "customTitle": "first"}) + "\n"
            + json.dumps({"type": "custom-title", "customTitle": "second"}) + "\n"
        )
        self.assertEqual(pergula.session_meta(self.path)["title"], "second")


class Blocks(TempTranscript):
    """Content arrives as a list of typed blocks, not only as a string."""

    def test_tool_use_becomes_its_own_message(self):
        self.path.write_text(json.dumps({
            "type": "assistant", "timestamp": "t",
            "message": {"role": "assistant", "content": [
                {"type": "text", "text": "running it"},
                {"type": "tool_use", "name": "Bash", "input": {"command": "ls"}},
            ]},
        }) + "\n")
        kinds = [m["kind"] for m in pergula.parse_transcript(self.path)]
        self.assertEqual(kinds, ["text", "tool_use"])

    def test_tool_result_text_is_joined(self):
        self.path.write_text(json.dumps({
            "type": "user", "timestamp": "t",
            "message": {"role": "user", "content": [
                {"type": "tool_result", "content": [
                    {"type": "text", "text": "one"},
                    {"type": "text", "text": "two"},
                ]},
            ]},
        }) + "\n")
        messages = pergula.parse_transcript(self.path)
        self.assertEqual(messages[0]["text"], "one\ntwo")

    def test_empty_tool_result_is_dropped(self):
        self.path.write_text(json.dumps({
            "type": "user", "timestamp": "t",
            "message": {"role": "user", "content": [{"type": "tool_result", "content": "   "}]},
        }) + "\n")
        self.assertEqual(pergula.parse_transcript(self.path), [])

    def test_malformed_line_is_skipped_not_fatal(self):
        self.path.write_text(record("good") + "{not json\n" + record("also good"))
        self.assertEqual([m["text"] for m in pergula.parse_transcript(self.path)],
                         ["good", "also good"])


class Translations(unittest.TestCase):
    """A missing key renders as its own name — loud to a reader, silent to a test."""

    def setUp(self):
        source = (Path(__file__).parent / "pergula").read_text()
        block = source[source.index("const STRINGS = {"):source.index("\n};", source.index("const STRINGS = {"))]
        self.pt = self.keys(block[block.index("pt: {"):block.index("en: {")])
        self.en = self.keys(block[block.index("en: {"):])
        self.source = source

    @staticmethod
    def keys(text):
        return set(re.findall(r"(?<![a-zA-Z])([a-zA-Z]+):\s*'", text))

    def test_both_languages_carry_the_same_keys(self):
        self.assertEqual(self.pt, self.en)

    def test_every_key_used_is_defined(self):
        used = set(re.findall(r"(?<![a-zA-Z])t\('([a-zA-Z]+)'", self.source))
        for first, second in re.findall(
            r"(?<![a-zA-Z])t\([^)]*\?\s*'([a-zA-Z]+)'\s*:\s*'([a-zA-Z]+)'", self.source
        ):
            used |= {first, second}
        used |= set(re.findall(r'data-i18n[a-z-]*="([a-zA-Z]+)"', self.source))

        self.assertEqual(used - self.pt, set())

    def test_no_key_is_dead(self):
        used = set(re.findall(r"(?<![a-zA-Z])t\('([a-zA-Z]+)'", self.source))
        for first, second in re.findall(
            r"(?<![a-zA-Z])t\([^)]*\?\s*'([a-zA-Z]+)'\s*:\s*'([a-zA-Z]+)'", self.source
        ):
            used |= {first, second}
        used |= set(re.findall(r'data-i18n[a-z-]*="([a-zA-Z]+)"', self.source))

        self.assertEqual(self.pt - used, set())


class Conventions(unittest.TestCase):
    """The house rules, checked mechanically so they cannot rot."""

    def setUp(self):
        self.source = (Path(__file__).parent / "pergula").read_text()
        self.lines = self.source.splitlines()

    def test_no_else_branches(self):
        offenders = [
            f"{number}: {line.strip()}"
            for number, line in enumerate(self.lines, 1)
            if re.match(r"^\s*(\} )?else\b|^\s*elif\b", line)
        ]
        self.assertEqual(offenders, [])

    def test_no_console_calls(self):
        self.assertNotIn("console.log", self.source)
        self.assertNotIn("console.error", self.source)
        self.assertNotIn("console.warn", self.source)

    def test_no_trailing_whitespace(self):
        offenders = [n for n, line in enumerate(self.lines, 1) if line != line.rstrip()]
        self.assertEqual(offenders, [])

    def test_only_the_pt_table_speaks_portuguese(self):
        """The page is bilingual through STRINGS; everything else — terminal
        output, comments, CSS — ships in English. The CLI messages were the half
        that got left behind once already."""
        opens = next(n for n, l in enumerate(self.lines) if re.match(r"^\s*pt: \{", l))
        closes = next(n for n, l in enumerate(self.lines[opens:], opens) if re.match(r"^\s*en: \{", l))

        stopwords = r"\b(n[ãa]o|para|com|uma|que|est[áa]|s[ãa]o|j[áa]|voc[êe]|rode|basta|sobe|cair|encerrado|interpretador|carregado|falhou|projetos|sess[õo]es|p[áa]gina|arquivo)\b"
        offenders = [
            f"{n}: {line.strip()}"
            for n, line in enumerate(self.lines, 1)
            if not opens + 1 <= n <= closes + 1 and re.search(stopwords, line, re.I)
        ]
        self.assertEqual(offenders, [])


class ShippedMark(unittest.TestCase):
    """brand/pergula-icon.svg against the spec in brand/BRAND.md. The exploration
    linters in brand/marks/ deliberately still fail on rejected marks — those are
    kept as record — so the gate belongs here, on the one that actually ships."""

    def setUp(self):
        self.root = Path(__file__).parent
        self.icon = (self.root / "brand" / "pergula-icon.svg").read_text()

    def numbers(self):
        joined = " ".join(re.findall(r'\sd="([^"]+)"', self.icon))
        return [float(n) for n in re.findall(r"-?\d+(?:\.\d+)?", joined)]

    def test_has_the_declared_viewbox_and_no_size(self):
        self.assertIn('viewBox="0 0 512 512"', self.icon)
        self.assertIsNone(re.search(r"<svg[^>]*\s(width|height)=", self.icon))

    def test_one_group_named_icon(self):
        groups = re.findall(r"<g\b[^>]*>", self.icon)
        self.assertEqual(len(groups), 1)
        self.assertIn('id="icon"', groups[0])

    def test_a_single_flat_colour(self):
        colours = {c.lower() for c in re.findall(r"#[0-9a-fA-F]{3,8}", self.icon)}
        self.assertEqual(colours, {"#c0e021"})

    def test_no_stroke_gradient_or_effect(self):
        for banned in ("stroke", "gradient", "filter", "opacity", "rx=", "ry="):
            self.assertNotIn(banned, self.icon)

    def test_three_members(self):
        self.assertEqual(len(re.findall(r"<path\b", self.icon)), 3)

    def test_every_coordinate_sits_on_the_32_unit_module(self):
        """512 / 16 = 32, so this is what keeps the favicon free of blur."""
        self.assertEqual([n for n in self.numbers() if n % 32], [])

    def test_the_ink_box_is_what_brand_md_documents(self):
        values = self.numbers()
        xs, ys = values[0::2], values[1::2]
        self.assertEqual((min(xs), max(xs)), (32, 480))
        self.assertEqual((min(ys), max(ys)), (32, 448))

    def test_the_page_inlines_the_same_mark(self):
        """The mark appears in the favicon, the header and the served icon. All
        four must come from the one file, or they drift apart unnoticed."""
        source = (self.root / "pergula").read_text()
        canonical = re.findall(r'\sd="([^"]+)"', self.icon)

        favicon = unquote(re.search(r'href="data:image/svg\+xml,([^"]+)"', source).group(1))
        self.assertEqual(re.findall(r'<path d="([^"]+)"', favicon), canonical)

        header = re.search(r'<svg class="brand".*?</svg>', source, re.S).group(0)
        self.assertEqual(re.findall(r'd="([^"]+)"', header), canonical)


class EverySvgParses(unittest.TestCase):
    def test_no_malformed_svg_anywhere(self):
        broken = []
        for path in sorted((Path(__file__).parent / "brand").rglob("*.svg")):
            try:
                ElementTree.parse(path)
            except ElementTree.ParseError as error:
                broken.append(f"{path}: {error}")

        self.assertEqual(broken, [])


class Nicknames(unittest.TestCase):
    def setUp(self):
        self.original = pergula.NAMES_PATH
        pergula.NAMES_PATH = Path(tempfile.mkdtemp()) / "names.json"

    def tearDown(self):
        pergula.NAMES_PATH = self.original

    def test_saving_then_loading_round_trips(self):
        pergula.save_name("slug", "My Project")
        self.assertEqual(pergula.load_names()["slug"], "My Project")

    def test_empty_label_removes_the_entry(self):
        pergula.save_name("slug", "My Project")
        pergula.save_name("slug", "")
        self.assertNotIn("slug", pergula.load_names())

    def test_missing_file_reads_as_empty(self):
        self.assertEqual(pergula.load_names(), {})


class Snippets(unittest.TestCase):
    """The library is a directory of Markdown files, and every claim that makes
    it usable — the title line stays out of the clipboard, a retitle moves the
    file, nothing a page sends escapes the directory — is checked here."""

    def setUp(self):
        self.original = pergula.SNIPPETS_PATH
        pergula.SNIPPETS_PATH = Path(tempfile.mkdtemp()) / "snippets"

    def tearDown(self):
        pergula.SNIPPETS_PATH = self.original

    def test_saving_then_loading_round_trips(self):
        pergula.save_snippet("commit-msg", "Commit message", "Write the message.")
        found = pergula.load_snippets()

        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["slug"], "commit-msg")
        self.assertEqual(found[0]["title"], "Commit message")
        self.assertEqual(found[0]["body"], "Write the message.\n")

    def test_the_title_line_stays_out_of_the_clipboard(self):
        pergula.save_snippet("x", "Title", "the prompt")
        text = (pergula.SNIPPETS_PATH / "x.md").read_text()

        self.assertTrue(text.startswith("# Title"))
        self.assertNotIn("# Title", pergula.load_snippets()[0]["body"])

    def test_a_file_written_by_hand_needs_no_heading(self):
        pergula.SNIPPETS_PATH.mkdir(parents=True)
        (pergula.SNIPPETS_PATH / "by-hand.md").write_text("just a prompt\n")
        found = pergula.load_snippets()

        self.assertEqual(found[0]["title"], "by hand")
        self.assertEqual(found[0]["body"], "just a prompt\n")

    def test_a_folder_becomes_the_group(self):
        pergula.save_snippet("review/pr", "PR review", "look at the diff")
        found = pergula.load_snippets()

        self.assertEqual(found[0]["group"], "review")
        self.assertEqual(found[0]["slug"], "review/pr")

    def test_deleting_takes_the_empty_folder_with_it(self):
        pergula.save_snippet("review/pr", "PR review", "look at the diff")
        pergula.drop_snippet("review/pr")

        self.assertEqual(pergula.load_snippets(), [])
        self.assertFalse((pergula.SNIPPETS_PATH / "review").exists())

    def test_a_shared_folder_survives_one_deletion(self):
        pergula.save_snippet("review/pr", "PR review", "one")
        pergula.save_snippet("review/security", "Security", "two")
        pergula.drop_snippet("review/pr")

        self.assertTrue((pergula.SNIPPETS_PATH / "review").is_dir())
        self.assertEqual(len(pergula.load_snippets()), 1)

    def test_the_slug_loses_accents_and_punctuation(self):
        self.assertEqual(pergula.snippet_slug("Revisão de PR!"), "revisao-de-pr")
        self.assertEqual(pergula.snippet_slug("review/PR review"), "review/pr-review")

    def test_the_slug_cannot_walk_out_of_the_directory(self):
        self.assertEqual(pergula.snippet_slug("../../etc/passwd"), "etc/passwd")
        self.assertEqual(pergula.snippet_slug("/etc/passwd"), "etc/passwd")
        self.assertEqual(pergula.snippet_slug("a/b/c/d"), "a/b")
        self.assertEqual(pergula.snippet_slug("..."), "")

    def test_the_token_moves_only_when_the_library_does(self):
        pergula.save_snippet("one", "One", "a")
        before = pergula.snippets_token(pergula.snippet_files())

        self.assertEqual(before, pergula.snippets_token(pergula.snippet_files()))

        pergula.save_snippet("two", "Two", "b")
        self.assertNotEqual(before, pergula.snippets_token(pergula.snippet_files()))

    def test_a_missing_directory_reads_as_empty(self):
        self.assertEqual(pergula.load_snippets(), [])
        self.assertEqual(pergula.snippet_files(), [])


class Favourites(unittest.TestCase):
    """Five snippets sit in the sidebar. The cap, the ordering and the two ways
    a star can be orphaned — a retitle and a delete — are the whole of it."""

    def setUp(self):
        self.home = Path(tempfile.mkdtemp())
        self.snippets = pergula.SNIPPETS_PATH
        self.stars = pergula.FAVOURITES_PATH
        pergula.SNIPPETS_PATH = self.home / "snippets"
        pergula.FAVOURITES_PATH = self.home / "favourites.json"

    def tearDown(self):
        pergula.SNIPPETS_PATH = self.snippets
        pergula.FAVOURITES_PATH = self.stars

    def test_starring_then_reading_round_trips(self):
        pergula.set_favourite("one", True)

        self.assertEqual(pergula.load_favourites(), ["one"])

    def test_starring_twice_does_not_duplicate(self):
        pergula.set_favourite("one", True)
        pergula.set_favourite("one", True)

        self.assertEqual(pergula.load_favourites(), ["one"])

    def test_unstarring_removes_it(self):
        pergula.set_favourite("one", True)
        pergula.set_favourite("one", False)

        self.assertEqual(pergula.load_favourites(), [])

    def test_a_new_star_joins_the_end(self):
        for slug in ("one", "two", "three"):
            pergula.set_favourite(slug, True)

        self.assertEqual(pergula.load_favourites(), ["one", "two", "three"])

    def test_the_sixth_is_refused_and_the_five_hold(self):
        for slug in ("a", "b", "c", "d", "e"):
            pergula.set_favourite(slug, True)

        pergula.set_favourite("f", True)

        self.assertEqual(pergula.load_favourites(), ["a", "b", "c", "d", "e"])

    def test_room_reopens_when_one_is_dropped(self):
        for slug in ("a", "b", "c", "d", "e"):
            pergula.set_favourite(slug, True)

        pergula.set_favourite("c", False)
        pergula.set_favourite("f", True)

        self.assertEqual(pergula.load_favourites(), ["a", "b", "d", "e", "f"])

    def test_a_retitle_carries_the_star_across(self):
        pergula.set_favourite("old", True)
        pergula.move_favourite("old", "new")

        self.assertEqual(pergula.load_favourites(), ["new"])

    def test_moving_a_snippet_nobody_starred_changes_nothing(self):
        pergula.set_favourite("one", True)
        pergula.move_favourite("other", "renamed")

        self.assertEqual(pergula.load_favourites(), ["one"])

    def test_a_hand_written_file_is_capped_on_read(self):
        pergula.FAVOURITES_PATH.write_text(json.dumps(list("abcdefgh")))

        self.assertEqual(len(pergula.load_favourites()), pergula.FAVOURITE_LIMIT)

    def test_a_missing_or_broken_file_reads_as_empty(self):
        self.assertEqual(pergula.load_favourites(), [])

        pergula.FAVOURITES_PATH.write_text("{}")
        self.assertEqual(pergula.load_favourites(), [])

    def test_the_token_moves_when_only_a_star_moves(self):
        pergula.save_snippet("one", "One", "a")
        before = pergula.snippets_token(pergula.snippet_files())

        pergula.set_favourite("one", True)

        self.assertNotEqual(before, pergula.snippets_token(pergula.snippet_files()))


if __name__ == "__main__":
    unittest.main(verbosity=2)
