---
name: StatusLine
version: 0.1.0
description: "Manage the Claude Code statusline — install ccline, switch themes, toggle segments, preview, or revert to custom script. USE WHEN statusline, status line, ccline, change theme, configure statusline, statusline setup."
---

# StatusLine

Manage the Claude Code statusline. Covers CCometixLine (ccline) installation, theme switching, segment toggling, and fallback to the custom bash script.

## Workflow Routing

| Workflow | Trigger | Section |
|----------|---------|---------|
| **Install** | "install ccline", "set up statusline" | [Install](#install) |
| **Theme** | "switch theme", "change theme", "list themes" | [Theme](#theme) |
| **Segments** | "toggle segment", "enable cost", "disable git" | [Segments](#segments) |
| **Preview** | "preview statusline", "test statusline" | [Preview](#preview) |
| **Switch** | "use ccline", "use old script", "revert statusline" | [Switch](#switch) |

## Architecture

Two statusline backends are available:

| Backend | Config | Pros |
|---------|--------|------|
| **ccline** | `~/.claude/ccline/config.toml` | Themes, segments, Nerd Font icons, TOML config |
| **Custom script** | `~/.claude/statusline-command.sh` | Matches p10k Pure, chains safety-net, full control |

Both are configured via `~/.claude/settings.json`:

```json
"statusLine": {
    "type": "command",
    "command": "ccline"
}
```

## ccline Reference

Binary: `~/.local/bin/ccline` (symlinked from bun global install).

| Flag | Purpose |
|------|---------|
| `ccline --help` | Usage |
| `ccline --config` | Interactive TUI (requires real TTY — does not work inside Claude Code) |
| `ccline --theme <name>` | Set theme |
| `ccline --print` | Print current config |
| `ccline --check` | Validate config |
| `ccline --init` | Regenerate default config and themes |
| `ccline --update` | Check for updates |

### Available Segments

| Segment ID | What it shows | Default |
|------------|---------------|---------|
| `model` | Claude model name | enabled |
| `directory` | Current working directory | enabled |
| `git` | Branch, dirty status, ahead/behind | enabled |
| `context_window` | Context usage percentage | enabled |
| `usage` | Token counts (requires API key) | disabled |
| `cost` | Session cost | disabled |
| `session` | Session elapsed time | disabled |
| `output_style` | Current output style | disabled |

### Available Themes

Themes are TOML files in `~/.claude/ccline/themes/`. Run `ccline --init` to regenerate defaults.

| Theme | Style |
|-------|-------|
| `default` | Plain separators, basic colors |
| `cometix` | Author's custom palette |
| `minimal` | Stripped down |
| `gruvbox` | Gruvbox color scheme |
| `nord` | Nord color scheme |
| `powerline-dark` | Dark Powerline arrows (Nerd Font required) |
| `powerline-light` | Light Powerline arrows (Nerd Font required) |
| `powerline-rose-pine` | Rose Pine Powerline |
| `powerline-tokyo-night` | Tokyo Night Powerline |

---

## Install

1. Check if ccline is already installed: `ccline --version`
2. If missing, install via bun: `/Users/N4M3Z/.bun/bin/bun install -g @cometix/ccline`
3. If bun hits `PermissionDenied`, the sandbox is blocking global installs. Retry with `dangerouslyDisableSandbox: true` and suggest adding `bun` to `sandbox.excludedCommands` in `~/.claude/settings.json`:
   ```json
   "sandbox": {
       "excludedCommands": ["bun"]
   }
   ```
4. The npm wrapper may fail to find the binary. Symlink it directly:
   ```bash
   ln -sf ~/.bun/install/global/node_modules/@cometix/ccline-darwin-arm64/ccline ~/.local/bin/ccline
   ```
5. Initialize config: `ccline --init`
6. Update `~/.claude/settings.json` to use ccline (this file is sandbox-protected — the user must edit it manually or approve the edit):
   ```json
   "statusLine": {
       "type": "command",
       "command": "ccline"
   }
   ```
7. Verify: `ccline --check`

---

## Theme

1. List available themes:
   ```bash
   ls ~/.claude/ccline/themes/
   ```
2. Show current theme: read line 1 of `~/.claude/ccline/config.toml` (`theme = "..."`)
3. To switch, edit `~/.claude/ccline/config.toml` line 1:
   ```toml
   theme = "nord"
   ```
4. Powerline themes require a Nerd Font in the terminal. Ask the user before switching to a powerline theme.
5. Preview the result using the [Preview](#preview) workflow.

---

## Segments

1. Read `~/.claude/ccline/config.toml` to find the `[[segments]]` blocks.
2. Each segment has:
   - `id` — segment identifier (see table above)
   - `enabled` — `true` or `false`
   - `[segments.icon]` — plain and nerd_font glyphs
   - `[segments.colors.icon]` and `[segments.colors.text]` — c16 color codes
   - `[segments.options]` — segment-specific settings
3. To toggle a segment, edit its `enabled` field.
4. To reorder segments, move the entire `[[segments]]` block (from `[[segments]]` to the next `[[segments]]`).
5. Preview the result using the [Preview](#preview) workflow.

---

## Preview

`ccline --config` TUI does not work inside Claude Code (no TTY). Instead, pipe sample JSON:

```bash
echo '{"model":{"id":"claude-opus-4-6","display_name":"Claude Opus 4.6"},"workspace":{"current_dir":"'"$PWD"'"},"context_window":{"used_percentage":42.5},"transcript_path":"/tmp/test"}' | ccline
```

Compare before/after when making changes.

---

## Switch

To switch between backends, edit the `statusLine.command` in `~/.claude/settings.json`:

| Backend | Command value |
|---------|---------------|
| ccline | `"ccline"` |
| Custom script | `"bash /Users/N4M3Z/.claude/statusline-command.sh"` |

The custom script is preserved at `~/.claude/statusline-command.sh` regardless of which backend is active.

---

## Constraints

- `~/.claude/settings.json` is sandbox-protected — edits require user approval or manual editing.
- `ccline --config` TUI requires a real TTY. Always use the pipe-based [Preview](#preview) instead.
- Powerline themes require Nerd Font glyphs — confirm terminal font before enabling.
- The bun global install path (`~/.bun/install/global/`) is not in PATH by default. The symlink at `~/.local/bin/ccline` is the stable entry point.
- When updating ccline (`bun install -g @cometix/ccline`), re-run the symlink step — bun may install a new binary path.
