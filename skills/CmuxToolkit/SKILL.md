---
name: CmuxToolkit
version: 0.1.0
description: "Drive cmux from its Unix-socket CLI: open a new split, pane, or tab and run a command in it by sending text and keys, build declarative layouts, render a diff in the native viewer, and resolve window / workspace / pane / surface handles. USE WHEN opening tuicr or any command in a new cmux pane, splitting the current pane from the CLI, sending commands or keys to another surface, watching logs in a side pane, showing a diff in cmux, or scripting cmux layouts. For app config, persistence, and hooks see the cmux tldr."
sources:
    - https://raw.githubusercontent.com/manaflow-ai/cmux/main/docs/cli-contract.md
    - https://cmux.com/docs/api
    - https://github.com/manaflow-ai/cmux
---

# CmuxToolkit

cmux is controlled through a Unix-socket CLI that addresses a tree of windows > workspaces > panes > surfaces. The headline capability for an agent: **open new panes and drive them by sending terminal commands**, so a review TUI, a log tail, a dev server, or any command runs in its own split beside your work. App setup, config, persistence, and Claude Code hooks live in the cmux tldr.

The binary is `cmux`, installed and symlinked into `~/.local/bin` by the provisioning module.

## Open a pane and run a command in it

`new-split` and `new-pane` create an empty terminal but do NOT accept a command, so it is two steps: spawn the pane, capture its surface ref, then `send` the command line. `send` types text into the surface; only `\n` (or `\r`) presses Enter, so without it the command sits unrun.

```sh
surf=$(cmux new-split right --focus true | grep -oE 'surface:[0-9]+')
cmux send --surface "$surf" "cd /path/to/repo && tuicr -r 'main@origin..my-bookmark'\n"
```

Spawn as many panes as you like and send each its own commands, building a live layout (review here, logs there, a shell over there). Send more lines anytime to the same ref; interrupt or submit with `send-key`.

| Action                                   | Command                                                         |
| ---------------------------------------- | --------------------------------------------------------------- |
| Split the current pane (returns the ref) | `cmux new-split <direction> [--focus true]`                     |
| New terminal or browser pane             | `cmux new-pane [--type terminal/browser] [--direction <dir>]`   |
| New tab that runs a command immediately  | `cmux new-workspace --cwd <dir> --command "<cmd>" [--name <t>]` |
| Run a command in a surface               | `cmux send --surface <ref> "<cmd>\n"`                           |
| Send one key (submit, interrupt)         | `cmux send-key --surface <ref> <key>` (`enter`, `ctrl+c`)       |

Escape sequences for `send`: `\n` / `\r` = Enter, `\t` = Tab. Only `new-workspace` accepts `--command` directly; `new-split` / `new-pane` need the `send` follow-up. A new split inherits the caller's cwd, so prefix the sent command with `cd <dir> &&`. `send-panel` / `send-key-panel` are the panel-targeted variants.

## Targeting surfaces

Every pane is a surface. cmux injects three env vars per pane: `CMUX_SURFACE_ID` (this pane), `CMUX_WORKSPACE_ID` (this tab), `CMUX_SOCKET_PATH` (the control socket). Targets accept a UUID, a short ref (`surface:30`, `workspace:9`, `tab:2`), or an index; output prints refs by default. With no `--surface`, a command acts on the caller's own pane, so always pass the ref captured from `new-split` when driving a different one.

| Command                | Effect                                                       |
| ---------------------- | ------------------------------------------------------------ |
| `cmux tree --all`      | Print the full window / workspace / pane / surface tree      |
| `cmux identify --json` | Report the caller's own window / workspace / surface context |
| `cmux list-panes`      | List panes in a workspace                                    |
| `cmux top`             | Per-surface process and resource usage                       |
| `cmux move-surface`    | Move a surface to another pane, workspace, window, or index  |
| `cmux split-off`       | Move a surface into a new split without stealing focus       |
| `cmux notify`          | Post a notification to a workspace or surface                |
| `cmux events`          | Stream cmux events as newline-delimited JSON (reconnectable) |

## Declarative layouts

For a fixed multi-pane arrangement, pass `--layout` (inline JSON, same schema as `cmux.json` `commands[]`) instead of `--command`. Surfaces are leaves with `type` (`terminal` / `browser`) and optional `command`, `cwd`, `url`, `env`; splits nest via `direction`, `split` (0.0-1.0 ratio), and `children`:

```sh
cmux new-workspace --name Review --layout '{"direction":"horizontal","split":0.5,"children":[
  {"pane":{"surfaces":[{"type":"terminal","command":"tuicr -w","cwd":"/repo"}]}},
  {"pane":{"surfaces":[{"type":"terminal","command":"jj log"}]}}]}'
```

Structural templates reference no versions or APIs, so they survive cmux updates. The same recipes live in `cmux.json` `commands[]`, invokable from the Command Palette (see the cmux tldr).

## Native diff viewer

`cmux diff` renders a unified diff in a read-only browser split. It reads piped stdin, so any diff source works, and also has git-native sources:

```sh
jj diff -r @- --git | cmux diff --title "diff" --layout split --focus true
git diff | cmux diff
cmux diff --branch --base main --cwd /repo        # or --unstaged / --staged / --last-turn
```

Options: `--source <unstaged|staged|branch|last-turn>` (or the matching flags), `--base <ref>`, `--cwd/--repo <path>`, `--layout <split|unified>`, `--font-size <pt>`, `--title`, `--focus`. It requires the cmux browser enabled (`cmux enable-browser`), failing `browser_disabled` otherwise. For an interactive, annotatable review, prefer a TUI (`tuicr` / `revdiff`) in a `new-split` pane.

## Gotchas

| Symptom                                         | Cause / Fix                                                                                           |
| ----------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| `Failed to connect to socket ... not permitted` | The agent command sandbox blocks the cmux Unix socket. Run cmux CLI commands with the sandbox lifted. |
| `cmux --help` omits the pane / window verbs     | It is truncated. Use `cmux docs api` and the cli-contract for the authoritative command list.         |
| `cmux diff` fails `browser_disabled`            | The browser is off. `cmux enable-browser` first, or run a TUI in a `new-split` pane instead.          |
| `send` lands in the wrong pane                  | The default target is the caller's own surface. Pass `--surface <ref>` captured from `new-split`.     |
| The sent command runs in the wrong directory    | Splits inherit the caller's cwd. Prefix with `cd <dir> &&`, or use `new-workspace --cwd`.             |
| Text was sent but nothing ran                   | Missing the trailing `\n`. `send` types text; only `\n` / `\r` submits it.                            |
