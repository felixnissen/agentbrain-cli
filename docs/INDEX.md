# AgentBrain CLI Documentation Index

Quick reference guide to all documentation files in this project.

## Core Documentation Files

### 1. README.md (Project Root)
**Location:** `../README.md` | **Size:** 249 LOC | **Audience:** New users, developers

Getting started guide with:
- Installation instructions
- Quick start (3 commands to get running)
- Usage examples for all major command groups
- Configuration overview
- Output format reference
- Development setup

**Start here if:** You're new to the CLI or need a quick start guide.

---

### 2. project-overview-pdr.md
**Location:** `./project-overview-pdr.md` | **Size:** 308 LOC | **Audience:** Product managers, architects, stakeholders

Comprehensive product specification including:
- Product overview and value proposition
- 8 functional requirements with acceptance criteria
- 5 non-functional requirements (security, performance, etc.)
- Architecture overview
- Success criteria for v0.1.0, v0.2.0, and v1.0.0
- Dependencies and platform constraints
- Risk assessment

**Start here if:** You need to understand what the product does, its requirements, or business goals.

---

### 3. codebase-summary.md
**Location:** `./codebase-summary.md` | **Size:** 417 LOC | **Audience:** Developers, code reviewers

Overview of codebase structure including:
- Project statistics (20 TypeScript files, 1,711 LOC, 39.5 KB bundle)
- Complete directory structure with descriptions
- File-by-file breakdowns of all modules
- Build and bundle configuration
- Dependencies analysis
- Code patterns and conventions
- Testing strategy
- Security considerations
- Known limitations and future improvements

**Start here if:** You want to understand how the codebase is organized or look up a specific file.

---

### 4. code-standards.md
**Location:** `./code-standards.md` | **Size:** 632 LOC | **Audience:** Developers, code reviewers, QA

Detailed coding standards and conventions:
- TypeScript configuration and strict mode
- File naming and organization (kebab-case, max 200 LOC)
- Code style (types, classes, functions, variables, constants)
- Comments and documentation patterns
- Error handling patterns (ApiError, user-friendly messages)
- API integration patterns (client creation, requests, responses)
- Output formatting conventions
- Configuration system patterns
- Testing patterns and coverage goals
- Performance and security best practices

**Start here if:** You're writing code for this project or reviewing pull requests.

---

### 5. system-architecture.md
**Location:** `./system-architecture.md` | **Size:** 657 LOC | **Audience:** Architects, senior developers, DevOps

Deep dive into system design:
- High-level architecture diagram (7-layer stack)
- 6 detailed component layers with data flow
- Authentication and authorization patterns
- SSE streaming for real-time logs
- Configuration resolution flow
- Complete command execution walkthrough (15 steps)
- Error handling architecture
- Dependencies and external integrations
- Deployment architecture
- Scalability and performance analysis

**Start here if:** You need to understand how the CLI works internally, integrate it, or troubleshoot complex issues.

---

### 6. project-roadmap.md
**Location:** `./project-roadmap.md` | **Size:** 544 LOC | **Audience:** Product managers, project leads, stakeholders, team

Strategic vision and planning:
- Current status (v0.1.0 Alpha, March 2025)
- Completed features and in-progress work
- 5 development phases with timelines and features:
  - Phase 1: Alpha (March-April) — Feature completion
  - Phase 2: Beta (April-May) — Testing, shell completions, templates
  - Phase 3: Production (June) — npm publish, Docker, MCP, Kubernetes, Terraform
  - Phase 4: Enterprise (July-Sept) — Caching, batch ops, audit, plugins
  - Phase 5: Ecosystem (Q4+) — SDKs, IDE plugins, CI/CD integrations
- Dependency update schedule
- Success metrics and milestones
- Risk assessment and mitigation
- Budget and resource allocation (880 hours to 1.0.0)
- Communication and launch plan

**Start here if:** You need to understand project timeline, future plans, or success criteria.

---

## Quick Navigation by Topic

### For New Developers
1. Start with **README.md** — Installation and quick start (use `agentbrain config init` first)
2. Read **codebase-summary.md** — Understand file structure
3. Check **code-standards.md** — Learn conventions before writing code
4. Review **system-architecture.md** — Understand how it all fits together

### For Product Managers
1. Read **project-overview-pdr.md** — Requirements and success criteria
2. Review **project-roadmap.md** — Timeline and phases
3. Check **system-architecture.md** — How the system works

### For System Administrators
1. Start with **README.md** — Installation and configuration
2. Read **system-architecture.md** — Authentication and security
3. Check **code-standards.md** — Security best practices section

### For Code Reviewers
1. Read **code-standards.md** — Conventions and patterns
2. Check **codebase-summary.md** — File organization
3. Review **system-architecture.md** — Design decisions

### For DevOps/Platform Teams
1. Start with **README.md** — Installation and Docker
2. Read **project-roadmap.md** — Phase 3 (Docker, Kubernetes)
3. Check **system-architecture.md** — Deployment and scalability

---

## Command Reference

All commands are documented in README.md. Quick list:

**Core Commands:**
- `agentbrain config` — Configuration management (get/set/list)
- `agentbrain org` — Organization management (CRUD, members)
- `agentbrain connector` (alias: `connector`) — Data source management
- `agentbrain knowledge` (alias: `kb`) — Knowledge base management
- `agentbrain workflow` (alias: `wf`) — ETL workflow management
- `agentbrain permission-group` (alias: `pg`) — Permission management
- `agentbrain category` (alias: `cat`) — Category management
- `agentbrain tag` — Tag management
- `agentbrain search` — Cross-entity search
- `agentbrain query-log` (alias: `ql`) — Query log viewer
- `agentbrain connector-subtype` (alias: `cs`) — Connector subtype management

See **README.md** for full command syntax and examples.

---

## Configuration Reference

**Config Keys:**
- `apiUrl` — API endpoint (default: https://api.agentbrain.sh)
- `apiKey` — API authentication key
- `orgId` — Default organization ID
- `output` — Output format: json, table, yaml (default: table for TTY, json for pipes)
- `timeout` — Request timeout in ms (default: 30000)

**Environment Variables:**
- `AGENTBRAIN_API_URL`
- `AGENTBRAIN_API_KEY`
- `AGENTBRAIN_ORG_ID`
- `AGENTBRAIN_OUTPUT`
- `AGENTBRAIN_TIMEOUT`

**Global Flags:**
- `--api-url <url>` — Override API endpoint
- `--api-key <key>` — Override API key
- `--org <id>` — Override organization ID
- `--output <fmt>` — Output format
- `--verbose` — Enable debug logging

See **README.md** and **system-architecture.md** for detailed configuration examples.

---

## Architecture Components

**Client Layer:**
- `src/client/http-client.ts` — HTTP client with auth, SSE, timeouts
- `src/client/api-error.ts` — Error handling and user messages

**Configuration Layer:**
- `src/config/config-schema.ts` — Configuration interface and defaults
- `src/config/config-manager.ts` — File I/O, env var, config resolution

**Command Layer:**
- `src/index.ts` — Main entry point and command registration
- `src/commands/` — 10 command modules (org, connector, knowledge, workflow, etc.)

**Formatting Layer:**
- `src/formatters/output-formatter.ts` — JSON/YAML/table formatting

**Type Layer:**
- `src/types/api-types.ts` — All API response types

**Utility Layer:**
- `src/utils/global-options.ts` — Global flag registration
- `src/utils/command-helpers.ts` — Shared helper functions

See **codebase-summary.md** for detailed file descriptions and **system-architecture.md** for data flow.

---

## Development Phases

| Phase | Timeline | Focus | Status |
|-------|----------|-------|--------|
| Phase 1: Alpha | March-April 2025 | Feature completion, documentation | Current |
| Phase 2: Beta | April-May 2025 | Testing 80%+, shell completions, templates | Planned |
| Phase 3: Production | June 2025 | npm publish, Docker, MCP, Kubernetes, Terraform | Planned |
| Phase 4: Enterprise | July-September 2025 | Caching, batch ops, audit, plugins | Planned |
| Phase 5: Ecosystem | Q4 2025+ | SDKs, IDE plugins, CI/CD integrations | Future |

See **project-roadmap.md** for detailed phase descriptions and features.

---

## Security Notes

- API keys stored in `~/.agentbrain/config.json` (mode 0600 — user-only readable)
- API key masked in output and logs (shows first 4 and last 4 chars)
- All requests include X-API-Key and X-Org-ID headers
- No sensitive data in error messages (unless --verbose)
- HTTPS required for API communication

See **code-standards.md** and **system-architecture.md** for security best practices.

---

## Common Tasks

### Install and Configure
→ See **README.md** "Quick Start" section

### List Organizations
→ See **README.md** "Organizations" section

### Create a Connector
→ See **README.md** "Connectors" section

### Set Up Workflows
→ See **README.md** "Workflows" section

### Understand Config Resolution
→ See **system-architecture.md** "Configuration Resolution" section

### Extend with Custom Commands
→ See **code-standards.md** "API Integration Patterns" section

### Deploy in Docker
→ See **project-roadmap.md** "Phase 3" section (planned for v0.3.0)

### Integrate with Claude IDE
→ See **project-roadmap.md** "Phase 3: GoClaw MCP Integration" section (planned)

---

## Files Summary

| File | LOC | KB | Purpose |
|------|-----|----|---------|
| README.md | 249 | 8 | Quick start and command reference |
| project-overview-pdr.md | 308 | 12 | Product specification and requirements |
| codebase-summary.md | 417 | 16 | Codebase structure and organization |
| code-standards.md | 632 | 16 | Coding standards and conventions |
| system-architecture.md | 657 | 24 | System design and architecture |
| project-roadmap.md | 544 | 16 | Strategic vision and timeline |
| **TOTAL** | **2,807** | **92** | Complete documentation suite |

---

## Document Maintenance

These documents are kept in sync with the codebase:
- Code examples verified against source
- File paths and command syntax tested
- Architecture descriptions match implementation
- Requirements tracked against features

When updating code, also update relevant documentation sections to maintain consistency.

---

## Questions?

- **Installation help** → README.md
- **Command usage** → README.md
- **Understanding the code** → codebase-summary.md
- **Writing code** → code-standards.md
- **How it works** → system-architecture.md
- **Future plans** → project-roadmap.md
- **Requirements** → project-overview-pdr.md

Last updated: March 5, 2025
