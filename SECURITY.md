# Security

## Reporting a Vulnerability

Email **martin.zeman@pm.me** with `[forge-dev security]` in the subject. Please include:

- Affected skill, agent, or adopted file (path within the repo)
- Reproduction steps or proof-of-concept
- Observed vs expected behaviour

Expect an initial acknowledgement within 72 hours.

## Third-Party Adopted Content

forge-dev contains skills and agents adopted from community sources — currently [davila7/claude-code-templates](https://github.com/davila7/claude-code-templates) (MIT). Every adopted file is pinned to a specific upstream commit SHA and ships with a SLSA provenance sidecar under `.provenance/` recording:

- The deployed file's `sha256` digest
- The upstream file's `sha256` digest
- The commit-pinned `upstream_url`
- `AdoptArtifact` as a build input

### How to verify

```sh
forge provenance .
```

Reports per-file verification. A deployed file whose on-disk digest does not match its sidecar indicates either (a) a benign post-adoption edit without sidecar refresh, or (b) tampering. Distinguish with `git log -p <file>` — intentional edits appear as commits by the repo owner; drift outside commits is the red flag.

### Trust boundary

The upstream aggregator is a community catalogue with no known audit process. Adoption is SHA-pinned, but behavioural content (skill instructions, agent prompts) is not line-by-line audited by forge maintainers. Recommendations:

- Treat adopted skills as third-party code — read before invoking in security-sensitive contexts
- Re-audit adopted files when bumping the upstream pin (see each sidecar's `upstream_url`)
- Report suspected behavioural issues in adopted content via the email above; we will assess and either patch-in-place or retire the adoption

## Scope

In scope:

- Malicious or unsafe behaviour in adopted skills / agents (including prompt-injection vectors in Instructions sections)
- Tampered files that claim valid provenance
- License attribution gaps
- Secret disclosure in committed content

Out of scope:

- Upstream vulnerabilities in `davila7/claude-code-templates` directly — report those upstream
- Vulnerabilities in the forge toolchain itself — see [forge-cli](https://github.com/N4M3Z/forge-cli) / [forge-core](https://github.com/N4M3Z/forge-core)
