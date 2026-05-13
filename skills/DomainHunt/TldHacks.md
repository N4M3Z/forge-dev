# TLD Hacks

Patterns where the TLD completes or amplifies the second-level word.

## Country-code completion

When a ccTLD reads as the end of a real word:

| Pattern               | Reads as            | TLD origin |
| --------------------- | ------------------- | ---------- |
| `for.ge`              | "forge"             | Georgia    |
| `<word>.de`           | English past tense  | Germany    |
| `<word>.es`           | Spanish plural/verb | Spain      |
| `<word>.it`           | "X it" imperative   | Italy      |
| `<word>.is`           | "X is" sentence     | Iceland    |
| `<word>.in`           | "X in" preposition  | India      |
| `<word>.ng`           | English `-ing` form | Nigeria    |
| `<word>.am`           | "X am" verb         | Armenia    |
| `<word>.do`           | "X do" verb         | Dominican Republic |
| `<word>.me`           | "X me" command      | Montenegro |
| `<word>.us`           | "X us" pronoun      | USA        |

Most cleverly-readable TLD-completion plays have been claimed by domainers for over a decade. Always probe before assuming.

## File-extension TLDs

When the TLD doubles as a recognized file format:

| TLD     | Reads as           | Brand fit                                                  |
| ------- | ------------------ | ---------------------------------------------------------- |
| `.md`   | Markdown           | Content-authoring tools, documentation-first projects      |
| `.rs`   | Rust source        | Rust libraries and CLIs                                    |
| `.sh`   | Shell script       | CLI tools, devops, infrastructure                          |
| `.py`   | Python source      | Python projects (registration heavily restricted)          |
| `.so`   | Shared object      | Compiled libraries, plugins                                |
| `.zip`  | Zip archive        | Compression, releases, transfers (security-sensitive TLD)  |
| `.mov`  | QuickTime video    | Video tools                                                |

## Element-symbol TLDs

The periodic table hides in some country codes:

| TLD   | Element    | Notes                                                                              |
| ----- | ---------- | ---------------------------------------------------------------------------------- |
| `.ai` | none       | Anguilla — reinterpreted as Artificial Intelligence                                |
| `.au` | Gold (Au)  | Australia — also reads as "forge gold" for metalworking brands. Australian-presence required for direct `.au` |
| `.ag` | Silver (Ag)| Antigua and Barbuda                                                                 |
| `.cu` | Copper (Cu)| Cuba — heavily restricted                                                          |
| `.pt` | Platinum (Pt) | Portugal                                                                        |

## Programmer-meta TLDs

| TLD    | Reads as                  | Operator / cost notes                       |
| ------ | ------------------------- | ------------------------------------------- |
| `.foo` | Placeholder variable      | Google, premium-tier on short names         |
| `.bar` | Placeholder variable      | Google                                      |
| `.new` | Create-new (sheets.new)   | Google, single-action semantic              |
| `.zip` | Compression               | Google, controversial launch                |

## Verifying a candidate TLD actually exists

Several plausible-sounding TLDs were never delegated. Confirm via IANA's bootstrap before designing around them:

```bash
whois -h whois.iana.org .<tld> 2>&1 | grep -iE "whois:|refer:"
```

Empty `whois:` field or "0 objects" means not delegated. Examples that don't exist as TLDs:

| Imagined TLD              | Reality                                                    |
| ------------------------- | ---------------------------------------------------------- |
| `.agent`                  | Not delegated                                              |
| `.forge`                  | Not delegated                                              |
| `.keep`                   | Not delegated                                              |
| `.skill`                  | Not delegated                                              |
| `.galaxy`, `.empire`, `.realm`, `.universe`, `.cosmos`, `.kingdom` | None delegated         |
| `.maker`, `.makers`, `.studios` | None delegated (singular `.studio` does exist)         |
| `.developer`, `.development`, `.factory`, `.machine` | None delegated                  |
