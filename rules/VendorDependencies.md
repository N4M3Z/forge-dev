For static HTML apps that need to work from `file://`, on SharePoint, or behind firewalls, vendor JS libraries into `app/vendor/` instead of loading from CDN.

CDN is fine during development and for apps served over HTTP. When distributing HTML files to non-technical users or deploying to restricted environments, vendored files guarantee the app works.

Both approaches can coexist in the same project.
