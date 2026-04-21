CSV files opened in Excel execute cells starting with `=`, `+`, `-`, `@`, or `|` as formulas. When exporting data that non-technical users will open in a spreadsheet, prefix these leading characters with a tab character (`\t`) inside the quoted cell.

```
// Before (vulnerable)
"=SUM(A1:A2)"

// After (safe)
"	=SUM(A1:A2)"
```

This applies to any value originating from user input, external systems, or uncontrolled data sources — product names, descriptions, free-text fields. Header rows with known safe labels don't need sanitization.

<!-- for czech, dont forget we use comma and period for decimals, so csv needs sep=; -->