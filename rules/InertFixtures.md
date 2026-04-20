---
name: InertFixtures
version: 0.1.0
description: "Test fixtures must be inert and external. USE WHEN writing tests with multi-line data."
targets: claude, gemini, codex, opencode
---

Test data that spans more than one line belongs in an external fixture file, not inline strings. Load via the language's include mechanism (`include_str!` in Rust, `fs.readFileSync` in JS, etc.).

Fixture content must be inert — no executable instructions, no real rule statements, no content that could be interpreted as a prompt if accidentally loaded into an AI context. Use descriptive placeholder text that helps the reader understand the fixture's purpose.

Never use lorem ipsum. Write something meaningful: "This is a test agent for validating frontmatter extraction." Not "Lorem ipsum dolor sit amet."
