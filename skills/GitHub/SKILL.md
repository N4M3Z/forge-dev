---
name: GitHub
version: 0.2.0
description: "GitHub CLI reference — repo management, releases, Actions/CI, PR operations, branch protection, labels. USE WHEN github, gh, repo, release, actions, ci, workflow, branch protection, labels, milestones."
---

# GitHub

@GitHubActions.md

General-purpose GitHub CLI (`gh`) reference for operations not covered by other skills. Always use `rtk gh` when available for token savings (see /RTK).

## Skill Map

| Operation | Skill | Don't duplicate here |
|-----------|-------|---------------------|
| Issue triage → fix → PR → close | /FixIssue | Issue commands, PR creation templates |
| Commit messages, staging, push, governance | /VersionControl | Commit conventions, staging, rulesets, CODEOWNERS |
| Token-optimized `gh` wrappers | /RTK | `rtk gh pr view`, `rtk gh run list`, etc. |
| Plugin marketplace publishing | /Publish | `gh release create` for plugins |
| Everything else | **This skill** | Repo ops, releases, CI, PR mgmt, branches, labels, API |

## Repository Management

### Create

```bash
gh repo create OWNER/NAME --public --description "Description"
gh repo create OWNER/NAME --private --clone   # create + clone locally
```

### Visibility

```bash
gh repo edit OWNER/REPO --visibility public --accept-visibility-change-consequences
gh repo edit OWNER/REPO --visibility private --accept-visibility-change-consequences
```

### Metadata

```bash
gh repo edit OWNER/REPO --description "New description"
gh repo edit OWNER/REPO --add-topic forge,rust,cli
gh repo edit OWNER/REPO --remove-topic old-topic
gh repo edit OWNER/REPO --homepage "https://example.com"
```

### Fork and clone

```bash
gh repo fork OWNER/REPO --clone    # fork + clone locally
gh repo clone OWNER/REPO           # clone without forking
```

### Archive and delete

```bash
gh repo archive OWNER/REPO         # read-only archive (reversible)
gh repo delete OWNER/REPO --yes    # destructive — confirm with user first
```

### Settings

```bash
gh repo edit OWNER/REPO --enable-issues --enable-wiki=false
gh repo edit OWNER/REPO --enable-squash-merge --enable-rebase-merge
gh repo edit OWNER/REPO --delete-branch-on-merge
gh repo edit OWNER/REPO --default-branch main
```

## Releases & Tags

### Create a release

```bash
gh release create v1.0.0 --title "v1.0.0" --notes "Release notes here"
gh release create v1.0.0 --generate-notes      # auto-generate from commits
gh release create v1.0.0 --draft                # draft, not published
gh release create v1.0.0 --prerelease           # mark as pre-release
gh release create v1.0.0 ./artifact.tar.gz      # attach files
```

### List and view

```bash
gh release list -R OWNER/REPO
gh release view v1.0.0 -R OWNER/REPO
```

### Delete

```bash
gh release delete v1.0.0 --yes                  # destructive — confirm first
gh release delete-asset v1.0.0 artifact.tar.gz   # remove single asset
```

### Tags without releases

```bash
git tag -a v1.0.0 -m "Version 1.0.0"
git push origin v1.0.0
```

## Actions & CI

### Monitor runs

```bash
gh run list                          # recent workflow runs
gh run list --workflow build.yml     # filter by workflow
gh run list --branch main            # filter by branch
gh run view RUN_ID                   # detailed run info
gh run view RUN_ID --log             # full logs
gh run view RUN_ID --log-failed      # only failed step logs
```

### Interact with runs

```bash
gh run cancel RUN_ID                 # cancel in-progress run
gh run rerun RUN_ID                  # rerun all jobs
gh run rerun RUN_ID --failed         # rerun only failed jobs
gh run watch RUN_ID                  # live tail (blocks)
```

### Trigger workflows

```bash
gh workflow run build.yml                              # trigger default branch
gh workflow run build.yml --ref feature-branch         # trigger specific branch
gh workflow run build.yml -f param=value               # with inputs
```

### List workflows

```bash
gh workflow list                     # all workflows
gh workflow view build.yml           # workflow details
gh workflow enable build.yml         # enable disabled workflow
gh workflow disable build.yml        # disable workflow
```

## Pull Request Operations

PR *creation* is in /FixIssue. This section covers PR *management* after creation.

### Merge strategies

```bash
gh pr merge PR_NUM --squash          # squash and merge (single commit)
gh pr merge PR_NUM --rebase          # rebase and merge (linear history)
gh pr merge PR_NUM --merge           # merge commit (preserves branch history)
gh pr merge PR_NUM --auto            # merge when checks pass
gh pr merge PR_NUM --delete-branch   # delete branch after merge
```

### Review workflow

```bash
gh pr review PR_NUM --approve
gh pr review PR_NUM --request-changes --body "Feedback here"
gh pr review PR_NUM --comment --body "Non-blocking note"
gh pr edit PR_NUM --add-reviewer user1,user2
```

### PR state management

```bash
gh pr ready PR_NUM                   # mark draft as ready for review
gh pr close PR_NUM                   # close without merging
gh pr reopen PR_NUM                  # reopen closed PR
gh pr edit PR_NUM --title "New title" --body "Updated description"
gh pr edit PR_NUM --add-label bug --add-assignee user1
```

### Checks and diff

```bash
gh pr checks PR_NUM                  # CI status
gh pr diff PR_NUM                    # view diff
gh pr view PR_NUM --json files -q '.files[].path'  # list changed files
```

## Branch Management

### List and delete

```bash
gh api repos/OWNER/REPO/branches --jq '.[].name'     # list all branches
git push origin --delete branch-name                   # delete remote branch
```

### Branch protection (legacy API)

For rulesets, CODEOWNERS, and bypass actors see /VersionControl GitHub companion.

```bash
# View legacy protection rules (returns 404 if only rulesets are configured)
gh api repos/OWNER/REPO/branches/main/protection

# Set protection (requires admin)
gh api repos/OWNER/REPO/branches/main/protection \
    --method PUT \
    --input - <<'EOF'
{
    "required_status_checks": {
        "strict": true,
        "contexts": ["ci/build"]
    },
    "enforce_admins": false,
    "required_pull_request_reviews": {
        "required_approving_review_count": 1
    },
    "restrictions": null
}
EOF

# Remove protection
gh api repos/OWNER/REPO/branches/main/protection --method DELETE
```

## Labels & Milestones

### Labels

```bash
gh label create "bug" --description "Something isn't working" --color E11D48
gh label create "enhancement" --color 2563EB
gh label edit "bug" --new-name "bug-fix" --color FF0000
gh label delete "old-label" --yes
gh label list -R OWNER/REPO
```

### Milestones

```bash
gh api repos/OWNER/REPO/milestones --method POST \
    -f title="v2.0" -f description="Next major release" -f due_on="2026-06-01T00:00:00Z"

gh api repos/OWNER/REPO/milestones --jq '.[] | "\(.number)\t\(.title)\t\(.open_issues)/\(.closed_issues)"'
```

### Filter issues by milestone/label

```bash
gh issue list --milestone "v2.0"
gh issue list --label "bug" --label "priority"
gh issue list --assignee "@me"
```

## API Patterns

For operations without dedicated `gh` subcommands, use `gh api` directly.

### REST

```bash
gh api repos/OWNER/REPO                                  # repo details
gh api repos/OWNER/REPO/contributors --jq '.[].login'    # contributors
gh api user                                               # authenticated user
```

### GraphQL

```bash
gh api graphql -f query='
  query {
    repository(owner: "OWNER", name: "REPO") {
      issues(first: 10, states: OPEN) {
        nodes { number title }
      }
    }
  }
'
```

### Pagination

```bash
gh api repos/OWNER/REPO/issues --paginate --jq '.[].title'
```

### JSON filtering

```bash
gh repo view OWNER/REPO --json name,visibility,defaultBranchRef -q '.visibility'
gh pr list --json number,title,headRefName -q '.[] | "\(.number)\t\(.title)"'
```

## Constraints

- **Public messages**: Use AskUserQuestion before posting comments, closing issues, or creating PRs with public-facing text (same rule as /FixIssue)
- **Destructive operations**: Confirm with user before `repo delete`, `release delete`, `branch --delete`, or visibility changes
- **Token optimization**: Use `rtk gh` for supported commands — see /RTK for the full list and savings
- **Commit conventions**: Follow /VersionControl for commit messages, staging, and push policy
- **Issue workflow**: Use /FixIssue for the full issue → fix → PR → close pipeline — don't reinvent it here
