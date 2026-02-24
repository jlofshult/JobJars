# CLAUDE.md — JobJars

This file provides context and guidance for AI assistants (Claude, Copilot, etc.) working in this repository. Update this file as the project evolves.

---

## Project Overview

**JobJars** is a new repository with no committed code yet. This document will grow alongside the codebase to capture architecture decisions, development workflows, and coding conventions.

> **Note for AI assistants:** This repository is in its initial state. No source files, package manifests, or configuration files exist yet. When the first code is committed, update this file to reflect the actual stack, structure, and workflows.

---

## Repository Status

| Item | Status |
|------|--------|
| Source code | Not yet added |
| Package manager | TBD |
| Framework / language | TBD |
| CI/CD | Not yet configured |
| Tests | Not yet added |
| Linting / formatting | Not yet configured |

---

## Codebase Structure

_To be filled in once the project structure is established._

```
JobJars/
├── CLAUDE.md         ← This file
└── (source files TBD)
```

---

## Development Workflow

### Branching

- Main branch: `main` (or `master` — confirm once first commit exists)
- Feature branches: `feature/<short-description>`
- Bug fixes: `fix/<short-description>`
- AI-generated branches: `claude/<session-id>`

### Commits

Use clear, imperative commit messages:

```
Add user authentication module
Fix null pointer in job listing parser
Update README with setup instructions
```

Avoid vague messages like `fix stuff`, `WIP`, or `changes`.

### Pull Requests

- Keep PRs focused on a single concern
- Include a description of what changed and why
- Reference related issues when applicable

---

## Commands

_Populate this section once the tech stack is established._

```bash
# Install dependencies
# (command TBD)

# Run development server
# (command TBD)

# Run tests
# (command TBD)

# Lint and format
# (command TBD)

# Build for production
# (command TBD)
```

---

## Coding Conventions

_To be defined as the stack is chosen. Common defaults to follow until overridden:_

- Prefer explicit over implicit
- Keep functions small and focused (single responsibility)
- Write tests alongside new features
- Avoid committing secrets, credentials, or `.env` files
- Delete dead code rather than commenting it out

---

## Environment Variables

_Document required environment variables here as they are introduced._

```
# Example format:
# VAR_NAME=description of what this controls
```

---

## AI Assistant Notes

- **Read before editing:** Always read existing files before modifying them
- **Minimal changes:** Only change what is necessary for the task at hand
- **No speculative features:** Do not add features not explicitly requested
- **Update this file:** When the stack and structure are established, update all TBD sections above
- **Branch discipline:** Always develop on the designated branch; never push to `main` directly

---

## Updating This File

When the first meaningful code is committed, revisit and update:

1. **Project Overview** — describe what JobJars does
2. **Codebase Structure** — reflect the actual directory layout
3. **Commands** — fill in real build/test/lint commands
4. **Coding Conventions** — capture language- and framework-specific rules
5. **Environment Variables** — document all required vars

---

_Last updated: 2026-02-24_
