# forge-dev

Developer discipline skills for the forge ecosystem — code quality, testing, defensive programming, git conventions.

Part of [forge-user](https://github.com/N4M3Z/forge-user), a modular AI orchestration framework.

## Skills

| Skill | What it does |
|-------|-------------|
| **CodeCleanup** | Proactive code cleanup — duplication removal, pattern adoption, readability maximization |
| **DefensiveProgramming** | Defensive coding principles — input validation, error boundaries, fail-safe defaults |
| **RustDevelopment** | Rust conventions for the forge ecosystem — crate structure, error handling, CLI patterns |
| **TestDrivenDevelopment** | Test discipline — Red-Green-Refactor cycle, test categories, coverage strategy |
| **Git** | Git best practices — conventional commits, submodule workflows, branch strategy |

## Install

```bash
make install    # deploy skills (Claude, Gemini, Codex, OpenCode)
make verify     # check skills deployed across all providers
make test       # validate-module convention checks
make clean      # remove previously installed skills
```

Requires forge-lib submodule. If missing: `git submodule update --init lib`.

## Architecture

```
skills/               — 5 skill directories (SKILL.md + optional SKILL.yaml)
lib/                  — git submodule → forge-lib (Rust binaries)
defaults.yaml         — skill roster + provider config
config.yaml           — user overrides (gitignored)
module.yaml           — module metadata
.claude-plugin/       — Claude Code plugin discovery
```

## License

MIT
