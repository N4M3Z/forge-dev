#!/usr/bin/env python3
"""Fetch failing PR checks, pull GitHub Actions logs, extract failure snippets.

Wraps `gh` CLI. Handles field drift across gh versions and falls back to the
job logs API when the run log is still in progress. Exits non-zero when any
failure remains so the script can be used in automation.

Usage:
    inspect_pr_checks.py [--repo DIR] [--pr PR] [--json]
                         [--max-lines N] [--context N]

Requires `gh` on PATH with repo + workflow scopes.
"""

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, asdict
from typing import Optional

RUN_ID_REGEX = re.compile(r"/actions/runs/(\d+)(?:/|$)")
JOB_ID_REGEX = re.compile(r"/actions/runs/\d+/job/(\d+)(?:/|$)")

PR_CHECKS_FIELDS_PRIMARY = "name,state,bucket,link,startedAt,completedAt,workflow"
PR_CHECKS_FIELDS_FALLBACK = "name,state,bucket,link"


@dataclass
class CheckFailure:
    name: str
    workflow: Optional[str]
    state: str
    details_url: Optional[str]
    run_id: Optional[str] = None
    run_status: Optional[str] = None
    run_conclusion: Optional[str] = None
    log_snippet: Optional[str] = None
    log_error: Optional[str] = None
    external: bool = False


def run_gh(args: list[str], cwd: str) -> tuple[int, str, str]:
    proc = subprocess.run(
        ["gh", *args], cwd=cwd, capture_output=True, text=True, check=False
    )
    return proc.returncode, proc.stdout, proc.stderr


def ensure_auth(cwd: str) -> None:
    code, _, err = run_gh(["auth", "status"], cwd)
    if code != 0:
        print(f"gh auth status failed: {err.strip()}", file=sys.stderr)
        sys.exit(2)


def resolve_pr(pr: Optional[str], cwd: str) -> str:
    if pr:
        return pr
    code, out, err = run_gh(["pr", "view", "--json", "number,url"], cwd)
    if code != 0:
        print(f"could not resolve current PR: {err.strip()}", file=sys.stderr)
        sys.exit(2)
    return str(json.loads(out)["number"])


def list_checks(pr: str, cwd: str) -> list[dict]:
    for fields in (PR_CHECKS_FIELDS_PRIMARY, PR_CHECKS_FIELDS_FALLBACK):
        code, out, err = run_gh(["pr", "checks", pr, "--json", fields], cwd)
        if code == 0:
            return json.loads(out)
        if "unknown field" not in err.lower():
            print(f"gh pr checks failed: {err.strip()}", file=sys.stderr)
            sys.exit(2)
    print("gh pr checks rejected all field sets", file=sys.stderr)
    sys.exit(2)


def parse_run_id(url: Optional[str]) -> Optional[str]:
    if not url:
        return None
    m = RUN_ID_REGEX.search(url)
    return m.group(1) if m else None


def tail_lines(text: str, max_lines: int, context: int) -> str:
    lines = text.splitlines()
    if not lines:
        return ""
    if len(lines) <= max_lines:
        return "\n".join(lines)
    # try to anchor on the last "error" occurrence
    last_error_idx = None
    for i in range(len(lines) - 1, -1, -1):
        if "error" in lines[i].lower():
            last_error_idx = i
            break
    if last_error_idx is None:
        return "\n".join(lines[-max_lines:])
    start = max(0, last_error_idx - context)
    end = min(len(lines), last_error_idx + context + 1)
    window = lines[start:end]
    if len(window) < max_lines:
        window = lines[max(0, end - max_lines):end]
    return "\n".join(window[:max_lines])


def fetch_run_log(run_id: str, cwd: str, max_lines: int, context: int) -> tuple[Optional[str], Optional[str]]:
    code, out, err = run_gh(["run", "view", run_id, "--log"], cwd)
    if code == 0 and out.strip():
        return tail_lines(out, max_lines, context), None
    # fallback: job log (find first job, pull its log via API)
    jcode, jout, jerr = run_gh(
        ["run", "view", run_id, "--json", "jobs"], cwd
    )
    if jcode != 0:
        return None, (err or jerr).strip()
    try:
        jobs = json.loads(jout).get("jobs", [])
    except json.JSONDecodeError:
        return None, "could not parse jobs JSON"
    for job in jobs:
        job_id = parse_run_id(job.get("url")) or None
        # job url pattern is /actions/runs/<run>/job/<job>
        m = JOB_ID_REGEX.search(job.get("url", ""))
        if m:
            job_id = m.group(1)
        if job_id and job.get("conclusion") == "failure":
            code, out, err = run_gh(
                ["api", f"/repos/{{owner}}/{{repo}}/actions/jobs/{job_id}/logs"],
                cwd,
            )
            if code == 0 and out.strip():
                return tail_lines(out, max_lines, context), None
            return None, err.strip()
    return None, "no failing job logs available"


def run_meta(run_id: str, cwd: str) -> tuple[Optional[str], Optional[str]]:
    code, out, _ = run_gh(
        ["run", "view", run_id, "--json", "status,conclusion"], cwd
    )
    if code != 0:
        return None, None
    data = json.loads(out)
    return data.get("status"), data.get("conclusion")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--pr", default=None)
    ap.add_argument("--json", dest="as_json", action="store_true")
    ap.add_argument("--max-lines", type=int, default=120)
    ap.add_argument("--context", type=int, default=20)
    args = ap.parse_args()

    ensure_auth(args.repo)
    pr = resolve_pr(args.pr, args.repo)
    checks = list_checks(pr, args.repo)

    failures: list[CheckFailure] = []
    for c in checks:
        bucket = (c.get("bucket") or c.get("state") or "").lower()
        if bucket not in ("fail", "cancel"):
            continue
        details_url = c.get("link")
        run_id = parse_run_id(details_url)
        failure = CheckFailure(
            name=c.get("name", "?"),
            workflow=c.get("workflow"),
            state=c.get("state", bucket),
            details_url=details_url,
            run_id=run_id,
            external=run_id is None,
        )
        if run_id:
            status, conclusion = run_meta(run_id, args.repo)
            failure.run_status = status
            failure.run_conclusion = conclusion
            snippet, err = fetch_run_log(
                run_id, args.repo, args.max_lines, args.context
            )
            failure.log_snippet = snippet
            failure.log_error = err
        failures.append(failure)

    if args.as_json:
        print(json.dumps([asdict(f) for f in failures], indent=2))
    else:
        if not failures:
            print(f"PR #{pr}: no failing checks")
            return 0
        print(f"PR #{pr}: {len(failures)} failing check(s)\n")
        for f in failures:
            print(f"— {f.name}" + (f" ({f.workflow})" if f.workflow else ""))
            print(f"  state: {f.state}")
            if f.external:
                print(f"  external check — only URL reported: {f.details_url}")
                continue
            print(f"  run: {f.run_id} status={f.run_status} conclusion={f.run_conclusion}")
            print(f"  url: {f.details_url}")
            if f.log_snippet:
                print("  log snippet:")
                for ln in f.log_snippet.splitlines():
                    print(f"    {ln}")
            elif f.log_error:
                print(f"  log unavailable: {f.log_error}")
            print()

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
