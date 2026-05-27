# htmx Reference

Adopted from [ercan-er/htmx-claude-skill](https://github.com/ercan-er/htmx-claude-skill) at commit `02fd53ac`. Consolidated from 10 reference files into one companion.

## Core Rules

1. Server returns HTML fragments, not JSON.
2. Detect `HX-Request` header; return fragments for htmx, full layout otherwise.
3. Use correct `hx-swap` for each UI update.
4. Use OOB swaps (`hx-swap-oob`) for multi-target updates.
5. Preserve browser history with `hx-push-url` when navigating.
6. Always validate CSRF tokens on mutating requests.
7. Avoid unnecessary polling.
8. Never rebuild DOM with client-side JS.

## Attributes

### Request attributes

`hx-get`, `hx-post`, `hx-put`, `hx-patch`, `hx-delete`

### Targeting

`hx-target="#element-id"` — always be explicit. Never replace an entire layout container.

### History

`hx-push-url`, `hx-replace-url`, `hx-history-elt` — preserve navigation consistency.

### Other

`hx-boost`, `hx-confirm`, `hx-include`, `hx-vals`, `hx-indicator`, `hx-disabled-elt`, `hx-select`, `hx-select-oob`, `hx-headers`

Use attributes before writing JS.

## Triggers

`hx-trigger="click"` (default for most elements), `"change"` (inputs), `"submit"` (forms), `"load"` (on element load), `"revealed"` (lazy load on scroll), `"every 5s"` (polling).

Modifiers: `once`, `changed`, `delay:500ms`, `throttle:1s`, `from:selector`.

## Swap Modes

| Mode | Effect |
|---|---|
| `innerHTML` | Replace inner content (default) |
| `outerHTML` | Replace entire element |
| `beforebegin` | Insert before element |
| `afterbegin` | Insert as first child |
| `beforeend` | Append as last child |
| `afterend` | Insert after element |
| `delete` | Remove element |
| `none` | No swap (fire-and-forget) |

Modifiers: `swap:1s` (delay), `settle:200ms`, `transition:true`, `show:top` (scroll).

Choose swap based on UI intention. Avoid replacing large containers.

## Server Patterns

```
if HX-Request header present:
    return HTML fragment (partial template)
else:
    return full page layout
```

Fragment architecture:

```
templates/
    base.html           full layout
    overview.html       extends base
    _detail.html        htmx partial (no base)
```

Fragments are reusable and isolated. Prefix partial-only templates with `_` or put in a `partials/` directory.

## Headers

| Header | Direction | Purpose |
|---|---|---|
| `HX-Request` | request | Identifies htmx requests |
| `HX-Target` | request | Target element ID |
| `HX-Trigger` | request | Triggering element ID |
| `HX-Trigger` | response | Trigger client-side events |
| `HX-Redirect` | response | Client-side redirect |
| `HX-Retarget` | response | Override target element |
| `HX-Reswap` | response | Override swap strategy |
| `HX-Push-Url` | response | Push URL to history |

## Security

- Validate CSRF tokens on POST/PUT/PATCH/DELETE.
- Sanitize all user input server-side before rendering into HTML.
- Set `Content-Security-Policy` headers to restrict inline scripts.
- Use `hx-headers` to include auth tokens when needed.

## Anti-Patterns

| Anti-pattern | Fix |
|---|---|
| Returning JSON and building DOM client-side | Return HTML fragments |
| Recreating SPA state management | Server holds the state |
| Returning full `<html>` for htmx requests | Return only the targeted fragment |
| Ignoring `hx-push-url` for pagination | Add history support for navigable views |
| Polling every 1s without reason | Use `hx-trigger="every 30s"` or SSE |
| Redirecting on validation error | Return the form with inline errors (422) |
| Updating multiple areas via JS | Use OOB swaps |

## Events

`htmx:beforeRequest`, `htmx:afterRequest`, `htmx:beforeSwap`, `htmx:afterSwap`, `htmx:responseError`

Use events for loading indicators and error handling, not for DOM manipulation.
