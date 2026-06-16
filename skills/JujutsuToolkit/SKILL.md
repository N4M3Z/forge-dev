---
name: JujutsuToolkit
version: 0.1.0
description: "Jujutsu (jj) as a colocated VCS front-end over git for AI-agent work: colocate strategy, git-hook-tool coexistence (Entire, gitleaks, safety-net), parallel agents via jj workspaces, op-log recovery, provisioning. USE WHEN colocating a repo with jj git init --colocate, deciding whether jj coexists with Entire / gitleaks / safety-net or other git-hook tooling, isolating parallel agents with jj workspace, recovering jj state with jj undo or op restore, or debugging jj-and-git interaction. For commit and push discipline see VersionControl's Jujutsu companion; for commands see the jj tldr."
sources:
    - https://docs.jj-vcs.dev/latest/
    - https://docs.jj-vcs.dev/latest/git-compatibility/
    - https://docs.jj-vcs.dev/latest/config/
    - https://steveklabnik.github.io/jujutsu-tutorial/
---

# JujutsuToolkit

Jujutsu (jj) run colocated over an existing git repo, the version-control front-end for multi-agent dev work. The working copy is an auto-snapshotted commit, so there is no index for concurrent sessions to collide on, and signing is deferred to push. Decision and rationale: `docs/decisions/ARCH-0032` (forge-provision). Command reference: `docs/tldrs/jujutsu.md`. Commit and push discipline: forge-core VersionControl's `Jujutsu.md` companion. This skill covers colocation, tool coexistence, parallel agents, and recovery.

## Colocate strategy

`jj git init --colocate` puts `.jj/` beside `.git/` and syncs them on every jj command. That is the load-bearing choice: git tooling keeps working (gh, gitui, revdiff, tuicr, the IDE, Claude Code repo detection) while jj drives the model. A non-colocated repo hides git inside `.jj/repo/store/git` and blinds all of it, so always colocate.

The one rule: drive mutations through jj; treat raw git as read-only. Colocated git sits in detached HEAD (jj parks it), and interleaving jj and git writes is the only way to produce conflicting refs. Reads (`git log`, `git status`, `git diff`, blame, the review TUIs) are always safe. Before a rare mutating git command, run `git switch <branch>` first.

`.jj/` is local-only and never pushed; the remote sees ordinary git. Colocation is reversible: move `.jj/` aside (`rm -rf` is guarded by the dangerous-command hook) and the git repo is untouched.

## Compatibility with git-hook tools

jj runs no git hooks. Any tool whose behavior rides on git hooks is bypassed for jj-driven commits. This is not damage, an uncalled hook is inert, but it moves where the work happens.

- **Entire.** Its session capture runs off Claude Code hooks (Task / TodoWrite / session events), which are VCS-agnostic and keep working under jj. Only its git hooks (`prepare-commit-msg` / `commit-msg` trailer injection, `post-commit` condense, `post-rewrite` remap, `pre-push` log shipping) are skipped. Under a squash-merge plus `push_sessions: false` workflow that linkage is already moot. jj support in Entire's hook layer is upstream's to add; do not work around it here. See `docs/decisions/ARCH-0028`.
- **gitleaks and safety-net.** Both of VersionControl's commit-time secret gates ride git hooks (gitleaks via `.githooks/pre-commit`; safety-net intercepts `git commit`, which jj never calls), so both bypass under jj. forge modules relocate the gate automatically: `make install` wires a repo-local jj `push` alias to `.githooks/jj-push`, which runs `prek run --all-files --stage pre-push` then `jj git push`. Push with `jj push`; details in VersionControl's `Jujutsu.md`.

General rule: under jj, a git-hook-based check becomes a pre-push check (run by the `jj push` alias) or a CI check. For strict isolation across parallel jj workspaces, `jj-hp` (the `jj-hooks` crate) runs the same hooks in an ephemeral worktree and is the escalation path.

## Parallel agents

Multiple agents editing one working copy still collide at the file level; jj only removes the index collision. Give each agent its own working copy sharing one store: `jj workspace add ../repo-agent-1` creates an isolated directory and `@` backed by the same history and op log. This is the jj-native replacement for the git-worktree lifecycle (no manual create / rebase / remove / delete-branch). Companions: `jj workspace list`, `jj workspace forget`.

## Recovery

Every jj operation is recorded in the op log. `jj undo` reverses the last one; `jj op log` browses the history; `jj op restore <id>` rolls the whole repo back to any prior state, including a botched agent edit or rebase. `revsets.immutable-heads` (default `trunk() | tags() | untracked_remote_bookmarks()`) blocks rewriting published history, so an agent cannot accidentally rewrite trunk.

## Provisioning

Installed via the Brewfile (`brew "jj"`, binary `jj`) and configured globally by `scripts/configure/jujutsu.sh` (forge-provision), which reads identity and the signing key from `git config` and sets `signing.behavior=drop` plus `git.sign-on-push=true`. Verify with `jj config list --user`.

## Common pitfalls

| Symptom | Cause / Fix |
|---|---|
| A jj or git mutation ran in the wrong repo | The harness resets cwd to the project root each call. Use absolute paths, `jj -R <path>`, `git -C <path>`, and verify `pwd` before any mutating command. |
| `gh` / IDE shows detached HEAD | Normal when colocated. `git switch <branch>` only before a mutating git command. |
| A `git commit` appears to do nothing | jj owns mutations; the change is already in `@`. Commit through jj, not git. |
| A file watcher (Vite, test runner) thrashes | It is watching `.jj/`. Exclude `.jj/` from the watcher. |
| Large file refused on snapshot | `snapshot.max-new-file-size` defaults to 1MiB; raise it per-repo. No Git LFS support. |
| Entire stopped tagging commits | Expected: jj skips git hooks. Capture (Claude Code hooks) is unaffected; the linkage trailer is moot under squash-merge. |
