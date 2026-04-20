Use `var` for top-level module exports that other scripts access via `window`. `const` and `let` at the top level of a `<script>` tag do NOT go on the `window` object. Any cross-file access like `window.App.state` silently returns `undefined` and falls back to defaults.

```javascript
// WRONG — other scripts can't see this via window.App
const App = (() => { ... })();

// RIGHT — accessible as window.App from other scripts
var App = (() => { ... })();
```

This applies to any multi-file vanilla JS app without a bundler. Bundlers (webpack, vite) wrap everything in modules where this distinction doesn't matter. For `file://` apps and unbundled `<script>` tags, `var` is the only way to share state across files.
