Every repo should include the GitHub community health files relevant to its audience. GitHub auto-detects these and surfaces them in the repository UI:

| File | UI element | When to include |
| --- | --- | --- |
| `README.md` | Rendered below file list | Always |
| `LICENSE` | License badge in sidebar | Always (EUPL-1.2 for forge modules) |
| `CONTRIBUTING.md` | "Contributing" link + PR helper | Repos accepting contributions |
| `SECURITY.md` | "Security" tab | Repos with deployable code |
| `CODE_OF_CONDUCT.md` | Sidebar link | Public repos |
| `SUPPORT.md` | Linked from issues | Repos with external users |
| `CITATION.cff` | "Cite this repository" sidebar | Research or academic projects |
| `FUNDING.yml` | "Sponsor" button | Open source projects |

Files can live in root, `.github/`, or `docs/`. GitHub checks all three locations.

For multilingual READMEs, use `README.md` (primary) + `README.{lang}.md` (ISO 639-1 code) with a language switcher line at the top of each file. GitHub does not natively support language tabs — the link pattern is a community convention.
