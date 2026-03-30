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

## Conditional Steps

```yaml
- name: Shell lint
  if: hashFiles('**/*.sh') != ''
  run: find . -name '*.sh' -not -path '*/build/*' | xargs shellcheck -S warning
```
