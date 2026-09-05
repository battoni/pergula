# pergula — one file, no dependencies. These targets exist mostly to encode the
# one thing that is easy to get wrong: the login agent runs the INSTALLED copy
# at ~/.local/bin/pergula, not this source. Editing the source changes nothing
# until `make deploy`.

INSTALLED := $(HOME)/.local/bin/pergula
AGENT     := dev.battoni.pergula
PORT      ?= 7373
SKILL     := $(HOME)/.claude/skills/battoni-new-brand/scripts

.DEFAULT_GOAL := help
.PHONY: help test check marks serve deploy status brand assets lockup proofs clean

help: ## Show this help
	@grep -hE '^[a-z-]+:.*?## ' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

test: ## Run the test suite
	@python3 test_pergula.py

check: test ## Test, then check syntax
	@python3 -c "import ast; ast.parse(open('pergula').read())" && echo "  pergula: syntax ok"

marks: ## Lint every explored mark. Round three fails on purpose — two of those
       ## marks were rejected and are kept as record.
	-@python3 brand/marks/lint.py    | tail -1
	-@python3 brand/marks/r2-lint.py | tail -1
	-@python3 brand/marks/r3-lint.py | tail -1

serve: ## Serve this source in the foreground, on PORT
	@python3 ./pergula --serve --port $(PORT)

deploy: check ## Copy the source over the installed copy and restart the agent
	@cp pergula $(INSTALLED) && chmod +x $(INSTALLED)
	@launchctl kickstart -k "gui/$$(id -u)/$(AGENT)" 2>/dev/null || true
	@until curl -s -o /dev/null http://127.0.0.1:$(PORT)/ 2>/dev/null; do sleep 1; done
	@echo "  deployed — http://127.0.0.1:$(PORT)"

status: ## Is anything listening, and is the installed copy current?
	@python3 ./pergula --status
	@cmp -s pergula $(INSTALLED) \
		&& echo "  installed copy: current" \
		|| echo "  installed copy: STALE — run make deploy"

brand: assets lockup ## Regenerate the lockup and every application asset

lockup: ## Rebuild the lockup from the icon and Space Grotesk
	@python3 brand/build-lockup.py

assets: ## Rebuild favicon, tiles, avatar and README header from the icon
	@python3 brand/build-assets.py

proofs: ## Rebuild the colour proof sheet
	@python3 brand/color/proofs.py

clean: ## Remove generated previews and caches
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@find brand -name "*.html" -delete 2>/dev/null || true
	@find brand -name ".ladder" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "  cleaned"
