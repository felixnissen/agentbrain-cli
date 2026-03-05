# AgentBrain CLI - Project Overview & Product Development Requirements

## Executive Summary

AgentBrain CLI is a TypeScript command-line interface for AgentBrain enterprise data hub. It enables developers, data engineers, and systems administrators to manage the complete data governance and workflow lifecycle programmatically.

Version: 0.1.0 | License: MIT | Repository: github.com/nextlevelbuilder/agentbrain-cli

## Product Overview

### Purpose

AgentBrain CLI bridges the gap between AgentBrain's web UI and programmatic access. It exposes the full AgentBrain API surface as intuitive command-line commands, enabling:

- Infrastructure-as-code workflows for data management
- CI/CD pipeline integration for automated deployments
- Batch operations across organizations and resources
- Local development and testing of data integrations
- Scripted governance and permission management

### Target Users

1. **Data Engineers** — Build ETL pipelines, manage connectors, test schemas
2. **DevOps/Platform Teams** — Automate infrastructure, manage organizations, deploy workflows
3. **Developers** — Integrate AgentBrain into applications via CLI subprocess calls
4. **Administrators** — Manage permissions, audit logs, organization settings

### Value Proposition

- **Complete Coverage** — All AgentBrain API endpoints available as CLI commands
- **Easy Scripting** — Shell scripts, Docker, Kubernetes manifests, Terraform
- **Developer-Friendly** — Clear command structure, sensible defaults, helpful errors
- **Secure by Default** — Config file permissions (0600), API key masking in output
- **Smart Output** — Auto-detects TTY for human-readable tables or JSON for machines
- **Zero Dependencies** — Lightweight (39.5 KB bundle), runs on Node 20+

## Product Requirements

### Functional Requirements

#### FR-1: Organization Management
- List accessible organizations with member info
- Create, update, delete organizations
- Switch active organization (persist to config)
- Add/remove members with role-based access

**Acceptance Criteria:**
- `agentbrain org list/me/get/create/update/delete` commands work
- `agentbrain org members <id>` returns member list with roles
- `agentbrain org switch <id>` updates config file atomically
- Member operations support role assignment (owner/admin/member/viewer)

#### FR-2: Connector Management
- CRUD operations for data connectors
- Test connector connectivity and configuration
- Introspect databases, schemas, tables, columns
- Share connectors with other users
- Manage connector subtypes

**Acceptance Criteria:**
- `agentbrain connector list/get/create/update/delete` functional
- `agentbrain connector test <id>` validates connection with provided config
- `agentbrain connector databases/schemas/tables/columns <id>` return correct hierarchy
- Sharing system creates/lists/revokes access
- Connector subtype CRUD (`agentbrain cs`) works

#### FR-3: Knowledge Base Versioning
- Create and manage knowledge bases
- Track versions with diff/rollback capability
- Share knowledge bases with users/groups
- List and retrieve specific versions

**Acceptance Criteria:**
- `agentbrain knowledge create/update/delete/get` operations complete
- `agentbrain knowledge versions <id>` lists all versions
- `agentbrain knowledge rollback <id> <versionId>` restores state
- Sharing system compatible with org roles

#### FR-4: Workflow Orchestration
- Define workflows with cron schedules
- Add, update, remove workflow steps
- Execute workflows on-demand or by schedule
- Monitor runs in real-time via SSE streaming
- Cancel running workflows

**Acceptance Criteria:**
- `agentbrain workflow create/update/delete/list/get` work
- `agentbrain workflow steps` manages workflow operators
- `agentbrain workflow run <id>` triggers execution
- `agentbrain workflow logs <id> <runId>` streams SSE output in real-time
- `agentbrain workflow cancel <id> <runId>` gracefully stops execution

#### FR-5: Permission & Governance
- Create permission groups with rule definitions
- Assign users to groups
- Verify user permissions before operations
- List all active rules for a group

**Acceptance Criteria:**
- `agentbrain permission-group` CRUD operations
- `agentbrain permission-group rules create/delete` functional
- `agentbrain permission-group verify-permission` returns boolean
- Rules support action (read/write/delete/admin) + resource (connector/knowledge/workflow)

#### FR-6: Categories & Tags
- CRUD operations for entity categories
- Tree view of category hierarchy
- Tag management (create, list, delete)
- Associate tags with entities

**Acceptance Criteria:**
- `agentbrain category list/tree/get/create/update/delete` work
- `agentbrain tag list/get/create/update/delete` work
- Tree output shows parent-child relationships

#### FR-7: Search & Audit
- Cross-entity search across organizations
- Query execution logs with filtering
- Search by name, type, status

**Acceptance Criteria:**
- `agentbrain search --query <term>` returns matching entities
- `agentbrain query-log list/get` returns execution history
- Results filterable by date, status, user

#### FR-8: Configuration Management
- Interactive setup wizard for initial configuration
- Persistent config at ~/.agentbrain/config.json
- Environment variable overrides
- CLI flag overrides
- View and update individual config keys

**Acceptance Criteria:**
- `agentbrain config init` wizard works interactively for API URL, API Key, and Org ID
- `agentbrain config get/set/list` commands work
- Config file has mode 0600 (user-readable only)
- Resolution order: defaults < file < env < CLI flags
- Environment variables: AGENTBRAIN_API_KEY, AGENTBRAIN_API_URL, AGENTBRAIN_ORG_ID, AGENTBRAIN_OUTPUT, AGENTBRAIN_TIMEOUT

### Non-Functional Requirements

#### NFR-1: Authentication & Security
- All requests include X-API-Key header
- Organization context via X-Org-ID header
- Config file protected with restrictive permissions
- Mask API keys in output/logs

**Acceptance Criteria:**
- Missing API key returns 401 with clear error
- X-Org-ID automatically added from config
- Config file created with mode 0600
- `agentbrain config list` shows apiKey as "sk_l****4k" not full value

#### NFR-2: Error Handling
- User-friendly error messages for common failures
- Full context in verbose mode (`--verbose`)
- Exit codes (0 success, 1 error, 2 invalid usage)

**Acceptance Criteria:**
- 404 errors suggest valid resource IDs
- 401 errors guide to API key setup
- Timeout errors suggest config adjustment
- `--verbose` shows HTTP method, URL, duration, raw response

#### NFR-3: Output Formatting
- Auto-detect TTY for human-readable output
- Force JSON for scripts/pipes
- Support YAML and table formats
- Customizable column selection

**Acceptance Criteria:**
- Terminal → table format with colors
- Pipe → JSON format (--output detection works)
- All data structures serialize to JSON/YAML
- Column headers properly styled

#### NFR-4: Performance
- SSE streaming for large log outputs (no buffering)
- Request timeout 30s default, configurable
- Connection pooling via Node built-in fetch

**Acceptance Criteria:**
- Workflow logs stream without memory growth
- Timeouts trigger abort signals
- No memory leaks on repeated operations

#### NFR-5: Backwards Compatibility
- Maintain API contract with AgentBrain backend
- Support response envelope unwrapping (auto-extract from { data: T })
- Handle pagination gracefully

**Acceptance Criteria:**
- API schema changes don't break CLI without major version bump
- Paginated responses display correct totals

## Architecture Overview

### Core Components

1. **Command Router** (`src/index.ts`) — Commander.js program with 10+ command groups
2. **HTTP Client** (`src/client/http-client.ts`) — Fetch-based API client with auth, SSE, timeouts
3. **Config Manager** (`src/config/`) — File-based config with env var and CLI overrides
4. **Output Formatter** (`src/formatters/`) — Multi-format output (JSON, YAML, table)
5. **Command Handlers** (`src/commands/`) — 10 command modules (org, connector, knowledge, workflow, etc.)
6. **Type Definitions** (`src/types/api-types.ts`) — Complete API response types

### Request Flow

```
User Input
    ↓
Commander Parser
    ↓
Global Options + Command-Specific Args
    ↓
Config Resolution (defaults < file < env < CLI)
    ↓
ApiClient (auth headers added)
    ↓
HTTP Request → AgentBrain API (/v1/cms/*)
    ↓
Response Handling (unwrap envelope, parse)
    ↓
Output Formatter (TTY detection, JSON/table/YAML)
    ↓
Console Output
```

## Success Criteria

### Version 0.1.0 (Current)
- [x] All 10 command groups functional
- [x] Configuration system working
- [x] Output formatting (JSON/table/YAML)
- [x] Error handling with user-friendly messages
- [x] SSE streaming for workflow logs
- [x] TypeScript compilation to ESM bundle
- [ ] Comprehensive unit tests (in progress)
- [ ] Integration tests for all commands

### Version 0.2.0 (Planned)
- [ ] Batch operations (bulk import/export)
- [ ] Configuration templates
- [ ] Plugin system for custom commands
- [ ] Shell completions (bash, zsh, fish)
- [ ] Interactive mode for complex operations
- [ ] Audit logging to file
- [ ] 80%+ code coverage

### Version 1.0.0 (Roadmap)
- [ ] npm registry publication
- [ ] GoClaw MCP integration for Claude/IDE usage
- [ ] Docker image with AgentBrain CLI pre-installed
- [ ] Terraform provider
- [ ] Kubectl plugin
- [ ] Enterprise support & SLA

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| commander | ^14.0.3 | CLI argument parsing & command routing |
| chalk | ^5.6.2 | Terminal colors & styling |
| cli-table3 | ^0.6.5 | ASCII table formatting |
| yaml | ^2.8.2 | YAML serialization |
| typescript | ^5.9.3 | Type checking & transpilation |
| tsup | ^8.5.1 | ESM bundling |
| vitest | ^4.0.18 | Unit testing |

## Platform & Constraints

- **Runtime:** Node.js 20+
- **Build Output:** 39.5 KB ESM bundle
- **Package Manager:** pnpm 10.22.0
- **Module Type:** ESM (no CommonJS)
- **Platforms:** Linux, macOS, Windows
- **License:** MIT

## Integration Points

### AgentBrain API
- Base URL: https://api.agentbrain.sh (configurable)
- Version: /v1/cms/*
- Auth: X-API-Key header
- Organization Context: X-Org-ID header
- Response Envelope: { data: T } (auto-unwrapped)

### Future Integrations
- **GoClaw MCP** — Model Context Protocol for Claude integration
- **Kubernetes** — Native kubectl plugin
- **Terraform** — Official provider for IaC
- **Docker** — Official container image

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|-----------|
| API schema changes | High | Maintain API types with tests, document breaking changes |
| Lost API key in config | Critical | File permissions 0600, key masking, docs warning |
| Network failures | Medium | Timeout handling, clear error messages, retry guidance |
| SSE stream hangs | Medium | Connection timeout, graceful cleanup, test coverage |
| Large result sets | Medium | Streaming for logs, pagination support documented |

## Next Steps

1. **Testing** — Delegate to tester agent for unit/integration tests
2. **Documentation** — Architecture deep-dives, API reference, examples
3. **Beta Testing** — Internal users provide feedback, real-world use cases
4. **npm Publication** — Publish to npm registry with release automation
5. **GoClaw Integration** — Enable Claude IDE usage via MCP protocol
