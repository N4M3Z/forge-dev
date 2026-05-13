#!/usr/bin/env bash
# Scan a dotfiles tree for secrets, aggregate per-dir-per-rule, and optionally
# filter flagged lines from shell-history files so the rest can be imported
# into atuin. Local-only; nothing leaves the machine.
#
# Usage:
#   audit-dotfiles.sh <path> [--filter-history]
#
# Output:
#   Aggregated "<count> <dir> <rule>" table on stdout.
#   When --filter-history is set, each flagged history file gets a sibling
#   <history>.clean with the leaked lines removed.
#
# Exit codes:
#   0 — no leaks found
#   1 — leaks found (report on stdout, optionally cleaned files written)
#   2 — usage error or missing dependencies
#
# Dependencies: gitleaks, yq (mikefarah's), awk, sed, sort, uniq

set -uo pipefail

target="${1:-}"
mode="${2:-}"

if [[ -z "${target}" || ! -d "${target}" ]]; then
    echo "usage: $(basename "$0") <path> [--filter-history]" >&2
    exit 2
fi

for cmd in gitleaks yq sed awk sort uniq; do
    if ! command -v "${cmd}" >/dev/null 2>&1; then
        echo "missing dependency: ${cmd}" >&2
        exit 2
    fi
done

if ! yq --version 2>&1 | grep -q mikefarah; then
    echo "wrong yq: need mikefarah's yq (brew install yq), got something else" >&2
    exit 2
fi

abs_target=$(cd "${target}" && pwd)
report=$(mktemp -t audit-dotfiles.XXXXXX.json)
trap 'rm -f "${report}"' EXIT

# gitleaks exits non-zero when leaks are found; that's a signal, not a failure
gitleaks detect --no-banner --redact --no-git \
    -s "${target}" \
    --report-format json --report-path "${report}" >/dev/null 2>&1 || true

leak_count=$(yq -p json '. | length' "${report}")

if [[ "${leak_count}" -eq 0 ]]; then
    echo "ok:audit-dotfiles (no leaks found in ${target})"
    exit 0
fi

rule_count=$(yq -p json '[.[].RuleID] | unique | length' "${report}")
echo "warn:audit-dotfiles (${leak_count} leaks across ${rule_count} rule types)"
echo
echo "  count  dir            rule"
echo "  -----  ---            ----"

# Strip the scan-root prefix and keep only the first surviving component
# (= the top-level subdir under ${target}). Per-dir-per-rule counts via uniq -c.
yq -p json -o tsv '.[] | [.File, .RuleID]' "${report}" \
    | awk -F'\t' -v prefix="${abs_target}/" '
        { sub("^" prefix, "", $1)
          split($1, parts, "/")
          print parts[1] "\t" $2
        }' \
    | sort | uniq -c \
    | awk '{printf "  %5d  %-14s %s\n", $1, $2, $3}'

if [[ "${mode}" != "--filter-history" ]]; then
    echo
    echo "  Re-run with --filter-history to emit cleaned shell-history files."
    exit 1
fi

echo
echo "  filtering flagged history files..."

# One awk pass groups findings by history file and builds a sed delete-list
# (Nd;Md;...) per file. Each file then gets one sed invocation.
yq -p json -o tsv '.[] | [.File, .StartLine]' "${report}" \
    | awk -F'\t' '
        $1 ~ /(history|zhistory)$/ {
            key = $1 "\t" $2
            if (!seen[key]++) {
                exprs[$1] = (exprs[$1] ? exprs[$1]";" : "") $2 "d"
                counts[$1]++
            }
        }
        END { for (f in exprs) print f "\t" exprs[f] "\t" counts[f] }' \
    | while IFS=$'\t' read -r hist expr removed; do
        sed -e "${expr}" "${hist}" > "${hist}.clean"
        kept=$(wc -l < "${hist}.clean")
        printf "  ok %s.clean (kept %d lines, removed %d)\n" \
            "${hist}" "${kept}" "${removed}"
    done

exit 1
