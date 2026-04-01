---
name: DataExplorer
description: Build single-file HTML data explorer apps with tabbed views, charts, and searchable tables. Extracts data via Python scripts, renders as static browser apps with Chart.js.
---

Build a standalone HTML data explorer for a database or dataset. The pattern: Python extraction script generates a `*-data.js` file, HTML app loads it with tabs, charts, and tables.

## Architecture

```
scripts/build-<domain>.py    → app/<domain>-data.js     (Python extract → JS variable)
app/<domain>.html            → loads <domain>-data.js   (static HTML app)
app/shared.css               → common styles            (reusable across apps)
app/shared.js                → DOM helpers              (createTable, createChart, etc.)
```

No build toolchain. No bundler. Open the HTML file directly in a browser.

## Step 1: Data Extraction Script

Create `scripts/build-<domain>.py` that connects to the data source and writes a JS file:

```python
data = { "table_name": rows, "summary": stats }
with open(output_path, "w") as handle:
    handle.write("var DOMAIN_DATA = ")
    json.dump(data, handle, ensure_ascii=False, default=str, indent=2)
    handle.write(";\n")
```

Rules for the extraction script:
- Use `argparse` for host, port, password, output path
- Password from environment variable, never hardcoded
- Each query function returns a simple structure (list of dicts or dict of values)
- Use `RTRIM()` on CHAR columns for SQL Server databases
- Include both active and archive tables when the database uses the A-prefix convention
- Filter out garbage dates with reasonable upper bounds (e.g., `< '2027-01-01'`)
- Print progress to stderr: what's being fetched, how many rows

## Step 2: Shared Assets

If `app/shared.css` and `app/shared.js` don't exist, create them. The shared JS provides DOM-safe helpers:

- `formatNumber(n)` — locale-formatted with cs-CZ
- `createStat(value, label)` — stat card element
- `createStatsRow(stats)` — row of stat cards
- `createCard(title)` — white card container
- `createTable(headers, rows, numericColumns)` — full table with thead/tbody
- `createChart(container, chartConfig)` — Chart.js canvas inside a container
- `setupTabs()` — tab switching for `data-tab` attributes

## Step 3: HTML App

Create `app/<domain>.html` with:
- Header (title, subtitle)
- Tab bar (3-5 tabs per app)
- Content div per tab
- Load `<domain>-data.js`, `shared.js`, `shared.css`
- App-specific JS using DOM methods (createElement, textContent — no innerHTML with data)

Standard tab set for a database explorer:
- **Overview** — stat cards + top items table + primary time-series chart
- **Detail** — searchable table of all items with key metrics
- **Trends** — time-series charts (monthly, yearly)
- **Categories** — breakdown by type/group/building/warehouse

Use Chart.js (CDN) for all charts. Bar charts for distributions, line charts for time series.

## Step 4: Build and Verify

```sh
source .env
python scripts/build-<domain>.py        # generates data JS
open app/<domain>.html                   # verify in browser
```

## Conventions

- `var` for top-level data variables (accessed via window by the app)
- No innerHTML with data values — use textContent and createElement
- Rough row counts in skill docs (~595K not 594,795)
- Chart.js options: `responsive: true, maintainAspectRatio: false, pointRadius: 0` for line charts
- Tab IDs: `tab-<name>` pattern, switched by `data-tab` attribute on `.tab` elements
