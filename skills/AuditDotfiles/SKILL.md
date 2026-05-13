---
name: AuditDotfiles
version: 0.1.0
description: "Scan a dotfiles tree for secrets via gitleaks, aggregate findings by top-level directory and rule, then surgically filter flagged lines from shell-history files before importing into atuin. USE WHEN auditing dotfiles before pushing to a public repo, scanning rsynced dotfiles-private contents, importing legacy zsh or bash history into atuin, filtering credential leaks out of a shell history file, deciding which dotfile subdirectories can be made public."
sources:
    - https://github.com/gitleaks/gitleaks
    - https://atuin.sh/docs/configuration/config
    - https://mikefarah.gitbook.io/yq
---

# AuditDotfiles

Scan a dotfiles tree (typically `dotfiles/` and `dotfiles-private/`) for secrets with gitleaks, group findings by top-level directory and rule so the right disposition is obvious, and produce a clean version of any flagged shell-history file by stripping just the leaked lines (not the whole file).

The executable end-to-end pipeline lives at `scripts/audit-dotfiles.sh` in this skill directory. Run it for the actual audit; the body below documents intent and the reasoning behind each step. Related: [SecretScan][SECRETSCAN] in forge-core covers commit-time prevention; this skill covers migration-time audit + history filtering.

## Instructions

1. **Scan with gitleaks**, redacted, into a JSON report:

    ```sh
    gitleaks detect --no-banner --redact --no-git -s <path> \
        --report-format json --report-path <out>.json
    ```

    `--redact` masks matched secrets inside the report. `--no-git` scans the filesystem rather than git history — faster for one-shot audits.

2. **Aggregate findings** by top-level dir + rule. The breakdown maps directly to disposition decisions (much more useful than the raw count):

    ```sh
    yq -p json -o tsv '.[] | [.File, .RuleID]' <out>.json \
        | awk -F'\t' -v prefix="<scan-root>/" '
            { sub("^" prefix, "", $1)
              split($1, parts, "/")
              print parts[1] "\t" $2
            }' \
        | sort | uniq -c
    ```

    Expected shape: `gnupg/` shows `private-key` (the GPG export), `kube/` shows `jwt` (bearer tokens), and the shell-history directory typically shows accumulated `generic-api-key`, `github-pat`, `stripe-access-token` matches from `curl -H Authorization:` and `export STRIPE_KEY=...` invocations.

3. **Filter the history file** when gitleaks flags a shell history (`.zsh_history`, `.zhistory`, `.bash_history`, `.history`). One yq + awk pass groups per-file findings and builds a sed delete-list (`Nd;Md;...`), then runs sed once per history file:

    ```sh
    yq -p json -o tsv '.[] | [.File, .StartLine]' <out>.json \
        | awk -F'\t' '
            $1 ~ /(history|zhistory)$/ {
                key = $1 "\t" $2
                if (!seen[key]++) exprs[$1] = (exprs[$1] ? exprs[$1]";" : "") $2 "d"
            }
            END { for (f in exprs) print f "\t" exprs[f] }' \
        | while IFS=$'\t' read -r hist expr; do
            sed -e "${expr}" "${hist}" > "${hist}.clean"
        done
    ```

    Then import the clean file into atuin:

    ```sh
    atuin import <shell> <history-file>.clean
    ```

    Do **not** pre-split `&&` chains before import. atuin's `fulltext` search matches substrings against the whole command, so typing `cmd2` recalls `cmd1 && cmd2 && cmd3`. Splitting strips the meaningful preceding context (the `cd dir` that prefixed the action).

4. **Decide per-dir disposition** from the aggregated table:

    | Finding shape                                  | Action                                                                                 |
    | ---------------------------------------------- | -------------------------------------------------------------------------------------- |
    | `gnupg/` private-key matches                   | Keep `.asc` exports as offline archive; do not bulk-import into the new GPG keychain   |
    | `kube/` jwt matches                            | Rotate bearer tokens at next cluster touch; keep current file private until rotated    |
    | shell-history matches (multiple rule types)    | Filter and import per step 3; preserve the rest of the file                            |
    | `password-store/` (no gitleaks matches)        | Encrypted; filenames are the secret names — do not enumerate carelessly                |
    | `*.gitconfig_local` token matches              | Diff against current `git config --global`; merge live config, drop stale tokens       |
    | `ssh/hosts`, `ssh/vendor/*` (no token matches) | Contain hostnames + IPs; treat as fully sensitive even when gitleaks finds nothing     |

5. **Rotate any live credentials** that gitleaks flagged before the cleaned dotfiles tree migrates into a less-private context (chezmoi source, public push, agent training corpus).

## Constraints

- **Never print raw matches** in chat, journal, commit messages, or PR descriptions — even with `--redact`, the file path and line number can identify the secret in context. Report aggregated counts + categories only.
- **Never bulk-delete a flagged history file.** Years of recall live in those lines; surgical line-filtering preserves the rest.
- **Never use trufflehog with `--verify`** during this audit. Verification mode contacts the issuing service with the candidate token, which leaks the existence of the leak even when the token is benign. gitleaks is offline-only by design.
- **Do not pre-split compound commands** before atuin import. Each shell history line is the unit of recall; `&&` chains carry semantic context that splitting destroys.
- **Filter line numbers are per-file, not per-finding.** A single line can carry multiple findings (e.g., one `curl` command containing both an API key and a stripe token). The awk pass in step 3 deduplicates via the `seen[]` table.
- **Use mikefarah's yq, not Andrey Kislyuk's** — the script checks for the right binary. The two share a name but have different syntax; mikefarah's is the Go-based YAML/JSON tool.
- **`--no-git` skips git history.** When the rsynced tree contains a `.git/` directory and historical secrets matter, drop `--no-git` and accept the slower scan.

[SECRETSCAN]: https://github.com/N4M3Z/forge-core/tree/main/skills/SecretScan
