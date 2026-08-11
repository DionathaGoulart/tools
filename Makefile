# Dev tasks for the good* tools. `make check` runs everything CI runs.
# Requires: python3 (tests), ruff (python lint), shellcheck (shell lint).
#   brew install ruff shellcheck      # macOS
.PHONY: help test test-sh lint lint-py lint-sh syntax-sh check fix install uninstall doctor

SHELL := bash

# Every shell script: all *.sh plus the extensionless bash entrypoints.
# Mirrored by the `bash -n` step in .github/workflows/ci.yml (that step can't
# use make, since the Windows matrix runner has no make).
SH_SCRIPTS := $(shell find . -path ./.git -prune -o -name '*.sh' -print) \
	goodpomo/goodpomo goodnerd/goodnerd goodhelp/goodhelp lib/shims/python3 \
	goodcheats/good goodcheats/goodcheat goodcheats/goodharness

help:
	@echo "targets: test  test-sh  lint  lint-py  lint-sh  syntax-sh  check  fix  install  uninstall  doctor"

test: ## python unit tests (stdlib unittest, no deps)
	python3 -m unittest discover -s tests -p 'test_*.py' -v

test-sh: ## bash smoke tests (rc block, goodharness) — need symlinks, so no Windows
	bash tests/test_rcblock.sh
	bash tests/test_goodharness.sh

lint: lint-py lint-sh ## every linter

lint-py: ## ruff over all python (incl. extensionless entrypoints — see ruff.toml)
	ruff check .

lint-sh: ## shellcheck over every shell script (config in .shellcheckrc)
	shellcheck --severity=warning $(SH_SCRIPTS)

syntax-sh: ## bash -n syntax gate (catches bash 3.2 issues too)
	@set -e; for f in $(SH_SCRIPTS); do [ -f "$$f" ] || continue; echo "checking $$f"; bash -n "$$f"; done

check: test test-sh lint syntax-sh ## everything CI runs, locally

fix: ## auto-fix what ruff can
	ruff check --fix .

install: ## interactive installer
	bash setup.sh

uninstall: ## interactive uninstaller
	bash setup.sh -u

doctor: ## check the install: anchor symlink, rc block, PATH, skills
	bash goodhelp/goodhelp doctor
