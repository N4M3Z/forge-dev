# axum + rust-embed Reference

HTTP server for the dashboard. Routes, middleware, embedded static assets.

## Route Structure

```rust
pub fn router(state: Arc<AppState>) -> Router {
    Router::new()
        .route("/", get(overview))
        .route("/modules", get(modules_page))
        .route("/modules/{name}", get(module_detail))
        .route("/static/{*path}", get(static_handler))
        .with_state(state)
}
```

- Full-page routes (`/`, `/modules`) return Askama templates extending a base layout.
- Detail routes (`/modules/{name}`) return htmx partials (no base layout).
- Static routes serve embedded assets.

## Shared State

```rust
pub struct AppState {
    pub view: DashboardView,
    pub providers: Vec<String>,
    pub version: String,
}
```

Wrap in `Arc<AppState>` and pass via `.with_state()`. Handlers extract with `State(state): State<Arc<AppState>>`.

## rust-embed Static Handler

```rust
use rust_embed::Embed;

#[derive(Embed)]
#[folder = "static/dashboard/"]
struct Assets;

pub async fn serve(Path(path): Path<String>) -> impl IntoResponse {
    let mime = match Path::new(&path).extension().and_then(|e| e.to_str()) {
        Some("js") => "application/javascript",
        Some("css") => "text/css",
        _ => "application/octet-stream",
    };
    match Assets::get(&path) {
        Some(file) => (StatusCode::OK, [(CONTENT_TYPE, mime)], file.data.to_vec()).into_response(),
        None => StatusCode::NOT_FOUND.into_response(),
    }
}
```

Vendor htmx.min.js and CSS into `static/dashboard/`. They compile into the binary at build time.

## Tokio Containment

The data layer (module scanning, manifest reading, provenance) is sync. The web server needs tokio. Contain the async boundary:

```rust
pub fn execute(root: &str, port: Option<u16>) -> Result<i32, Error> {
    let runtime = tokio::runtime::Builder::new_current_thread()
        .enable_all()
        .build()?;
    runtime.block_on(server::start(Path::new(root), port))?;
    Ok(0)
}
```

Handlers that call sync lib functions use `spawn_blocking`:

```rust
async fn overview(State(state): State<Arc<AppState>>) -> impl IntoResponse {
    // state.view is pre-computed at startup, no spawn_blocking needed
    OverviewTemplate { view: &state.view, ... }
}
```

Pre-compute the view at startup. Only use `spawn_blocking` for on-demand operations (refresh, provenance detail).

## Security

### Localhost binding

Always `SocketAddr::from(([127, 0, 0, 1], port))`. Never `0.0.0.0`.

### Host header validation

Block DNS rebinding by rejecting requests where the `Host` header is not `127.0.0.1:<port>` or `localhost:<port>`:

```rust
async fn validate_host(
    request: axum::extract::Request,
    next: axum::middleware::Next,
) -> impl IntoResponse {
    let host = request.headers().get("host").and_then(|h| h.to_str().ok());
    match host {
        Some(h) if h.starts_with("127.0.0.1:") || h.starts_with("localhost:") => {
            next.run(request).await.into_response()
        }
        _ => StatusCode::FORBIDDEN.into_response(),
    }
}
```

Apply as a layer: `.layer(axum::middleware::from_fn(validate_host))`

### Path canonicalization

Any route that accepts a path parameter and reads from disk must canonicalize first:

```rust
let canonical = std::fs::canonicalize(&user_path)?;
if !canonical.starts_with(&allowed_root) {
    return Err("path traversal blocked");
}
```

### No CORS headers

The UI is same-origin. No `Access-Control-Allow-Origin` needed. Omitting it blocks cross-origin reads from other tabs.
