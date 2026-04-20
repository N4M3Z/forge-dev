# Contributing to forge-dev

forge-dev delivers developer discipline skills — code quality, testing, defensive programming, git conventions — to AI coding tools across providers. Skills are authored once in `skills/` and deployed via `make install`.

## Getting Started

```sh
git clone https://github.com/N4M3Z/forge-dev.git
cd forge-dev
make install     # deploy skills and agents, activate git hooks
make validate    # run the pre-commit validation chain
```

Prerequisites:

- `forge` CLI on PATH ([forge-cli](https://github.com/N4M3Z/forge-cli))
- `shellcheck` (`brew install shellcheck`)
- At least one AI provider CLI (Claude Code, Gemini CLI, Codex, or OpenCode)

## Creating a Skill

Each skill lives in its own directory under `skills/`:

```
skills/YourSkill/
    SKILL.md        # Provider-neutral AI instructions
    SKILL.yaml      # Optional sidecar — provider routing, references
```

SKILL.md carries `name`, `description`, `version` in frontmatter. The `description` drives discovery — use `USE WHEN` to list trigger keywords explicitly.

See [forge-core Contributing](https://github.com/N4M3Z/forge-core/blob/main/CONTRIBUTING.md) for the full authoring guide.

## Validation

```sh
make validate        # via Makefile (runs the pre-commit chain)
forge validate .     # directly
```

The pre-commit hook (in `.githooks/pre-commit`) runs the same checks before every commit. Enable it with `git config core.hooksPath .githooks`.

## Git

Conventional Commits: `type: description`. Lowercase, no trailing period, no scope.

Types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`.

## Pull Requests

1. Fork and create a branch
2. Make changes following the conventions above
3. Run `make validate`
4. Open a PR against `main`

CI runs validation on every PR. The `main` branch requires passing CI before merge.
