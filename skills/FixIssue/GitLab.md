## GitLab CLI Commands

Platform-specific commands for the FixIssue workflow using `glab` (GitLab CLI).

### Fetch issue (Step 1)

```bash
glab issue view N -R GROUP/PROJECT
```

For JSON output:

```bash
glab api projects/:id/issues/N
```

### Check existing work (Step 2)

```bash
# Open MRs for this project
glab mr list -R GROUP/PROJECT --search "N"

# Check issue assignees
glab issue view N -R GROUP/PROJECT
```

### Create linked branch (Step 4)

```bash
# Create an MR linked to the issue (creates branch + draft MR)
glab mr create --related-issue N -R GROUP/PROJECT --draft --target-branch main

# Manual branch creation (fallback)
git checkout -b fix/<slug>
```

The `--related-issue` flag links the MR to the issue in GitLab's UI.

### Create MR (Step 6)

**Same-project fix:**

```bash
glab mr create -R GROUP/PROJECT \
    --title "fix: <description>" \
    --description "$(cat <<'EOF'
## Summary
- <what changed and why>

Closes #N

## Test plan
- [ ] <test step>
EOF
)" \
    --target-branch main
```

`Closes #N` auto-closes the issue when the MR merges (same-project only).

**Cross-project fix:**

```bash
glab mr create -R GROUP/FIX_PROJECT \
    --title "fix: <description>" \
    --description "$(cat <<'EOF'
## Summary
- <what changed and why>

Closes GROUP/ISSUE_PROJECT#N

## Test plan
- [ ] <test step>
EOF
)" \
    --target-branch main
```

### Close cross-project issue (Step 7)

```bash
glab issue close N -R GROUP/ISSUE_PROJECT
glab issue note N -R GROUP/ISSUE_PROJECT -m "Fixed by GROUP/FIX_PROJECT!MR_N"
```

Note: GitLab uses `!N` for MR references (not `#N` which is for issues).

### Quick Reference

| Command | Purpose |
|---------|---------|
| `glab issue view N -R GROUP/PROJECT` | Read issue details |
| `glab issue list -R GROUP/PROJECT --label bug` | Find issues by label |
| `glab issue close N` | Close issue |
| `glab issue note N -m "message"` | Comment on issue |
| `glab mr create` | Create merge request |
| `glab mr create --related-issue N` | Create MR linked to issue |
| `glab mr list` | List merge requests |
| `glab mr view N` | Read MR details |
| `glab mr merge N` | Merge MR |
| `glab mr diff N` | View MR changes |
| `glab mr approve N` | Approve MR |
| `glab repo view GROUP/PROJECT` | Check repo exists |

### Auto-Close Keywords

These keywords in an MR description auto-close the referenced issue **when the MR merges into the default branch of the same project**:

`Close`, `Closes`, `Closed`, `Closing`, `close`, `closes`, `closed`, `closing`
`Fix`, `Fixes`, `Fixed`, `Fixing`, `fix`, `fixes`, `fixed`, `fixing`
`Resolve`, `Resolves`, `Resolved`, `Resolving`, `resolve`, `resolves`, `resolved`, `resolving`
`Implement`, `Implements`, `Implemented`, `Implementing`, `implement`, `implements`, `implemented`, `implementing`

Cross-project: does NOT auto-close. Always close manually.

### GitLab vs GitHub Terminology

| GitHub | GitLab | Reference syntax |
|--------|--------|-----------------|
| Pull Request (PR) | Merge Request (MR) | `#N` (issue), `!N` (MR) |
| Repository | Project | `GROUP/PROJECT` |
| Organization | Group/Namespace | `GROUP/SUBGROUP/PROJECT` |
| `gh` | `glab` | -- |
