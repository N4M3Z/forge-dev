---
name: WebDevelopment
version: 0.1.0
description: "Server-rendered web dashboards and apps in Rust using axum + htmx + Askama + rust-embed. USE WHEN building a web dashboard, adding a web UI to a CLI tool, server-rendered HTML, htmx partials, Askama templates, axum routes, embedded static assets, localhost webserver."
allowed-tools: Read, Bash, Write, Edit
upstream: https://github.com/ercan-er/htmx-claude-skill/blob/main/skill/skills.md
---

# WebDevelopment

Server-rendered web applications in Rust. Single binary, no client-side framework, no build step.

## Stack

| Layer | Tool | Role |
|---|---|---|
| Server | axum | HTTP routing, middleware, shared state |
| Templates | Askama | Compile-time HTML templates (Jinja2 syntax) |
| Interactivity | htmx | HTML-attribute-driven partial page updates |
| Static assets | rust-embed | Compile CSS/JS into the binary |

## Related Skills

- **DesignFrontend** (forge-core): aesthetic direction, typography, color, motion
- **HtmlPlayground** (forge-core): single-file HTML demos without a server
- **DataExplorer**: static HTML data apps with charts and tables
- **DataVisualization**: chart library selection
- **RustDevelopment**: crate structure, error handling, CLI patterns

## Architecture

1. Feature-gate the web server behind a Cargo feature. Keep tokio out of the default build.
2. Tokio runtime lives only in the subcommand entry point. Data-layer functions stay sync; handlers call `spawn_blocking`.
3. Bind `127.0.0.1` only, random ephemeral port. Validate Host header to block DNS rebinding.
4. Vendor all JS via rust-embed. No CDN, no runtime network fetches.
5. Askama templates extend a base layout. Tabs via full-page loads; detail panes via htmx partials.
6. Server returns HTML fragments, not JSON. Detect htmx requests via `HX-Request` header.
7. Use correct `hx-swap` strategy per UI intention. Avoid replacing large containers unnecessarily.

## Companions

| Topic | File |
|---|---|
| htmx attributes, swap modes, patterns, anti-patterns | [`Htmx.md`](Htmx.md) |
| Askama template syntax, compile-time gotchas | [`Askama.md`](Askama.md) |
| axum routes, rust-embed handler, security | [`Axum.md`](Axum.md) |
| Dark dashboard CSS patterns | [`VercelStyle.md`](VercelStyle.md) |

## Constraints

- Server returns HTML, not JSON. No client-side DOM building.
- No client-side JS frameworks. htmx handles interactivity.
- No Node.js build step. Templates compile with Rust. CSS is hand-written.
- Askama templates cannot call `.get()` on BTreeMap directly. Add helper methods on view-model structs.
- Every route reading a path parameter must canonicalize before filesystem access.
- Use OOB swaps for multi-target updates instead of client-side JS.
- Aesthetic decisions belong in DesignFrontend, not here.
