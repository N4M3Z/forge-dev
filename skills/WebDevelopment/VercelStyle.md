# Vercel-Style Dashboard CSS

Dark theme conventions for developer tool dashboards. Inspired by Vercel, Linear, and Grafana's deployment status views.

## Design Principles

- Status color as the only chromatic element against a monochrome background.
- Monospace font for paths, hashes, and technical values.
- System sans-serif for UI labels and prose.
- Generous whitespace between sections.
- Minimal borders (1px, low-contrast).

## Color Tokens

```css
:root {
    --bg: #0a0a0a;
    --surface: #141414;
    --surface2: #1e1e1e;
    --border: #2a2a2a;
    --text: #e5e5e5;
    --text-muted: #888;
    --accent: #3b82f6;
    --green: #22c55e;
    --amber: #f59e0b;
    --red: #ef4444;
}
```

## Status Dots

Small colored circles (8px) indicating artifact state:

```css
.dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; }
.dot-ok { background: var(--green); }       /* Unchanged */
.dot-stale { background: var(--amber); }    /* Stale (source changed) */
.dot-modified { background: var(--red); }   /* Modified (user edited) */
.dot-new { background: var(--accent); }     /* New (not yet deployed) */
.dot-none { background: var(--border); }    /* Not deployed to this provider */
```

Use `title` attributes for hover tooltips: `<span class="dot dot-ok" title="Unchanged"></span>`.

## Typography

```css
--mono: 'SF Mono', 'Cascadia Code', 'JetBrains Mono', monospace;
--sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
```

- `.path` class for file paths, SHA hashes, URIs: `font-family: var(--mono); font-size: 0.8rem;`
- Body text in sans-serif.
- No web fonts loaded. System fonts keep the dashboard offline-capable and fast.

## Layout Patterns

### Summary bar

Colored counters above the main content:

```css
.summary-bar {
    display: flex; gap: 1.5rem;
    padding: 0.75rem 1rem;
    background: var(--surface);
    border-radius: 6px;
    font-size: 0.85rem;
}
```

### Deployment matrix

Table with artifact rows, provider columns, status dots in cells. Module headers span all columns as group separators.

### Sidebar + detail

CSS grid split: `grid-template-columns: 240px 1fr`. Sidebar has a selectable list; detail pane loads via htmx partial.

### Tab navigation

Horizontal `<nav>` with `border-bottom: 2px solid transparent` on inactive tabs, `border-bottom-color: var(--accent)` on active. Full-page navigation, not htmx (tabs change the whole view).

## Anti-Patterns

- Colored backgrounds on table rows (noisy). Use status dots only.
- Rounded cards for everything (Vercel uses flat tables for data).
- Gradient backgrounds (breaks the monochrome rule).
- Emoji as status indicators (inconsistent rendering across OS).
- Light theme as default (developer tools are dark-first).
