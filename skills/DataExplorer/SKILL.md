---
name: DataExplorer
description: Build static HTML data explorer apps from SQL databases or datasets. Vega-Lite or Chart.js for charts, Tabulator for tables, vendored JS. Produces standalone HTML files suitable for SharePoint, Cloudflare Pages, or email.
---

Build standalone HTML data explorers that work without a server. The output is a set of files you can put on SharePoint, Cloudflare Pages, or send as email attachments.

## Architecture

```
scripts/build-<domain>.py  → data/<domain>.parquet        (canonical, typed)
                           → app/<domain>-data.js          (JS variable for HTML apps)
app/<domain>.html          → loads data + vendor libs      (static HTML app)
app/vendor/                → vega-embed, tabulator, etc.   (vendored, no CDN dependency)
app/shared.css             → CSS design system             (variables, cards, pills, tabs)
app/shared.js              → shared utilities              (export, glossary, comments)
```

No build toolchain. No bundler. No server. Open the HTML file directly in a browser.

## Tool Stack

| Layer      | Tool                       | Why                                                       |
| ---------- | -------------------------- | --------------------------------------------------------- |
| Charts     | Vega-Lite or Chart.js      | Vega-Lite for declarative specs, Chart.js for Sankey/custom|
| Tables     | Tabulator.js               | Sort, filter, search, CSV/XLSX export built in            |
| Design     | CSS custom properties      | Inspired by Tabler and lb-store-cleanup patterns          |
| Data       | Parquet (canonical)        | Typed, columnar, readable by pandas/DuckDB/PyGWalker     |
| Extraction | Python + pymssql/pandas    | Direct database queries, argparse for config              |

### Chart Library Choice

**Vega-Lite** — declarative JSON specs, interactive, portable to Altair/Observable/Quarto. Best for standard bar/line/scatter/heatmap charts where the spec describes what to show and the renderer handles the rest.

**Chart.js** — imperative config, richer plugin ecosystem. Best for Sankey flow diagrams (chartjs-chart-sankey), custom annotations, and cases where you need fine control over rendering. The Sankey visualization in lb-accounting is an example of Chart.js doing something Vega-Lite can't match easily.

Use both when appropriate. They coexist in the same HTML file.

### Why Tabulator Over Hand-Coded Tables

Tabulator.js gives sort, filter, search, pagination, and CSV/XLSX export from a single constructor call. No hand-coding `sortableTable()` functions. Inline header filters narrow rows as you type.

## Step 1: Vendor Dependencies

Download JS libraries into `app/vendor/`. No CDN loading — files must work from `file://` without internet.

```sh
mkdir -p app/vendor
curl -o app/vendor/vega-embed.min.js "https://cdn.jsdelivr.net/npm/vega-embed@6/build/vega-embed.min.js"
curl -o app/vendor/tabulator.min.js "https://unpkg.com/tabulator-tables/dist/js/tabulator.min.js"
curl -o app/vendor/tabulator.min.css "https://unpkg.com/tabulator-tables/dist/css/tabulator_midnight.min.css"
```

For Chart.js (when needed for Sankey or custom charts):
```sh
curl -o app/vendor/chart.umd.min.js "https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"
curl -o app/vendor/chartjs-chart-sankey.min.js "https://cdn.jsdelivr.net/npm/chartjs-chart-sankey@0"
```

Commit vendor files. They change rarely.

## Step 2: Data Extraction

Create `scripts/build-<domain>.py` using shared `db_utils.py` (if it exists) or standalone:

```python
from db_utils import create_connection, parse_build_args, write_js_output

def main():
    arguments = parse_build_args("Build domain data", default_database="DbName", default_output="app/domain-data.js")
    connection = create_connection(arguments.database, arguments.host, arguments.port, arguments.password)
    # ... fetch queries ...
    write_js_output("DOMAIN_DATA", data, arguments.output)
    # Also write parquet for downstream tools:
    df.to_parquet("data/domain.parquet")
```

Extraction rules:
- Password from environment variable, never hardcoded
- `RTRIM()` on CHAR columns (SQL Server padding)
- Include archive tables (A-prefix convention) for full history
- Filter garbage dates with upper bound (`< '2027-01-01'`)
- Emit `data_quality` array for detected issues (nulls, outliers, orphans)
- Write both JS (for HTML apps) and Parquet (for PyGWalker/Datapane/Metabase)

## Step 3: HTML App

Load vendored libraries:

```html
<link rel="stylesheet" href="vendor/tabulator.min.css">
<link rel="stylesheet" href="shared.css">
<script src="vendor/vega-embed.min.js"></script>
<script src="vendor/tabulator.min.js"></script>
<script src="domain-data.js"></script>
<script src="shared.js"></script>
```

### Charts with Vega-Lite

```javascript
vegaEmbed('#chart-yearly', {
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "data": {"values": data.yearly_summary},
    "mark": "bar",
    "encoding": {
        "x": {"field": "year", "type": "ordinal"},
        "y": {"field": "count", "type": "quantitative"}
    }
}, {actions: false});
```

### Charts with Chart.js (Sankey, custom)

```javascript
new Chart(canvas, {
    type: 'sankey',
    data: { datasets: [{ data: flowData, colorFrom: c => c.from, colorTo: c => c.to }] }
});
```

### Tables with Tabulator

```javascript
var table = new Tabulator("#table-procedures", {
    data: data.procedures,
    columns: [
        {title: "Name", field: "name", sorter: "string", headerFilter: "input"},
        {title: "Code", field: "code", sorter: "string"},
        {title: "Price", field: "price", sorter: "number", formatter: "money"},
    ],
    pagination: true,
    paginationSize: 50,
    layout: "fitColumns",
});
// Export: table.download("csv", "procedures.csv")
```

### Standard Tab Layout

- **Overview** — stat cards, primary chart, top items table
- **Trends** — time-series (yearly, monthly), year-over-year comparison
- **Detail** — full searchable/sortable table with export
- **Categories** — pill filters by type/group/domain, breakdown charts
- **Quality** — data quality issues detected during extraction

## Step 4: CSS Design System

Use CSS custom properties (`:root` variables):

```css
:root {
    --primary: #1a6b8a;
    --bg: #f4f6f8;
    --card: #fff;
    --text: #2c3e50;
    --green: #27ae60;
    --red: #c0392b;
    --radius: 8px;
    --shadow: 0 1px 3px rgba(0,0,0,0.06);
}
```

Gradient header, sticky tab bar, pill filters with counts, glossary tooltips.

## Step 5: Distribution

| Target           | What to deliver                               |
| ---------------- | --------------------------------------------- |
| SharePoint       | Upload HTML + data.js + vendor/ + shared.*    |
| Cloudflare Pages | Push to git, auto-deploys                     |
| Email            | Zip the app/ directory                        |
| Metabase (later) | Point at the Parquet files or source database |

## Downstream Renderers

The Parquet files and Vega-Lite specs are standard formats consumable by other tools:

| Tool        | Reads                    | For                           |
| ----------- | ------------------------ | ----------------------------- |
| PyGWalker   | Parquet via pandas       | Ad-hoc Tableau-like explorer  |
| Datapane    | Parquet via pandas       | Polished report HTML          |
| Altair      | Generates Vega-Lite specs| Python-side chart definitions |
| DuckDB      | Parquet natively         | Fast SQL on exported data     |
| Metabase    | Source database or Parquet| Full BI platform (later)     |

## Anti-Patterns

- **No CDN in production** — vendor all JS. CDN fails offline, on SharePoint, behind firewalls
- **No Perspective WASM** — fragile CDN loading, CORS issues, breaks on `file://`
- **No hand-coded sort/filter/export** — use Tabulator
- **No innerHTML with data** — use textContent or Tabulator's cell formatters
- **No exact row counts in docs** — use rough numbers (~595K not 594,795)
