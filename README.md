# forge-dev

Developer discipline skills and agents for the forge ecosystem — code quality, testing, defensive programming, debugging, git workflows, and code review.

Part of [forge-user](https://github.com/N4M3Z/forge-user), a modular AI orchestration framework.

## Skills

| Skill | What it does |
|-------|-------------|
| **CodeCleanup** | Proactive code cleanup — duplication removal, pattern adoption, readability maximization |
| **DataExplorer** | Static HTML data explorer apps from SQL or datasets (Vega-Lite, Chart.js, Tabulator) |
| **DataVisualization** | Choose and configure visualization tools for data explorer apps |
| **DefensiveProgramming** | Input validation, error boundaries, fail-safe defaults, invariant checking |
| **FinishBranch** | Decide how to integrate completed work once tests pass — merge, PR, or cleanup |
| **FixCI** | Inspect failing GitHub Actions checks, pull logs, and propose a fix plan |
| **FixIssue** | End-to-end issue fixing — triage, diagnose, branch, PR/MR, close (GitHub + GitLab) |
| **FixTests** | Run tests and systematically fix failing ones using smart error grouping |
| **GitHub** | GitHub CLI reference — repos, releases, Actions/CI, PR ops, branch protection |
| **ReceiveReview** | Process code review feedback with technical rigor — verify before implementing |
| **RequestingCodeReview** | Author a clear, scoped request when asking for a code review |
| **RustDevelopment** | Rust conventions — crate structure, error handling, CLI patterns, config loading |
| **SubagentDrivenDevelopment** | Delegate independent plan tasks to subagents |
| **SystematicDebug** | Four-phase debugging methodology — root cause before fixes |
| **TestDrivenDevelopment** | Red-Green-Refactor, test categories, coverage strategy, anti-patterns |

Shell scripting conventions (`BashConventions`) live in forge-core alongside `MarkdownConventions`.

## Agents

| Agent | What it does |
|-------|-------------|
| **ArchitectReviewer** | Architecture reviewer — system designs, scalability, integration, evolution |
| **CodeReviewer** | Senior code reviewer — correctness, security, performance, maintainability |
| **ErrorDetective** | Error and log forensic analyst — cascade mapping, root cause in distributed systems |
| **RefactoringSpecialist** | Safe stepwise refactoring with characterization tests and catalog-based transforms |

## Install

```sh
make install     # deploy skills and agents, activate git hooks
make validate    # run the pre-commit validation chain
make clean       # remove build artifacts
```

Requires the `forge` CLI on PATH ([forge-cli](https://github.com/N4M3Z/forge-cli)). Or call it directly:

```sh
forge install --target ~ .
```

## Architecture

```text
skills/               skill directories — SKILL.md + optional @-included companions
agents/               agent markdown files (flat directory)
defaults.yaml         skill roster + provider config
config.yaml           user overrides (gitignored)
module.yaml           module metadata
.claude-plugin/       Claude Code plugin discovery
.provenance/          SLSA sidecars for every versioned file
```

## Provenance

Several skills and all four agents were adopted from [davila7/claude-code-templates](https://github.com/davila7/claude-code-templates) (MIT). Each adopted file carries a SLSA provenance sidecar under `.provenance/` recording the upstream commit SHA, file SHA-256, and transform dependency chain. Run `forge provenance .` to audit.

## License

[EUPL-1.2](LICENSE)
