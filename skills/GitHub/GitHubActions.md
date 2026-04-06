# GitHub Actions CI

Workflow files live in `.github/workflows/` with `.yaml` extension.

## Runners

| Runner           | When to use                                    |
| ---------------- | ---------------------------------------------- |
| `ubuntu-latest`  | Default for most projects                      |
| `macos-latest`   | macOS-specific tools (Xcode, EventKit, swift)  |
| `windows-latest` | Windows-specific tools (.NET, WinUI, PowerShell) |

## Common Actions

| Action                         | Purpose                |
| ------------------------------ | ---------------------- |
| `actions/checkout@v4`          | Clone the repo         |
| `actions/setup-python@v5`     | Install Python         |
| `actions/setup-node@v4`       | Install Node.js        |
| `dtolnay/rust-toolchain@stable` | Install Rust         |

## Minimal CI Template

```yaml
name: CI

on:
    push:
        branches: [main]
    pull_request:
        branches: [main]

jobs:
    validate:
        runs-on: ubuntu-latest
        steps:
            - uses: actions/checkout@v4

            - uses: actions/setup-python@v5
              with:
                  python-version: "3.12"

            - name: Run tests
              run: make test

            - name: Lint
              run: make lint
```

## ADR Schema Validation

[structured-madr](https://github.com/zircote/structured-madr) ships a GitHub Action for ADR frontmatter validation:

```yaml
- uses: zircote/structured-madr@main
  with:
      path: docs/decisions
      schema: templates/forge-adr.json
      fail-on-error: true
```

Or use the Python fallback:

```yaml
- name: ADR validation
  run: python3 bin/validate-adr.py templates/forge-adr.json docs/decisions/
```

## Security

Never interpolate untrusted input directly in `run:` blocks. Untrusted inputs include `github.event.issue.title`, `github.event.pull_request.body`, `github.event.comment.body`, `github.head_ref`, and commit messages.

Use `env:` variables instead:

```yaml
# unsafe
- run: echo "${{ github.event.issue.title }}"

# safe
- env:
      TITLE: ${{ github.event.issue.title }}
  run: echo "$TITLE"
```

## Tool Installation

Prefer `apt install` over `curl` + GitHub API for CI tools. GitHub API rate limits (60 req/hr unauthenticated) cause intermittent failures.

```yaml
# fragile — rate limited, URL parsing breaks
- run: curl -sSfL "$(curl -s https://api.github.com/repos/gitleaks/gitleaks/releases/latest | grep -o 'https://[^"]*linux_x64.tar.gz')" | tar xz -C /usr/local/bin

# reliable — deterministic, no API calls
- run: sudo apt-get install -y gitleaks
```

## prek Integration

`j178/prek-action@v2` installs and runs prek. It caches hook environments across runs — stale cache entries referencing deleted files cause failures. Clear with `rm -rf ~/.cache/prek` if cache corruption is suspected.

prek scans ALL `.pre-commit-config.yaml` files in the repo, not just the root. Template configs with remote `repo:` references cause failures if the referenced repo lacks `.pre-commit-hooks.yaml`.

A `.pre-commit-hooks.yaml` at the repo root makes prek treat the repo as a hook source. With `language: rust`, prek runs `cargo install --bins --locked` from the cloned repo on first use, caching the binary in `~/.cache/prek/`. Subsequent runs reuse the cached binary. Cache key is based on the `rev:` — bumping the rev triggers a recompile (~2-5 min on cold CI runners).

Use `.prekignore` (gitignore syntax) at the repo root to exclude directories from workspace discovery. Template configs in `templates/` that reference remote repos cause failures if scanned.

## Composite Actions

Ship reusable CI steps alongside the tool repo at `.github/actions/<name>/action.yml`. Consumers reference as:

```yaml
- uses: owner/repo/.github/actions/setup-tool@v1.0.0
```

Composite actions use `runs: using: composite` with shell steps — no TypeScript build needed. Cache binaries with `actions/cache@v4` keyed on version + runner platform.

## Branch Rulesets

Rulesets with required approvals block repo owners from merging their own PRs. Add the Repository Admin role as a bypass actor:

```sh
gh api repos/OWNER/REPO/rulesets/ID --method PUT --input - <<< '{
    "bypass_actors": [{"actor_id": 5, "actor_type": "RepositoryRole", "bypass_mode": "always"}]
}'
```

## Conditional Steps

```yaml
- name: Shell lint
  if: hashFiles('**/*.sh') != ''
  run: find . -name '*.sh' -not -path '*/build/*' | xargs shellcheck -S warning
```
