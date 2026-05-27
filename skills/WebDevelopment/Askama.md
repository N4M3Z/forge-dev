# Askama Reference

Compile-time HTML templates for Rust. Jinja2 syntax, type-checked at build.

## Template Struct

```rust
use askama::Template;

#[derive(Template)]
#[template(path = "dashboard/overview.html")]
pub struct OverviewTemplate<'a> {
    pub tab: &'a str,
    pub version: &'a str,
    pub items: &'a [ItemView],
}
```

The struct fields are available as variables in the template. Type mismatches are compile errors.

## Template Directory

Askama reads from `templates/` relative to `CARGO_MANIFEST_DIR`. No configuration needed for the default location.

## Syntax

### Variables

`{{ variable }}`, `{{ struct.field }}`, `{{ method_call() }}`

### Blocks and Inheritance

```html
{# base.html #}
<html>
<body>{% block content %}{% endblock %}</body>
</html>

{# child.html #}
{% extends "base.html" %}
{% block content %}
<h1>Page content here</h1>
{% endblock %}
```

### Control Flow

```html
{% for item in items %}
<tr><td>{{ item.name }}</td></tr>
{% endfor %}

{% if condition %}...{% else %}...{% endif %}

{% match option_value %}
{% when Some with (inner) %}{{ inner }}
{% when None %}default
{% endmatch %}
```

### Includes

```html
{% include "dashboard/partial.html" %}
```

Included templates share the parent's variables.

## Gotchas

### No `.get()` on maps

Askama's codegen breaks on `BTreeMap::get()` due to `Borrow` trait bounds. Add a helper method on the view-model struct:

```rust
impl ArtifactView {
    pub fn status_for(&self, provider: &str) -> Option<&ProviderStatus> {
        self.providers.get(provider)
    }
}
```

Then in the template: `{% match artifact.status_for(provider) %}`

### No arithmetic in expressions

`{{ providers|length + 1 }}` fails. Compute in the struct and pass as a field, or hardcode.

### Enum matching requires full path

```html
{% match status %}
{% when crate::manifest::FileStatus::Unchanged %}ok
{% when crate::manifest::FileStatus::Stale %}stale
{% endmatch %}
```

Use `commands::manifest::FileStatus::Unchanged` (the lib crate name as the path root).

### Recompilation required

Template changes require `cargo build`. No hot reload. During development, keep the feedback loop short by running `cargo check` after template edits.

## Axum Integration

Askama 0.13 has built-in axum support. The `Template` derive generates an `IntoResponse` implementation. Return the template directly from a handler:

```rust
async fn overview(State(state): State<Arc<AppState>>) -> impl IntoResponse {
    OverviewTemplate {
        tab: "overview",
        version: &state.version,
        items: &state.items,
    }
}
```

No need for `Html(template.to_string())` wrapping (though it works too).
