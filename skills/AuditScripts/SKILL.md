---
name: AuditScripts
version: 0.1.0
description: "Architecture for security and health audit scripts: standalone-runnable checks, severity ladder with UNKNOWN, key:value output contract, orchestrator dispatch, exit-code semantics. Language-agnostic; reference implementations in Bash, applies to Python and other languages. USE WHEN writing audit tools, designing check-script contracts, adding checks to tools like check-mac, reviewing audit-script architecture, or porting an audit tool between languages."
---

# AuditScripts

A contract for writing security and health audit scripts. The same contract works in Bash, Python, or any other language that can write structured output to stdout. Reference implementation: [check-mac][CHECKMAC] (Bash). For shell-specific idioms, see the companion skill [BashDevelopment](../BashDevelopment/SKILL.md).

The architecture has three load-bearing pieces:

1. **Check scripts**, each independently runnable, each emitting `key:value` lines.
2. **A severity ladder** with five steps including UNKNOWN.
3. **An orchestrator** that runs checks in series, dispatches severity codes to display, and decides exit-code semantics.

## Severity Ladder

Five severities, [Nagios plugin convention][NAGIOS] extended with UNKNOWN:

| Code | Name    | Meaning                                                     |
| ---- | ------- | ----------------------------------------------------------- |
| 0    | OK      | Observed and matches expected                               |
| 1    | WARN    | Observed misconfiguration, recommended fix                  |
| 2    | CRIT    | Observed misconfiguration, critical                         |
| 3    | INFO    | Informational, no action needed (hardware, hostname, etc.)  |
| 4    | UNKNOWN | Could not determine, manual verification recommended        |

Two invariants:

- **OK requires positive evidence.** A check passes only when it has read a value and confirmed it matches the expected setting. Empty source never silently passes.
- **UNKNOWN is the default for empty source.** When `defaults read` returns nothing, when a CLI is missing, when a configuration profile may have overridden the legacy plist domain, the result is UNKNOWN. Not OK, not CRIT.

This makes a green run meaningful: every OK is backed by observation. UNKNOWN tells the user where to look manually.

## Output Contract

Each check writes `key:value` lines to stdout. Each `pass_<variable>:<code>` carries a severity. Display values (versions, lists, counts) appear as additional lines for the orchestrator to render alongside the result.

```text
version:14.5.1
days_old:32
pass_xprotect:0
```

Lines are independent; order does not matter. Values may contain colons (IPv6 addresses, status strings, hostnames with ports), so parsers must split on the *first* colon only and keep the rest as-is.

## Standard Pattern

Default `$UNKNOWN`, flip on observed evidence (good or bad). Two flips per setting in the simplest case.

### Bash

```sh
#!/bin/bash
# Source: URL

# Retrieve value
setting=$(
    defaults read com.example.plist Key 2>/dev/null
)

# Severity codes
OK=0; WARN=1; CRIT=2; INFO=3; UNKNOWN=4

pass_check=$UNKNOWN
[[ "$setting" == "expected" ]] && pass_check=$OK
[[ "$setting" == "bad-value" ]] && pass_check=$WARN

echo "pass_check:$pass_check"
```

### Python

```python
#!/usr/bin/env python3
"""Check whether a managed setting matches the expected value."""
import subprocess

OK, WARN, CRIT, INFO, UNKNOWN = 0, 1, 2, 3, 4

result = subprocess.run(
    ["defaults", "read", "com.example.plist", "Key"],
    capture_output=True, text=True,
).stdout.strip()

pass_check = UNKNOWN
if result == "expected":
    pass_check = OK
elif result == "bad-value":
    pass_check = WARN

print(f"pass_check:{pass_check}")
```

In both languages, the empty-source case is preserved (no `result or "0"` defaulting) so UNKNOWN remains distinguishable from a positively-observed value.

## Standalone Runnability

Each check script must be runnable on its own without sourcing a lib or being driven by the orchestrator:

```sh
./checks/filevault.sh
# → version:14.5
#   pass_filevault:0
```

This means severity constants are defined inside each check (or imported from a tiny single-purpose module), not from a shared style lib that may not be reachable. The duplication cost (a few lines per file) is the price for the property: any check is its own test harness.

The orchestrator-side helpers (color rendering, severity dispatch, summary counters) live in a separate lib that only the orchestrator sources. Checks know nothing about display.

## Probe Guarding

A check must not provoke an interactive installer or prompt. On macOS, `git --version` triggers the Xcode CLT GUI installer when CLT is absent. Guard external CLI invocations:

```sh
# Bash
git_version=""
if command -v git >/dev/null 2>&1 && xcode-select -p >/dev/null 2>&1; then
    git_version=$(git --version 2>/dev/null | awk '{print $3}')
fi
```

```python
# Python
import shutil

git_version = ""
if shutil.which("git") and subprocess.run(["xcode-select", "-p"], capture_output=True).returncode == 0:
    git_version = subprocess.run(["git", "--version"], capture_output=True, text=True).stdout.split()[-1]
```

The principle is language-agnostic: probe presence before invocation, treat absence as `pass_<tool>=$INFO` ("not installed, no action needed") rather than as a failure unless the check is specifically about the tool's installation.

## Orchestrator

The orchestrator runs each check, parses its output, dispatches severity codes to display, and accumulates counters. A minimal Bash sketch:

```sh
issues=0
unknowns=0

run() { "$DIR/$1.sh" 2>/dev/null; }
key() { echo "$data" | grep "^$1:" | cut -d: -f2-; }    # f2-, never f2

pass()    { printf "  ✓  %s (%s)\n" "$1" "$2"; }
warn()    { printf "  !  %s (%s)\n" "$1" "$2"; ((issues++)); }
fail()    { printf "  ✗  %s (%s)\n" "$1" "$2"; ((issues++)); }
info()    { printf "  ℹ  %s (%s)\n" "$1" "$2"; }
unknown() { printf "  ?  %s (%s)\n" "$1" "$2"; ((unknowns++)); }

check() {
    case "$1" in
        0) pass    "$2" "$3" ;;
        1) warn    "$2" "$4" ;;
        2) fail    "$2" "$4" ;;
        3) info    "$2" "$4" ;;
        4) unknown "$2" "Indeterminate" ;;
        *) unknown "$2" "Invalid code" ;;
    esac
}

data=$(run filevault)
check "$(key pass_filevault)" "FileVault" "Enabled" "Disabled"
```

Track `issues` and `unknowns` separately. Display them separately in the summary. UNKNOWN is not an issue (the user has not observed a misconfiguration), but it is not a clean pass either.

## Exit-Code Semantics

Two modes, an explicit flag for the second:

| Mode       | Behavior                                                                              |
| ---------- | ------------------------------------------------------------------------------------- |
| Default    | Always exit `0`. The issues counter is a visual cue for humans.                       |
| `--strict` | Exit `1` when `issues + unknowns > 0`. For CI gates and bootstrap scripts.            |

Preserve the `0` default. Many users invoke the orchestrator interactively and pipe through `tee` or `less`; flipping the default to non-zero would surprise existing users and break those flows. CI users opt in via `--strict`, which counts UNKNOWN as a failure because a CI gate cannot defer to a human for manual verification.

## Anti-Patterns

- **`${var:-0}` defaulting on a managed key.** Collapses the empty case (UNKNOWN) into a known value (CRIT). Never apply this pattern to keys that may live in a configuration profile.
- **Default severity = OK.** Inverts the safety polarity. Always default to UNKNOWN or the relevant failure severity, then flip to OK on positive match.
- **Sourcing the orchestrator's style lib from a check.** Breaks standalone runnability when the check is run from a different working directory.
- **Probing tools without `command -v`.** On a fresh machine the probe itself can trigger an installer prompt mid-audit.
- **Spawning a subprocess for pattern matching the language can do natively.** `grep` for substring detection in Bash; `subprocess.run` with `grep` in Python; both are the wrong layer.

## Why This Architecture

- **Standalone runnability**, every check is its own test harness; run it, read the `pass_*` lines.
- **Separation of concerns**, data and testing in the check, display in the orchestrator.
- **Honesty**, UNKNOWN means "we did not observe", OK means "we observed and it is good." Empty source must never silently pass.
- **Language portability**, the contract is text-based; any language that can print `key:value` to stdout participates.
- **Replaceability**, the orchestrator can be rewritten without touching any check.

[NAGIOS]: https://nagios-plugins.org/doc/guidelines.html#AEN78
[CHECKMAC]: https://github.com/N4M3Z/check-mac
