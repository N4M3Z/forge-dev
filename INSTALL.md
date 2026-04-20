# forge-dev

> Developer discipline skills for the forge ecosystem — code quality, testing, defensive programming, git conventions.

*This file follows the [install.md](https://github.com/mintlify/install-md) standard — structured instructions for AI agents to execute autonomously. Human readers: see [README.md](README.md) for conventional documentation.*

I want you to install forge-dev for me. Execute all the steps below autonomously.

## OBJECTIVE

Deploy forge-dev skills to all AI providers (Claude, Gemini, Codex, OpenCode) via Makefile.

## DONE WHEN

- `make test` passes
- `ls ~/.claude/skills/CodeCleanup/SKILL.md` (or the chosen provider directory) confirms skill deployment
- `git config core.hooksPath` returns `.githooks`

## Prerequisites

- Claude Code (or another AI provider CLI)
- `forge` CLI on PATH — install from [forge-cli](https://github.com/N4M3Z/forge-cli)
- `shellcheck` for linting

Without Rust: copy `skills/` into the provider config directory (e.g., `~/.claude/skills/`) directly.

## TODO

- [ ] Install prerequisites (forge-cli, shellcheck)
- [ ] Clone the repository
- [ ] Run `make install` to deploy
- [ ] Verify skill deployment
- [ ] Enable git hooks

## Steps

### Clone

```sh
git clone https://github.com/N4M3Z/forge-dev.git
cd forge-dev
```

### Install

```sh
make install
```

### Verify skill deployment

```sh
ls ~/.claude/skills/CodeCleanup/SKILL.md
```

### Enable git hooks

```sh
git config core.hooksPath .githooks
```

EXECUTE NOW: Complete the above TODO list to achieve passing `make test`, deployed skills, and active hooks.
