## GitHub CLI Commands

Platform-specific commands for the FixIssue workflow using `gh` (GitHub CLI).

### Fetch issue (Step 1)

```bash
gh issue view N -R OWNER/REPO --json title,body,labels,state,comments,assignees
```

### Check existing work (Step 2)

```bash
# Open PRs referencing this issue
gh pr list -R OWNER/REPO --search "is:open N" --json number,title,headRefName

# Check assignees
gh issue view N -R OWNER/REPO --json assignees
```

### Create linked branch (Step 4)

```bash
# Creates a branch linked to the issue in GitHub's UI
gh issue develop N -R OWNER/REPO --checkout --name fix/<slug>

# Cross-repo: branch in the fix repo, linked to the issue repo
gh issue develop N -R OWNER/ISSUE_REPO --checkout --name fix/<slug> --branch-repo OWNER/FIX_REPO
```

### Create PR (Step 6)

**Same-repo fix:**

```bash
gh pr create -R OWNER/REPO \
    --title "fix: <description>" \
    --body "$(cat <<'EOF'
## Summary
- <what changed and why>

Fixes #N

## Test plan
- [ ] <test step>
EOF
)"
```

`Fixes #N` auto-closes the issue when the PR merges (same-repo only).

**Cross-repo fix:**

```bash
gh pr create -R OWNER/FIX_REPO \
    --title "fix: <description>" \
    --body "$(cat <<'EOF'
## Summary
- <what changed and why>

Fixes OWNER/ISSUE_REPO#N

## Test plan
- [ ] <test step>
EOF
)"
```

`Fixes OWNER/ISSUE_REPO#N` creates a visible link but does NOT auto-close across repos.

### Close cross-repo issue (Step 7)

```bash
gh issue close N -R OWNER/ISSUE_REPO \
    -c "Fixed by OWNER/FIX_REPO#PR_N"
```

### Quick Reference

| Command | Purpose |
|---------|---------|
| `gh issue view N -R OWNER/REPO` | Read issue details |
| `gh issue list -R OWNER/REPO --label bug` | Find issues by label |
| `gh issue develop N --checkout` | Create linked branch |
| `gh issue close N -c "message"` | Close with comment |
| `gh pr create` | Create pull request |
| `gh pr list --search "N"` | Find related PRs |
| `gh pr view N` | Read PR details |
| `gh pr merge N` | Merge PR |
| `gh pr checks N` | Check CI status |
| `gh repo view OWNER/REPO` | Check repo exists |

### Auto-Close Keywords

These keywords in a PR body auto-close the referenced issue **when the PR merges into the default branch of the same repo**:

`close`, `closes`, `closed`, `fix`, `fixes`, `fixed`, `resolve`, `resolves`, `resolved`

Cross-repo: creates a link, does NOT auto-close. Always close manually.
