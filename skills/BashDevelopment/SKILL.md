---
name: BashDevelopment
version: 0.1.0
description: "Bash and POSIX shell conventions for the forge ecosystem — idioms over subprocesses, fail-safe defaults, probe guarding, multi-line command substitution, exit-code semantics. USE WHEN writing or reviewing shell scripts (audit tools, hooks, build scripts), designing CLI flag handling, or wiring shell tools into CI."
---

# BashDevelopment

Conventions for writing bash and POSIX shell scripts in the forge ecosystem and adjacent personal projects. Reference implementation lives in [check-mac][CHECKMAC] and the build hooks under forge-core.

For audit-script architecture (severity ladders, key:value output, orchestrator dispatch), see the companion skill [AuditScripts](../AuditScripts/SKILL.md).

## Idioms

Use bash built-ins instead of spawning subprocesses for things bash can do natively:

```sh
# Substring (case-sensitive)
[[ "$status" == *"enabled"* ]]

# Regex
[[ "$ports" =~ \.22[[:space:]] ]]
[[ "$dns" =~ ^(1\.1\.1\.1|8\.8\.8\.8)$ ]]

# Wildcard
[[ "$groups" == *admin* ]]

# Prefix / suffix removal
filename="${path##*/}"          # basename
extension="${filename##*.}"     # extension
trimmed="${var%, }"             # strip trailing ", "
```

Avoid:

```sh
echo "$var" | grep -q "pattern"   # spawns a subprocess for what bash can do natively
basename="$(basename "$path")"    # use ${path##*/} instead
```

Use `[[ ]]` for tests, never `[ ]`. `[[ ]]` is bash-aware (no word splitting, supports `=~`, supports `&&`/`||` inside).

## Fail-Safe Defaults

Default to the safe value, then flip on observed evidence. Never default to OK:

```sh
pass_check=$CRIT
[[ "$setting" == "expected" ]] && pass_check=$OK
```

For values that may legitimately be empty (managed-config keys, profile-overridden plist domains), do not collapse empty into a known value:

```sh
# WRONG — masks the empty case
setting=${setting:-0}

# RIGHT — preserve the empty distinction
[[ -z "$setting" ]] && pass_check=$UNKNOWN
[[ "$setting" == "1" ]] && pass_check=$OK
[[ "$setting" == "0" ]] && pass_check=$CRIT
```

## Probe Guarding

A probe must not provoke an interactive installer or prompt. On macOS, `git --version` triggers the Xcode CLT GUI installer when CLT is absent. Guard with `command -v`, plus `xcode-select -p` for Xcode-tooling probes:

```sh
git_version=""
if command -v git >/dev/null 2>&1 && xcode-select -p >/dev/null 2>&1; then
    git_version=$(git --version 2>/dev/null | awk '{print $3}')
fi
```

Apply the `command -v` guard before any third-party CLI (`brew`, `gpg`, `openssl`). An absent tool is not a misconfiguration unless the script is specifically *about* the tool's installation.

## Multi-Line Command Substitution

For readability, break long pipelines across lines:

```sh
firewall_enabled=$(
    defaults read /Library/Preferences/com.apple.alf globalstate 2>/dev/null
)
```

```sh
non_apple_kexts=$(
    kmutil showloaded 2>/dev/null \
        | awk 'NR>1 {print $NF}' \
        | grep -v '^com\.apple\.'
)
```

Indent the body four spaces. Closing paren on its own line. Same shape works for `local val=$(...)`:

```sh
local val
val=$(
    defaults read "$DOMAIN" "$KEY" 2>/dev/null
)
```

## Variable Quoting

Always quote variables in tests and command substitutions, except inside `[[ ]]` where bash does the right thing:

```sh
# Quote in shell command lines
mv "$src" "$dst"
echo "$result"

# [[ ]] does not require quoting for word-splitting, but quote for clarity
[[ "$status" == *enabled* ]]

# Always quote command substitutions in calling sites
check "$(key pass_x)" "Label" "$ENABLED" "$DISABLED"
```

## Suppressing Expected Errors

`2>/dev/null` to silence stderr from probes that may legitimately fail (absent plist key, missing CLI, no matching process):

```sh
setting=$(defaults read com.apple.foo Bar 2>/dev/null)
listening=$(lsof -i :22 2>/dev/null)
```

Do not suppress stdout. Do not redirect to `/dev/null` everything wholesale — that hides bugs. Only silence stderr where empty output is the legitimate signal.

## Exit-Code Semantics

For tools that humans run interactively, exit `0` always and report status visually. For the same tool wired into CI, expose an explicit `--strict` flag that propagates non-zero on failure. Never make non-zero exit the default; that surprises every existing user and breaks pipes through `tee` or `less`.

```sh
strict=0
for arg in "$@"; do
    case "$arg" in
        --strict) strict=1 ;;
        -h|--help)
            echo "Usage: $0 [--strict]"
            exit 0
            ;;
    esac
done

# ... do work, accumulate $issues ...

if (( strict && issues > 0 )); then
    exit 1
fi
```

## Function Layout

Helpers go in a sourced lib. Standalone scripts inline what they need. Use `local` for function-scope variables:

```sh
key() {
    local field="$1"
    echo "$data" | grep "^${field}:" | cut -d: -f2-
}
```

`cut -d: -f2-` (with the trailing dash) preserves trailing colons in values; `-f2` truncates at the first colon and silently corrupts IPv6 addresses, hostnames with ports, and structured status strings.

Avoid `local val=$(cmd)` because the assignment masks the return code of `cmd`. Split into two lines if the return code matters:

```sh
local val
val=$(cmd)
```

## Linting

Run `shellcheck` before committing. Treat warnings as bugs unless they flag a deliberate pre-existing pattern; in that case, add a `# shellcheck disable=SCxxxx` comment with a one-line reason.

Common pre-existing patterns the lint may flag:

- `SC2155` (mask return value with `local val=$(...)`): split into two lines, see above.
- `SC2154` (variable referenced but not assigned): expected for sourced libs that read variables set by the caller.
- `SC2034` (variable appears unused): expected for status-string constants in a sourced style lib.

## Cross-Platform Considerations

Bash version varies. macOS ships an old bash 3.2 at `/bin/bash`; modern bash (4+, 5+) is at `/opt/homebrew/bin/bash` or `/usr/local/bin/bash`. Scripts using `[[ ]]`, `${var//}`, and `=~` work in 3.2; associative arrays (`declare -A`) require 4+.

If a script needs bash 4+, use `#!/usr/bin/env bash` and document the dependency. If portability to old macOS bash matters, use `#!/bin/bash` and stay in 3.2-compatible territory.

For coreutils differences (`sed`, `date`, `readlink`), prefer POSIX flags or guard with `command -v gsed` / `command -v gdate`.

## Code Style

- Self-documenting names. A comment is a smell unless it explains *why*.
- 4-space indentation, never tabs.
- Liberal blank lines between logical sections.
- One `# Source:` comment at the top of any check or audit script pointing to the upstream reference.
- Lowercase function names with snake_case multi-word (`read_hook_input`).

[CHECKMAC]: https://github.com/N4M3Z/check-mac
