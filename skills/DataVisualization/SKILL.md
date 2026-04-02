---
name: DataVisualization
description: Choose and configure visualization tools for data explorer apps. Vega-Lite for declarative charts, Chart.js for Sankey and custom visualizations, Tabulator for interactive tables.
---

Guide for selecting and configuring visualization tools in data explorer apps.

## Chart Libraries

### Vega-Lite — Declarative Charts

Best for standard visualizations where the data shape determines the chart. Define a JSON spec, the renderer handles layout, tooltips, and interaction.

```javascript
vegaEmbed('#chart', {
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "data": {"values": data},
    "mark": "bar",
    "encoding": {
        "x": {"field": "year", "type": "ordinal"},
        "y": {"field": "count", "type": "quantitative"}
    }
}, {actions: false});
```

Use for: bar, line, scatter, area, heatmap, histogram, faceted charts, geographic maps.

Vega-Lite specs are portable — the same spec works in Altair (Python), Observable, Quarto, and standalone HTML.

### Chart.js — Imperative Charts

Best for visualizations that need plugins or fine-grained control. The Sankey flow diagram in lb-accounting is an example — Chart.js with chartjs-chart-sankey produces a visualization Vega-Lite can't match easily.

```javascript
new Chart(canvas, {
    type: 'sankey',
    data: { datasets: [{ data: flowData }] }
});
```

Use for: Sankey diagrams, charts with datalabels plugin, annotation overlays (threshold lines, target markers), zoom/pan interaction.

Key plugins:
- `chartjs-chart-sankey` — flow diagrams
- `chartjs-plugin-datalabels` — value labels on bars/segments
- `chartjs-plugin-annotation` — threshold lines, reference bands
- `chartjs-plugin-zoom` — pan and pinch-zoom on time series

### When to Use Which

| Visualization               | Library    | Reason                                    |
| ---------------------------- | ---------- | ----------------------------------------- |
| Bar, line, scatter, area     | Vega-Lite  | Declarative spec, less code               |
| Heatmap, histogram           | Vega-Lite  | Built-in transforms                       |
| Faceted (small multiples)    | Vega-Lite  | One spec, automatic faceting              |
| Sankey flow diagram          | Chart.js   | Plugin ecosystem, no Vega-Lite equivalent |
| Chart with value labels      | Chart.js   | datalabels plugin                         |
| Chart with threshold lines   | Chart.js   | annotation plugin                         |
| Mixed (both in same app)     | Both       | They coexist, load both libraries         |

## Table Library

### Tabulator.js — Interactive Tables

Replaces hand-coded sortable tables. One constructor call gives sort, filter, search, pagination, and export.

```javascript
var table = new Tabulator("#container", {
    data: data.items,
    columns: [
        {title: "Name", field: "name", sorter: "string", headerFilter: "input"},
        {title: "Price", field: "price", sorter: "number", formatter: "money", hozAlign: "right"},
    ],
    pagination: true,
    paginationSize: 50,
    layout: "fitColumns",
});

// Export
table.download("csv", "data.csv");
table.download("xlsx", "data.xlsx");
```

Key features: inline header filters (type to narrow rows), column resize, frozen columns, row grouping, tree data, virtual DOM for large datasets.

## CSS Design System

Use CSS custom properties for consistency across apps:

```css
:root {
    --primary: #1a6b8a;
    --primary-hover: #145a75;
    --bg: #f4f6f8;
    --card: #fff;
    --text: #2c3e50;
    --text-sec: #6c7a89;
    --green: #27ae60;
    --red: #c0392b;
    --orange: #e67e22;
    --blue: #2980b9;
    --radius: 8px;
    --shadow: 0 1px 3px rgba(0,0,0,0.06);
}
```

Gradient header, sticky tab bar, pill filters with counts, glossary tooltips. Inspired by Tabler (39K stars) and lb-store-cleanup patterns.

## Data Format

Produce Parquet as the canonical output alongside JS data files. Parquet is readable by pandas, DuckDB, PyGWalker, Datapane, and Metabase — the standard interchange format for tabular data.

```python
df.to_parquet("data/domain.parquet")
write_js_output("DOMAIN_DATA", data, "app/domain-data.js")
```

## Known Non-Starters

**Perspective (FINOS)** — WASM-based pivot table. Impressive in demos but fragile in practice: CDN loading fails, CORS issues on `file://`, requires 4 chained script loads. Tested and rejected.

**AG Grid** — powerful but complex API, heavier than Tabulator for dashboard use cases.

**D3.js** — overkill for standard charts. Only adds value for custom visualizations (force-directed graphs, chord diagrams) that neither Vega-Lite nor Chart.js can handle.
