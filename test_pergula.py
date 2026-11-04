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
import os
import re
import tempfile
import threading
import time
import unittest
import unittest.mock
import xml.etree.ElementTree as ElementTree
from datetime import datetime, timedelta, timezone
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


class TempProject(TempTranscript):
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


class Windowing(TempProject):
    """A long session reaches the page as its tail, and says how long it is."""

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


class Resume(TempProject):
    """The prompt that restarts a session is built from these turns. Too much in
    them and the new session costs what the old one would have; a command's
    output slipping through is how that happens."""

    def test_keeps_only_what_was_said(self):
        self.path.write_text(record("ask") + json.dumps({
            "type": "assistant",
            "message": {"role": "assistant", "content": [
                {"type": "tool_use", "name": "Bash", "input": {"command": "ls"}},
                {"type": "text", "text": "answer"},
            ]},
        }) + "\n")
        turns = pergula.resume_turns(pergula.parse_transcript(self.path))

        self.assertEqual(turns, [
            {"role": "user", "text": "ask"},
            {"role": "assistant", "text": "answer"},
        ])

    def test_only_the_last_turns_in_the_order_they_happened(self):
        self.path.write_text("".join(
            record(f"m{i}", role="user" if i % 2 == 0 else "assistant") for i in range(20)
        ))
        turns = pergula.resume_turns(pergula.parse_transcript(self.path))

        self.assertEqual(len(turns), pergula.RESUME_TURNS)
        self.assertEqual(turns[-1]["text"], "m19")
        self.assertEqual(turns[0]["text"], f"m{20 - pergula.RESUME_TURNS}")

    def test_narration_between_commands_does_not_push_the_request_out(self):
        narration = "".join(record(f"step {i}", role="assistant") for i in range(10))
        self.path.write_text(record("the request") + narration)
        turns = pergula.resume_turns(pergula.parse_transcript(self.path))

        self.assertEqual(turns, [
            {"role": "user", "text": "the request"},
            {"role": "assistant", "text": "step 9"},
        ])

    def test_two_messages_in_a_row_from_the_user_are_both_kept(self):
        self.path.write_text(record("first") + record("second"))
        turns = pergula.resume_turns(pergula.parse_transcript(self.path))

        self.assertEqual(turns, [{"role": "user", "text": "first\n\nsecond"}])

    def test_what_the_cli_injected_is_not_something_the_user_said(self):
        self.path.write_text(record("typed") + record("# A skill body", isMeta=True))
        turns = pergula.resume_turns(pergula.parse_transcript(self.path))

        self.assertEqual(turns, [{"role": "user", "text": "typed"}])

    def test_a_session_of_commands_alone_has_no_turns(self):
        self.path.write_text(json.dumps({
            "type": "assistant",
            "message": {"role": "assistant", "content": [
                {"type": "tool_use", "name": "Bash", "input": {"command": "ls"}},
            ]},
        }) + "\n")
        state = pergula.build_state(None, self.path.stem, 400)

        self.assertEqual(state["resume"]["turns"], [])

    def test_a_long_message_keeps_its_head_and_its_tail(self):
        clipped = pergula.clip_middle("start " + "x" * 5000 + " finish")

        self.assertTrue(clipped.startswith("start "))
        self.assertTrue(clipped.endswith(" finish"))
        self.assertLess(len(clipped), pergula.RESUME_CLIP + 10)

    def test_a_short_message_is_left_alone(self):
        self.assertEqual(pergula.clip_middle("short"), "short")

    def test_the_state_says_where_the_transcript_is(self):
        self.path.write_text(record("hello"))
        state = pergula.build_state(None, self.path.stem, 400)

        self.assertEqual(state["resume"]["path"], str(self.path))
        self.assertEqual(state["resume"]["turns"][0]["text"], "hello")

    def test_the_whole_session_is_searched_not_the_window(self):
        self.path.write_text(record("said") + "".join(
            json.dumps({"type": "assistant", "message": {"role": "assistant", "content": [
                {"type": "tool_use", "name": "Bash", "input": {"command": f"c{i}"}},
            ]}}) + "\n"
            for i in range(30)
        ))
        state = pergula.build_state(None, self.path.stem, 5)

        self.assertEqual(state["resume"]["turns"][0]["text"], "said")


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


class TabTitle(TempTranscript):
    """The terminal tab names a live session after its project; the sidebar
    shows the name without the project, since the group already says it."""

    def index(self, tab):
        running = {"pid": 1, "status": "idle", "state": "ready", "subagents": 0, "tab": tab}
        live = {self.path.stem: running}
        transcripts = unittest.mock.patch.object(pergula, "all_transcripts", return_value=[self.path])
        sessions = unittest.mock.patch.object(pergula, "live_sessions", return_value=live)
        with transcripts, sessions:
            return pergula.build_index(None)["projects"][0]["sessions"][0]

    def test_the_tab_name_beats_a_generated_title(self):
        self.path.write_text(record("hello") + json.dumps({"type": "ai-title", "aiTitle": "generated"}) + "\n")
        meta = self.index("3101 claude")

        self.assertEqual(meta["title"], "3101 claude")
        self.assertTrue(meta["renamed"])

    def test_a_rename_in_the_transcript_still_wins(self):
        self.path.write_text(record("hello") + json.dumps({"type": "custom-title", "customTitle": "mine"}) + "\n")

        self.assertEqual(self.index("3101 claude")["title"], "mine")

    def test_without_a_tab_name_nothing_changes(self):
        self.path.write_text(record("hello") + json.dumps({"type": "ai-title", "aiTitle": "generated"}) + "\n")
        meta = self.index("")

        self.assertEqual(meta["title"], "generated")
        self.assertFalse(meta["renamed"])

    def test_the_tab_is_read_from_the_hooks_record(self):
        self.assertEqual(pergula.tab_title({"tab": "  3101   claude "}), "3101 claude")
        self.assertEqual(pergula.tab_title({"tab": 3101}), "")
        self.assertEqual(pergula.tab_title({}), "")

    def test_a_new_tab_name_changes_the_index_token(self):
        before = {"abc-1": {"status": "idle", "state": "ready", "tab": "3101 claude"}}
        after = {"abc-1": {"status": "idle", "state": "ready", "tab": "3185 claude"}}

        self.assertNotEqual(pergula.live_stamp(before), pergula.live_stamp(after))


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


def compact(body):
    """A line as the CLI really writes it: no space after the separators."""
    return json.dumps(body, separators=(",", ":")) + "\n"


class Shortcuts(TempTranscript):
    """What the parser skips to stay fast. A mistake here deletes turns silently."""

    def test_a_record_typed_up_front_and_not_shown_is_skipped(self):
        self.path.write_text(
            compact({"type": "api-request", "params": {"messages": [{"role": "user", "content": "no"}]}})
            + compact({"type": "user", "message": {"role": "user", "content": "typed first"}})
            + compact({"parentUuid": "x", "type": "assistant",
                       "message": {"role": "assistant", "content": "typed later"}})
        )
        self.assertEqual(self.texts(), ["typed first", "typed later"])

    def test_screenshots_are_emptied_and_the_turn_survives(self):
        blob = "A" * pergula.BLOB_MIN
        self.path.write_text(compact({
            "parentUuid": "x", "type": "user",
            "message": {"role": "user", "content": [
                {"type": "tool_result", "content": [
                    {"type": "text", "text": "shot taken"},
                    {"type": "image", "source": {"type": "base64", "data": blob}},
                ]},
            ]},
            "toolUseResult": {"file": {"base64": blob}},
        }))
        self.assertEqual(self.texts(), ["shot taken"])

    def test_two_requests_for_one_cold_file_parse_it_once(self):
        self.path.write_text(record("once"))
        original = pergula.parse_lines
        calls = []

        def slow(lines, messages):
            calls.append(1)
            time.sleep(0.2)
            original(lines, messages)

        threads = [threading.Thread(target=pergula.parse_transcript, args=(self.path,)) for _ in range(3)]
        with unittest.mock.patch.object(pergula, "parse_lines", slow):
            for thread in threads:
                thread.start()

            for thread in threads:
                thread.join()

        self.assertEqual(len(calls), 1)

    def test_cut_leaves_valid_json(self):
        line = compact({"data": "A" * pergula.BLOB_MIN, "base64": "B" * 999, "keep": "C" * 999})
        self.assertEqual(json.loads(pergula.drop_blobs(line.encode())),
                         {"data": "", "base64": "", "keep": "C" * 999})

    def test_short_values_and_quoted_keys_inside_text_are_kept(self):
        quoted = '"data":"' + "A" * pergula.BLOB_MIN + '"'
        line = compact({"data": "short", "text": quoted})
        self.assertEqual(json.loads(pergula.drop_blobs(line.encode())),
                         {"data": "short", "text": quoted})


class AgentState(unittest.TestCase):
    """The four states come from a file another program writes. When it is
    missing, stale or wrong the row must still say something true."""

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        patcher = unittest.mock.patch.object(pergula, "AGENT_STATE_PATH", Path(self.directory.name))
        patcher.start()
        self.addCleanup(patcher.stop)

    def write(self, session, state):
        (Path(self.directory.name) / f"{session}.json").write_text(json.dumps({"state": state}))

    def test_without_a_file_the_registry_answers(self):
        self.assertEqual(pergula.agent_state("abc-1", "busy"), "working")
        self.assertEqual(pergula.agent_state("abc-1", "idle"), "ready")

    def test_the_file_says_what_the_registry_cannot(self):
        self.write("abc-1", "needs_you")

        self.assertEqual(pergula.agent_state("abc-1", "busy"), "needs_you")

    def test_an_error_is_kept(self):
        self.write("abc-1", "error")

        self.assertEqual(pergula.agent_state("abc-1", "idle"), "error")

    def test_a_turn_waiting_on_a_shell_is_not_ready(self):
        self.write("abc-1", "waiting")

        self.assertEqual(pergula.agent_state("abc-1", "idle"), "waiting")

    def test_the_shell_finishing_wakes_it_to_working(self):
        self.write("abc-1", "waiting")

        self.assertEqual(pergula.agent_state("abc-1", "busy"), "working")

    def test_an_interrupted_turn_is_ready_not_working(self):
        self.write("abc-1", "working")

        self.assertEqual(pergula.agent_state("abc-1", "idle"), "ready")

    def write_behind(self, session, count, turn_over=True):
        record = {"state": "working", "subagents": count, "turn_over": turn_over}
        (Path(self.directory.name) / f"{session}.json").write_text(json.dumps(record))

    def test_subagents_behind_a_finished_turn_keep_it_working(self):
        self.write_behind("abc-1", 2)

        self.assertEqual(pergula.agent_state("abc-1", "idle"), "working")
        self.assertEqual(pergula.subagents_behind(pergula.agent_record("abc-1")), 2)

    def test_a_count_left_from_a_turn_still_running_is_not_trusted(self):
        self.write_behind("abc-1", 2, turn_over=False)

        self.assertEqual(pergula.agent_state("abc-1", "idle"), "ready")
        self.assertEqual(pergula.subagents_behind(pergula.agent_record("abc-1")), 0)

    def test_a_count_that_is_not_a_number_is_none(self):
        self.write_behind("abc-1", "2")

        self.assertEqual(pergula.subagents_behind(pergula.agent_record("abc-1")), 0)

    def test_a_change_in_the_count_changes_the_index_token(self):
        two = {"abc-1": {"status": "idle", "state": "working", "subagents": 2}}
        one = {"abc-1": {"status": "idle", "state": "working", "subagents": 1}}

        self.assertNotEqual(pergula.live_stamp(two), pergula.live_stamp(one))

    def test_an_unknown_state_falls_back(self):
        self.write("abc-1", "dancing")

        self.assertEqual(pergula.agent_state("abc-1", "busy"), "working")

    def test_a_file_that_is_not_an_object_falls_back(self):
        (Path(self.directory.name) / "abc-1.json").write_text("[1, 2]")

        self.assertEqual(pergula.agent_state("abc-1", "idle"), "ready")

    def test_an_id_cannot_reach_outside_the_directory(self):
        outside = Path(self.directory.name).parent / "outside.json"
        outside.write_text(json.dumps({"state": "needs_you"}))
        self.addCleanup(outside.unlink)

        self.assertEqual(pergula.agent_state("../outside", "idle"), "ready")

    def test_a_change_of_state_changes_the_index_token(self):
        quiet = {"abc-1": {"status": "busy", "state": "working"}}
        waiting = {"abc-1": {"status": "busy", "state": "needs_you"}}

        self.assertNotEqual(pergula.live_stamp(quiet), pergula.live_stamp(waiting))


def reply(key, stamp, model="claude-opus-5-5", tokens=(10, 1000, 100, 50), version="2.1.5",
          cwd="/nowhere"):
    """One assistant line with usage, in the shape the CLI writes. The CLI
    repeats a response over several lines, so callers write it more than once."""
    given, read, written, out = tokens
    body = {
        "type": "assistant", "timestamp": stamp, "version": version, "cwd": cwd,
        "message": {"id": key, "model": model, "role": "assistant", "content": [],
                    "usage": {"input_tokens": given, "cache_read_input_tokens": read,
                              "cache_creation_input_tokens": written, "output_tokens": out}},
    }
    return json.dumps(body) + "\n"


class TempUsage(unittest.TestCase):
    """A private ~/.claude: transcripts, summary and clock."""

    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.saved = (pergula.PROJECTS, pergula.USAGE_PATH, os.environ.get("TZ"))
        pergula.PROJECTS = self.dir / "projects"
        pergula.USAGE_PATH = self.dir / "usage.json"
        pergula._USAGE.update(state=None, done=0, total=0, ready=False)
        pergula._ROOTS.clear()
        pergula._META_CACHE.clear()
        os.environ["TZ"] = "America/Sao_Paulo"
        time.tzset()
        self.folder = pergula.PROJECTS / "-work-app"
        self.folder.mkdir(parents=True)

    def tearDown(self):
        pergula.PROJECTS, pergula.USAGE_PATH, zone = self.saved
        pergula._USAGE.update(state=None, done=0, total=0, ready=False)
        if zone is None:
            os.environ.pop("TZ", None)
        if zone is not None:
            os.environ["TZ"] = zone
        time.tzset()

    def write(self, name, *lines, folder=None):
        path = (folder or self.folder) / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a") as handle:
            handle.write("".join(lines))
        return path

    def state(self):
        pergula.index_usage()
        return pergula._USAGE["state"]

    def leaves(self):
        return list(pergula.walk_leaves(self.state(), "", "~"))

    def total(self, field="calls"):
        return sum(leaf[field] for *_rest, leaf in self.leaves())


class UsageCounting(TempUsage):
    """Every failure here inflates or deflates the panel without a sound."""

    def test_a_response_written_over_three_lines_counts_once(self):
        self.write("s.jsonl", *[reply("msg_1", "2026-11-02T12:00:00.000Z")] * 3)

        self.assertEqual(self.total(), 1)
        self.assertEqual(self.total("cache_read"), 1000)

    def test_two_responses_count_twice(self):
        self.write("s.jsonl", reply("msg_1", "2026-11-02T12:00:00.000Z"),
                   reply("msg_2", "2026-11-02T12:01:00.000Z"))

        self.assertEqual(self.total(), 2)

    def test_appending_adds_only_what_is_new(self):
        self.write("s.jsonl", reply("msg_1", "2026-11-02T12:00:00.000Z"))
        self.assertEqual(self.total(), 1)

        self.write("s.jsonl", reply("msg_2", "2026-11-02T12:05:00.000Z"))
        self.assertEqual(self.total(), 2)

    def test_a_response_cut_in_two_by_a_read_is_not_counted_again(self):
        self.write("s.jsonl", reply("msg_1", "2026-11-02T12:00:00.000Z"))
        self.state()

        self.write("s.jsonl", reply("msg_1", "2026-11-02T12:00:00.000Z"),
                   reply("msg_2", "2026-11-02T12:05:00.000Z"))
        self.assertEqual(self.total(), 2)

    def test_the_ids_survive_a_restart(self):
        self.write("s.jsonl", reply("msg_1", "2026-11-02T12:00:00.000Z"))
        self.state()
        pergula._USAGE["state"] = None

        self.write("s.jsonl", reply("msg_1", "2026-11-02T12:00:00.000Z"))
        self.assertEqual(self.total(), 1)

    def test_half_a_line_waits_for_the_rest(self):
        line = reply("msg_1", "2026-11-02T12:00:00.000Z")
        self.write("s.jsonl", line[:40])
        self.assertEqual(self.total(), 0)

        self.write("s.jsonl", line[40:])
        self.assertEqual(self.total(), 1)

    def test_an_unchanged_pass_changes_nothing(self):
        self.write("s.jsonl", reply("msg_1", "2026-11-02T12:00:00.000Z"))
        self.state()
        self.state()

        self.assertEqual(self.total(), 1)

    def test_a_subagent_counts_in_the_session_that_started_it(self):
        self.write("s.jsonl", reply("msg_1", "2026-11-02T12:00:00.000Z"))
        self.write("s/subagents/agent-a.jsonl", reply("msg_9", "2026-11-02T12:02:00.000Z"))

        kinds = {(session, kind) for _h, _p, session, _m, kind, _l in self.leaves()}
        self.assertEqual(kinds, {("s", "main"), ("s", "sub")})

    def test_the_first_call_is_the_base(self):
        self.write("s.jsonl", reply("msg_1", "2026-11-02T12:00:00.000Z", tokens=(1, 50000, 0, 9)),
                   reply("msg_2", "2026-11-02T12:01:00.000Z", tokens=(1, 90000, 0, 9)))

        leaf = self.leaves()[0][-1]
        self.assertEqual((leaf["starts"], leaf["first_ctx"]), (1, 50001))

    def test_a_long_call_is_counted_as_one(self):
        self.write("s.jsonl", reply("msg_1", "2026-11-02T12:00:00.000Z", tokens=(1, 250000, 0, 9)),
                   reply("msg_2", "2026-11-02T12:01:00.000Z", tokens=(1, 9000, 0, 9)))

        self.assertEqual(self.total("ctx_over_200k"), 1)

    def test_a_synthetic_reply_costs_nothing_and_is_not_a_call(self):
        self.write("s.jsonl", reply("msg_1", "2026-11-02T12:00:00.000Z", model="<synthetic>"))

        self.assertEqual(self.total(), 0)

    def test_the_dollars_follow_the_table(self):
        leaf = {"input": 1_000_000, "cache_read": 0, "cache_write": 0, "output": 1_000_000}

        self.assertAlmostEqual(pergula.leaf_cost("claude-opus-5-5", leaf), 24.0)
        self.assertIsNone(pergula.leaf_cost("claude-unknown-9", leaf))


class UsageCopies(TempUsage):
    """The CLI copies history between files; a copy is not another response."""

    def calls_by_session(self):
        found = {}
        for _hour, _project, session, _model, kind, leaf in self.leaves():
            found[(session, kind)] = found.get((session, kind), 0) + leaf["calls"]
        return found

    def test_a_fork_does_not_count_its_parents_history_again(self):
        self.write("s.jsonl", reply("msg_1", "2026-11-02T12:00:00.000Z"))
        self.write("s/subagents/agent-a.jsonl", reply("msg_1", "2026-11-02T12:00:00.000Z"),
                   reply("msg_9", "2026-11-02T12:02:00.000Z"))

        self.assertEqual(self.calls_by_session(), {("s", "main"): 1, ("s", "sub"): 1})

    def test_a_copy_written_after_the_original_was_counted_is_skipped(self):
        self.write("s.jsonl", reply("msg_1", "2026-11-02T12:00:00.000Z"))
        self.state()

        self.write("s/subagents/agent-a.jsonl", reply("msg_1", "2026-11-02T12:00:00.000Z"))
        self.assertEqual(self.total(), 1)

    def test_a_continued_session_leaves_the_copied_history_where_it_was_made(self):
        # Named so that the alphabet puts the newer file first.
        old = self.write("b-old.jsonl", reply("msg_1", "2026-11-02T12:00:00.000Z"))
        os.utime(old, (1_700_000_000, 1_700_000_000))
        self.write("a-new.jsonl", reply("msg_1", "2026-11-02T12:00:00.000Z"),
                   reply("msg_2", "2026-11-02T13:00:00.000Z"))

        self.assertEqual(self.calls_by_session(), {("b-old", "main"): 1, ("a-new", "main"): 1})

    def test_the_output_is_what_the_last_line_reports(self):
        self.write("s.jsonl", reply("msg_1", "2026-11-02T12:00:00.000Z", tokens=(10, 1000, 100, 10)),
                   reply("msg_1", "2026-11-02T12:00:00.000Z", tokens=(10, 1000, 100, 257)))

        self.assertEqual((self.total(), self.total("output")), (1, 257))

    def test_the_rest_of_the_output_arrives_in_the_next_read(self):
        self.write("s.jsonl", reply("msg_1", "2026-11-02T12:00:00.000Z", tokens=(10, 1000, 100, 10)))
        self.state()

        self.write("s.jsonl", reply("msg_1", "2026-11-02T12:00:00.000Z", tokens=(10, 1000, 100, 257)))
        self.assertEqual((self.total(), self.total("output"), self.total("cache_read")), (1, 257, 1000))

    def test_a_day_no_transcript_holds_is_forgotten(self):
        old = self.write("s.jsonl", reply("msg_1", "2020-01-01T12:00:00.000Z"))
        today = datetime.now().strftime("%Y-%m-%d")
        self.write("t.jsonl", reply("msg_3", today + "T12:00:00.000Z"))
        self.assertIn("2020-01-01", self.state()["seen"])

        old.unlink()
        seen = self.state()["seen"]
        self.assertNotIn("2020-01-01", seen)
        self.assertIn("msg_3", seen[today])

    def test_a_fork_of_a_long_session_does_not_count_its_old_history(self):
        # The CLI deletes by when a file was last written, so a living session
        # can hold responses older than any cleanup.
        long_ago = (datetime.now(timezone.utc) - timedelta(days=40)).strftime("%Y-%m-%dT12:00:00.000Z")
        recent = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%dT12:00:00.000Z")
        history = (reply("msg_1", long_ago), reply("msg_2", recent))
        self.write("s.jsonl", *history)
        self.state()

        self.write("s/subagents/agent-a.jsonl", *history, reply("msg_3", recent))
        self.assertEqual(self.total(), 3)

    def test_a_response_that_crosses_midnight_counts_once(self):
        # 02:59:52 and 03:00:10 UTC are either side of midnight in São Paulo.
        self.write("s.jsonl", reply("msg_1", "2026-11-02T02:59:52.000Z", tokens=(10, 1000, 100, 10)),
                   reply("msg_1", "2026-11-02T03:00:10.000Z", tokens=(10, 1000, 100, 257)))

        sums = [(hour, leaf["calls"], leaf["output"]) for hour, *_rest, leaf in self.leaves()]
        self.assertEqual(sums, [("2026-11-01T23", 1, 257)])

    def test_the_rest_of_the_output_stays_in_the_hour_of_the_call(self):
        self.write("s.jsonl", reply("msg_1", "2026-11-02T12:59:50.000Z", tokens=(10, 1000, 100, 10)),
                   reply("msg_1", "2026-11-02T13:00:10.000Z", tokens=(10, 1000, 100, 257)))

        sums = [(hour, leaf["calls"], leaf["output"]) for hour, *_rest, leaf in self.leaves()]
        self.assertEqual(sums, [("2026-11-02T09", 1, 257)])

    def test_a_continued_session_has_no_base_of_its_own(self):
        old = self.write("b-old.jsonl", reply("msg_1", "2026-11-02T12:00:00.000Z"))
        os.utime(old, (1_700_000_000, 1_700_000_000))
        self.write("a-new.jsonl", reply("msg_1", "2026-11-02T12:00:00.000Z"),
                   reply("msg_2", "2026-11-02T13:00:00.000Z", tokens=(10, 150000, 100, 50)))

        self.assertEqual((self.total("starts"), self.total("first_ctx")), (1, 1110))


class UsageClock(TempUsage):
    """A day is a local day, and the week turns when the quota does."""

    def test_the_day_is_cut_in_local_time(self):
        self.write("s.jsonl", reply("msg_1", "2026-11-02T01:30:00.000Z"))

        self.assertEqual(self.leaves()[0][0], "2026-11-01T22")

    def test_the_week_starts_on_saturday_at_two(self):
        reset = pergula.QUOTA_RESET
        before = pergula.quota_week_start(datetime(2026, 10, 31, 13, 59), reset)
        after = pergula.quota_week_start(datetime(2026, 10, 31, 14, 0), reset)

        self.assertEqual(before, datetime(2026, 10, 24, 14))
        self.assertEqual(after, datetime(2026, 10, 31, 14))

    def test_another_setting_moves_the_cut(self):
        reset = {"weekday": "mon", "hour": 9}

        self.assertEqual(pergula.quota_week_start(datetime(2026, 10, 31, 15), reset),
                         datetime(2026, 10, 26, 9))

    def test_calls_either_side_of_the_turn_land_in_different_weeks(self):
        # 16:30 and 17:30 UTC are 13:30 and 14:30 in São Paulo, on a Saturday.
        self.write("s.jsonl", reply("msg_1", "2026-10-31T16:30:00.000Z"),
                   reply("msg_2", "2026-10-31T17:30:00.000Z"))
        state = self.state()

        late = pergula.usage_report(state, "week", "2026-10-31T15", set())
        early = pergula.usage_report(state, "week", "2026-10-31T13", set())
        self.assertEqual((late["totals"]["calls"], early["totals"]["calls"]), (1, 1))
        self.assertEqual(late["start"], "2026-10-31T14")

    def test_the_setting_is_saved_and_moves_the_report(self):
        self.write("s.jsonl", reply("msg_1", "2026-10-31T16:30:00.000Z"),
                   reply("msg_2", "2026-10-31T17:30:00.000Z"))
        self.state()
        pergula.set_quota_reset("sat", 12)

        report = pergula.usage_report(pergula._USAGE["state"], "week", "2026-10-31T15", set())
        self.assertEqual(report["totals"]["calls"], 2)
        self.assertEqual(pergula.load_usage()["settings"]["quota_reset"], {"weekday": "sat", "hour": 12})

    def test_true_is_not_an_hour(self):
        state = {"settings": {"quota_reset": {"weekday": "sat", "hour": True}}}

        self.assertEqual(pergula.quota_reset(state), pergula.QUOTA_RESET)
        self.assertFalse(pergula.valid_quota_reset("sat", True))
        self.assertFalse(pergula.valid_quota_reset("sat", "14"))
        self.assertFalse(pergula.valid_quota_reset("sat", 24))

    def test_the_bars_of_a_month_are_its_days(self):
        window = pergula.usage_window("month", "2026-11-15T10", "", pergula.QUOTA_RESET)

        self.assertEqual(len(window["bars"]), 30)
        self.assertEqual((window["start"], window["end"]), ("2026-11-01T00", "2026-12-01T00"))


class UsageProjects(TempUsage):
    """Projects are repositories, and a worktree is its repository's."""

    def git(self, *arguments, where):
        import subprocess
        subprocess.run(["git", "-C", str(where), *arguments], check=True, capture_output=True)

    def test_a_worktree_is_summed_in_the_main_repository(self):
        main = (self.dir / "repo").resolve()
        main.mkdir()
        self.git("init", "-q", where=main)
        self.git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty",
                 "-m", "first", where=main)
        tree = (self.dir / "tree").resolve()
        self.git("worktree", "add", "-q", str(tree), where=main)

        for path, key in ((main, "msg_1"), (tree, "msg_2")):
            folder = pergula.PROJECTS / pergula.project_slug(path)
            self.write("s.jsonl", reply(key, "2026-11-02T12:00:00.000Z", cwd=str(path)), folder=folder)

        projects = {project for _h, project, *_rest in self.leaves()}
        self.assertEqual(projects, {str(main)})

    def test_a_transcript_that_opens_without_a_directory_finds_it_later(self):
        repo = (self.dir / "my.repo").resolve()
        repo.mkdir()
        folder = pergula.PROJECTS / pergula.project_slug(repo)
        self.write("s.jsonl", json.dumps({"type": "mode", "mode": "default"}) + "\n", folder=folder)
        self.state()

        self.write("s.jsonl", reply("msg_1", "2026-11-02T12:00:00.000Z", cwd=str(repo)), folder=folder)
        projects = {project for _h, project, *_rest in self.leaves()}
        self.assertEqual(projects, {str(repo)})

    def test_a_folder_whose_directory_is_gone_keeps_its_last_answer(self):
        folders = {"-gone": "/somewhere/repo"}

        self.assertEqual(pergula.project_of("-gone", ("/does/not/exist", True), folders), "/somewhere/repo")

    def test_a_folder_never_answered_falls_back_to_its_name(self):
        self.assertEqual(pergula.project_of("-does-not-exist", ("", False), {}), "/does/not/exist")


class UsageMilestones(unittest.TestCase):
    def state(self, days):
        state = pergula.fresh_usage()
        for day, model, version in days:
            call = {"hour": f"{day}T10", "model": model, "version": version, "input": 1,
                    "cache_read": 0, "cache_write": 0, "cache_write_1h": 0, "output": 1}
            pergula.add_call(state, "/p", "s", "main", call, False)
        return state

    def test_a_new_leading_model_is_marked(self):
        found = pergula.detect_milestones(self.state([
            ("2026-10-20", "claude-sonnet-5-5", "2.1"),
            ("2026-10-21", "claude-opus-5-5", "2.1"),
        ]))

        self.assertEqual(found, [{"day": "2026-10-21", "kind": "model", "label": "opus 5.5"}])

    def test_a_patch_release_is_not_marked(self):
        found = pergula.detect_milestones(self.state([
            ("2026-10-20", "claude-opus-5-5", pergula.minor_version("2.1.290")),
            ("2026-10-21", "claude-opus-5-5", pergula.minor_version("2.1.296")),
        ]))

        self.assertEqual(found, [])

    def test_a_minor_release_is_marked(self):
        found = pergula.detect_milestones(self.state([
            ("2026-10-20", "claude-opus-5-5", "2.1"),
            ("2026-10-21", "claude-opus-5-5", "2.2"),
        ]))

        self.assertEqual(found, [{"day": "2026-10-21", "kind": "version", "label": "claude code 2.2"}])


class UsageSummary(TempUsage):
    """The summary outlives the transcripts, so losing it costs months."""

    def test_the_summary_is_written_whole(self):
        self.write("s.jsonl", reply("msg_1", "2026-11-02T12:00:00.000Z"))
        self.state()

        saved = json.loads(pergula.USAGE_PATH.read_text())
        self.assertEqual(saved["version"], pergula.USAGE_VERSION)
        self.assertFalse(pergula.USAGE_PATH.with_name("usage.json.tmp").exists())

    def test_history_outlives_a_deleted_transcript(self):
        path = self.write("s.jsonl", reply("msg_1", "2026-11-02T12:00:00.000Z"))
        self.state()
        path.unlink()

        self.assertEqual(self.total(), 1)

    def test_a_broken_summary_is_rebuilt_and_set_aside(self):
        pergula.USAGE_PATH.write_text("{{{")
        self.write("s.jsonl", reply("msg_1", "2026-11-02T12:00:00.000Z"))

        self.assertEqual(self.total(), 1)
        self.assertEqual(pergula.USAGE_PATH.with_name("usage.json.broken").read_text(), "{{{")

    def test_a_summary_of_the_wrong_shape_is_rebuilt(self):
        pergula.USAGE_PATH.write_text(json.dumps({"version": pergula.USAGE_VERSION, "hours": []}))
        self.write("s.jsonl", reply("msg_1", "2026-11-02T12:00:00.000Z"))

        self.assertEqual(self.total(), 1)

    def test_a_first_version_summary_keeps_only_what_cannot_be_read_again(self):
        def leaf(calls):
            return {"claude-opus-5-5": {"main": {**dict.fromkeys(pergula.LEAF_FIELDS, 0), "calls": calls}}}

        pergula.USAGE_PATH.write_text(json.dumps({
            "version": 1, "settings": {}, "files": {"x": {"offset": 9}}, "folders": {}, "titles": {},
            "hours": {"2026-09-01T10": {"/old": {"gone": leaf(5)}},
                      "2026-11-02T09": {"/work/app": {"s": leaf(7)}}},
            "versions": {"2026-09-01": {"2.0": 5}, "2026-11-02": {"2.1": 7}},
        }))
        self.write("s.jsonl", reply("msg_1", "2026-11-02T12:00:00.000Z"))

        state = self.state()
        self.assertEqual(self.total(), 6)
        self.assertEqual(state["version"], pergula.USAGE_VERSION)
        self.assertEqual(state["versions"], {"2026-09-01": {"2.0": 5}, "2026-11-02": {"2.1": 1}})

    def test_the_report_answers_with_nothing_indexed(self):
        report = pergula.usage_report(pergula.fresh_usage(), "week", "", set())

        self.assertEqual(report["totals"]["calls"], 0)
        self.assertEqual(report["prev"], "")

    def test_a_project_switched_off_leaves_the_totals(self):
        self.write("s.jsonl", reply("msg_1", "2026-11-02T12:00:00.000Z"))
        state = self.state()
        project = self.leaves()[0][1]

        report = pergula.usage_report(state, "day", "2026-11-02T09", {project})
        self.assertEqual(report["totals"]["calls"], 0)
        self.assertEqual(report["projects"][0]["calls"], 1)

    def test_a_session_keeps_its_title(self):
        self.write("s.jsonl", record("fix the login"), reply("msg_1", "2026-11-02T12:00:00.000Z"))
        state = self.state()
        project = self.leaves()[0][1]

        found = pergula.usage_sessions(state, "day", "2026-11-02T09", project)
        self.assertEqual(found["sessions"][0]["title"], "fix the login")


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


class Caffeine(unittest.TestCase):
    """The Mac is held awake by a child process, and the page is told about it by
    a deadline. Everything that can go wrong here is a lie told to the page: a
    countdown for a process that died, a second assertion running unreachable
    behind the first, or a recorded pid signalled after the number was reused.

    No real `caffeinate` is spawned. A test that kept the machine awake for a
    quarter of an hour, and left it awake when it failed, would be worse than the
    bug it looked for."""

    def setUp(self):
        self.home = Path(tempfile.mkdtemp())
        self.file = pergula.CAFFEINE_PATH
        pergula.CAFFEINE_PATH = self.home / "caffeine.json"
        self.spawned = []

    def tearDown(self):
        pergula._CAFFEINE["child"] = None
        pergula._CAFFEINE["until"] = 0.0
        pergula.CAFFEINE_PATH = self.file

    def fake_popen(self, alive=True):
        """A stand-in for the child: `poll()` is how pergula asks whether the
        assertion is still up."""
        child = unittest.mock.Mock()
        child.pid = 4242 + len(self.spawned)
        child.poll.return_value = None if alive else 0
        self.spawned.append(child)
        return child

    def start(self, hours, alive=True):
        with unittest.mock.patch.object(pergula.subprocess, "Popen",
                                        side_effect=lambda *a, **k: self.fake_popen(alive)):
            return pergula.start_caffeine(hours)

    def test_nothing_running_reads_as_asleep(self):
        self.assertEqual(pergula.caffeine_state()["until"], 0)

    def test_starting_sets_a_deadline_two_hours_out(self):
        state = self.start(2)

        self.assertAlmostEqual(state["until"] - time.time(), 2 * 3600, delta=5)

    def test_starting_passes_the_flags_that_actually_hold_sleep(self):
        with unittest.mock.patch.object(pergula.subprocess, "Popen",
                                        side_effect=lambda *a, **k: self.fake_popen()) as spawn:
            pergula.start_caffeine(1)

        self.assertEqual(spawn.call_args.args[0], ["caffeinate", "-disu", "-t", "3600"])

    def test_a_second_start_ends_the_first(self):
        self.start(1)
        self.start(4)

        self.assertEqual(self.spawned[0].terminate.call_count, 1)
        self.assertIs(pergula._CAFFEINE["child"], self.spawned[1])

    def test_stopping_ends_the_child_and_clears_the_deadline(self):
        self.start(1)

        state = pergula.stop_caffeine()

        self.assertEqual(self.spawned[0].terminate.call_count, 1)
        self.assertEqual(state["until"], 0)

    def test_a_child_that_exited_reads_as_asleep(self):
        """`caffeinate -t` ends by itself. The clock still says hours to go, so
        the process is what gets asked."""
        self.start(4)
        self.spawned[0].poll.return_value = 0

        self.assertEqual(pergula.caffeine_state()["until"], 0)

    def test_the_hours_are_clamped_to_the_limit(self):
        state = self.start(pergula.CAFFEINE_LIMIT + 40)

        self.assertAlmostEqual(state["until"] - time.time(),
                               pergula.CAFFEINE_LIMIT * 3600, delta=5)

    def test_the_deadline_is_written_down_with_the_pid(self):
        self.start(1)

        saved = json.loads(pergula.CAFFEINE_PATH.read_text())
        self.assertEqual(saved["pid"], self.spawned[0].pid)

    def test_stopping_clears_the_recorded_pid(self):
        self.start(1)
        pergula.stop_caffeine()

        self.assertEqual(json.loads(pergula.CAFFEINE_PATH.read_text()),
                         {"until": 0, "pid": 0})

    def test_a_restart_clears_a_deadline_it_can_no_longer_honour(self):
        pergula.save_caffeine(time.time() + 3600, 0)

        pergula.adopt_caffeine()

        self.assertEqual(json.loads(pergula.CAFFEINE_PATH.read_text())["until"], 0)

    def test_a_reused_pid_is_not_signalled(self):
        """This process answers to its own pid and is not caffeinate."""
        pergula.save_caffeine(time.time() + 3600, os.getpid())

        with unittest.mock.patch.object(pergula.os, "kill") as kill:
            pergula.adopt_caffeine()

        self.assertEqual(kill.call_count, 0)

    def test_a_surviving_orphan_is_signalled(self):
        pergula.save_caffeine(time.time() + 3600, 4242)

        with unittest.mock.patch.object(pergula, "owns_pid", return_value=True):
            with unittest.mock.patch.object(pergula.os, "kill") as kill:
                pergula.adopt_caffeine()

        self.assertEqual(kill.call_args.args[0], 4242)

    def test_a_missing_file_is_not_an_error(self):
        pergula.adopt_caffeine()

        self.assertFalse(pergula.CAFFEINE_PATH.exists())

    def test_a_broken_file_is_not_an_error(self):
        pergula.CAFFEINE_PATH.write_text("{{{")

        pergula.adopt_caffeine()

        self.assertEqual(pergula.CAFFEINE_PATH.read_text(), "{{{")


if __name__ == "__main__":
    unittest.main(verbosity=2)
