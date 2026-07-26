# Agent Instructions

## General

- **Unrelated changes:** Do not modify files unrelated to the current task without asking first.
- **Destructive actions:** Always ask for approval before performing destructive or hard-to-reverse actions (e.g. `git push --force`, `git reset --hard`, deleting branches/files, dropping tables).

## Project Overview

This is an async Python Modbus TCP client library for Sugar Valley NeoPool based pool controllers. It is distributed on PyPI as `neopool-modbus` and imported as `neopool_modbus`. The library is the communication layer used by the Home Assistant `neopool` integration and is usable from any async Python project. The package lives under `src/neopool_modbus/` and is a typed package (`py.typed`).

## Development Commands

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run a single test file
pytest tests/test_client.py

# Run tests with coverage
pytest --cov=neopool_modbus --cov-report=term-missing tests/

# Type checking (must be 0 errors)
basedpyright

# Linting
ruff check

# Formatting check
ruff format --check

# Auto-fix formatting
ruff format
```

## Architecture

### Public API

The package exports a small surface from `src/neopool_modbus/__init__.py`:

- `NeoPoolModbusClient` - the async client (connect, read/write registers, retry/backoff).
- `async_probe_serial` - one-shot serial-number probe for connection validation.
- Exception hierarchy: `NeoPoolError` and its subclasses `NeoPoolConnectionError`,
  `NeoPoolModbusError`, `NeoPoolTimeoutError`, `NeoPoolInvalidStateError`.
- `InvalidStateReason`, `__version__`.

Consumers should import from the top-level package, not from submodules.

### Modules

- **`client.py`** (`NeoPoolModbusClient`): async Modbus TCP client via `pymodbus`. Connects,
  reads/writes registers, applies retry/backoff, and verifies writes. Decodes raw registers into a
  structured data snapshot dict.
- **`decoders.py`**: pure decoders, encoders and computations for register values. No I/O.
- **`registers.py`**: Modbus register addresses and protocol-level constants for NeoPool devices.
- **`status_mask.py`**: status mask decoders (based on `xsns_83_neopool.ino`).
- **`capabilities.py`**: capability predicates over a decoded data snapshot (hydrolysis, pH, Redox,
  chlorine, etc.).
- **`probe.py`**: lightweight one-shot probes that open a fresh connection, do a single read, and
  tear it down (e.g. `async_probe_serial`).
- **`exceptions.py`**: the public exception hierarchy.

### Key Patterns

- Decoders in `decoders.py` and `status_mask.py` are pure functions (no I/O); all transport lives
  in `client.py` and `probe.py`. Keep that separation when adding features.
- The client returns a flat data snapshot dict; capability predicates in `capabilities.py` read
  from it to decide what a consumer can use.
- Probes raise the public `NeoPoolError` hierarchy so callers do not need to import `pymodbus` to
  handle errors.

## Branch Naming

Follow [Conventional Branch](https://conventional-branch.github.io/) format: `<type>/<description>`

- Lowercase alphanumerics and hyphens only (dots allowed in release versions)
- No consecutive, leading, or trailing hyphens or dots
- Include ticket/issue number when applicable

| prefix     | when to use                                 |
| ---------- | ------------------------------------------- |
| `feature/` | new feature (alias: `feat/`)                |
| `bugfix/`  | bug fix (alias: `fix/`)                     |
| `hotfix/`  | urgent fix                                  |
| `release/` | release preparation (e.g. `release/v1.2.0`) |
| `chore/`   | non-code tasks (deps, docs, config)         |

Examples: `feat/add-login-page`, `fix/header-bug`, `feature/issue-123-new-login`

## Git Commits

### Approval

- **Never commit or push automatically.** Always wait for my explicit approval before running `git commit` or `git push`.
- **Approval is per action, not per session.** Approving one commit or push does not authorize the next one. Ask again each time.
- **Never automatically merge pull requests.** This will be always done by me manually.
- **Tests:** If the project has tests, run them before proposing a commit. Verify that all tests pass and that code coverage has not decreased.

### Versioning & Merge Strategy

- **Versioning is handled by release-please.** Never bump the version by hand; release-please opens the release PR.
- **PRs are squash-merged.** Only the PR title reaches the changelog, so the title must be a clean, correct commit message. Per-commit messages inside a PR are internal history only.

### Commit Message Format

Always use the format: `<type>(<scope>): <gitmoji> <description>`

**Rules:**

- `scope` is optional but use it when the change is clearly scoped to a module
  (e.g. `client`, `decoders`, `registers`, `status_mask`, `capabilities`, `probe`, `exceptions`)
- `description`: lowercase, imperative mood ("add", not "added"), no period at end
- Keep it terse. Commit subjects, bodies, and code comments should be concise and to the point; avoid verbose prose.
- No em-dashes anywhere (commit messages, PR text, code, comments, docs). Use a regular hyphen, comma, or separate sentence instead.
- No `@` or `#` characters in commit messages, PR text, or comments: GitHub auto-links them. The only exception is a `Resolves #<issue-number>` trailer at the end of a commit or PR body.

**Pick the type and gitmoji that best reflect the nature of the change:**

| type       | gitmoji | when to use                                        |
| ---------- | ------- | -------------------------------------------------- |
| `feat`     | ✨      | new user-facing feature                            |
| `feat!`    | 💥      | breaking change                                    |
| `fix`      | 🐛      | bug fix                                            |
| `fix`      | 🩹      | minor / non-critical fix (style, typo, off-by-one) |
| `fix`      | 🚑️      | critical hotfix                                    |
| `fix`      | 🔒️      | security / privacy fix                             |
| `docs`     | 📝      | add or update documentation or comments            |
| `style`    | 🎨      | code structure / formatting (no logic change)      |
| `style`    | 💄      | UI or style files                                  |
| `refactor` | ♻️      | refactor without behaviour change                  |
| `test`     | ✅      | add, update, or fix tests                          |
| `test`     | 🧪      | add a failing test                                 |
| `perf`     | ⚡️      | performance improvement                            |
| `chore`    | 🔧      | config or tooling update                           |
| `chore`    | 🏷️      | add or update types / labels                       |
| `chore`    | 🔖      | release or version tag                             |
| `chore`    | ⬆️      | upgrade dependency                                 |
| `chore`    | ⬇️      | downgrade dependency                               |
| `chore`    | 🌱      | add or update seed / fixture files                 |
| `ci`       | 👷      | add or update CI build system                      |
| `ci`       | 💚      | fix CI build                                       |
| `revert`   | ⏪️      | revert a previous commit                           |

**Commit message body:**

Add a blank line after the subject line, then a bullet list covering:

- what changed (one bullet per logical change, imperative style)
- why it was changed (motivation, context)
- relevant technical detail if non-obvious

Keep bullets concise (one line each). If the commit resolves a GitHub issue, end the body with `Resolves #<issue-number>`.

```
feat(client): ✨ add async event-notification polling

- replace interval polling with Modbus event notifications
- reduce unnecessary register reads when no state change occurred
- add configurable debounce threshold for notification batching
- improve responsiveness and reduce Modbus bus load

Resolves #97
```

**Examples from this project:**

```
feat(client): ✨ add async_start_backwash via FILTVALVE registers
feat(client): ✨ add async_stop_backwash and skip verify for countdown registers
fix(client): 🐛 guard backwash against auto mode and align filtvalve API with relays
refactor(decoders): ♻️ extract pure register decoding helpers
chore: 🩹 drop unused noqa flagged by ruff 0.16
chore(deps): ⬆️ bump codecov/codecov-action from 5 to 6
```

### Shell Execution

Multi-line commit messages in bash/zsh: use multiple `-m` flags (one per paragraph) or heredoc (`git commit -F - <<'EOF' ... EOF`). A single `-m` with newlines inside quotes does NOT work reliably.

## Pull Requests

- PR description must be in **English** and **Markdown** format (ready for copy & paste into GitHub).
- **PR title** must follow the same commit message format: `<type>(<scope>): <gitmoji> <description>`.
- **PR body** should use emoji to visually categorize sections and bullet points.

## Code Quality

### Type Checking

- This project uses **basedpyright** with `typeCheckingMode: strict` (see `pyrightconfig.json`).
- Run `basedpyright` before committing and ensure **0 errors**.
- CI enforces type checking via `.github/workflows/typecheck.yaml`.

### Linting & Formatting

- Use **ruff** for both linting and formatting.
- Run `ruff check` and `ruff format --check` before committing.
- CI enforces ruff checks on every PR.

### Pre-commit Checklist

Before proposing a commit, verify:

1. `basedpyright` - 0 errors
2. `ruff check` - all checks passed
3. `ruff format --check` - all files formatted
4. `pytest` - all tests pass, coverage not decreased (100% coverage if applicable)
