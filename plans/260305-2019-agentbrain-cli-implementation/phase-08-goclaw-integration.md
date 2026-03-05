# Phase 8: GoClaw Integration

## Context
- Depends on: Phases 3-7 (all commands implemented)
- GoClaw uses shell-based custom tools: `command` template with `{{param}}` placeholders
- GoClaw tool config lives in TOML files
- Goal: provide ready-to-use tool templates + documentation

## Overview
- **Priority:** P2
- **Status:** pending
- **Effort:** 4h
- **Description:** GoClaw tool templates, integration documentation, and example configurations for using agentbrain-cli as GoClaw tools.

## Files to Create/Modify

```
docs/goclaw-integration.md             # Integration guide
tools/goclaw/                           # Tool template files
  agentbrain-search.toml
  agentbrain-connector-list.toml
  agentbrain-knowledge-search.toml
  agentbrain-workflow-run.toml
  agentbrain-connector-data.toml
examples/
  goclaw-config-snippet.toml           # Example GoClaw config with agentbrain tools
  agent-data-analyst.toml              # Example: data analyst agent using agentbrain
```

## Implementation Steps

### 1. GoClaw tool template format
Based on GoClaw's custom tool pattern:
```toml
[tool.agentbrain_search]
name = "agentbrain_search"
description = "Search AgentBrain knowledge bases for relevant information"
command = "agentbrain search --query '{{query}}' --output json"

[tool.agentbrain_search.parameters]
query = { type = "string", description = "Search query", required = true }
```

### 2. Create essential tool templates

**Priority tools for AI agents:**
1. `agentbrain_search` — Semantic search across knowledge bases
2. `agentbrain_connector_list` — List available data connectors
3. `agentbrain_connector_tables` — List tables in a connector
4. `agentbrain_connector_data` — Preview table data
5. `agentbrain_connector_columns` — Get table schema
6. `agentbrain_knowledge_list` — List knowledge bases
7. `agentbrain_workflow_run` — Execute a workflow
8. `agentbrain_org_list` — List organizations

### 3. Write integration documentation (`docs/goclaw-integration.md`)

Contents:
- Prerequisites (install agentbrain-cli, configure API key)
- Quick start (3 steps)
- Tool template reference
- Environment variable configuration
- Example agent configurations
- Troubleshooting common issues

### 4. Example agent configuration
```toml
# Agent that can explore and query databases via AgentBrain
[agent.data_analyst]
name = "Data Analyst"
model = "claude-sonnet-4-20250514"
system_prompt = """You are a data analyst with access to enterprise databases via AgentBrain.
Use the agentbrain tools to explore connectors, schemas, and data."""
tools = [
  "agentbrain_connector_list",
  "agentbrain_connector_tables",
  "agentbrain_connector_columns",
  "agentbrain_connector_data",
  "agentbrain_search",
]
```

### 5. JSON output contract documentation
Document the JSON output shape for each command so GoClaw agents can parse reliably:
- Search results: `{ results: [{ id, title, content, score }] }`
- Connector list: `{ data: [{ id, name, type, status }] }`
- Error: `{ error: true, message: "...", code: 401 }`

### 6. `agentbrain` as npx-runnable
Ensure the CLI works via `npx @agentbrain/cli search --query "..."` for environments without global install.

## Todo List
- [ ] Create GoClaw tool template TOML files
- [ ] Write integration documentation
- [ ] Create example agent configurations
- [ ] Document JSON output contracts
- [ ] Test all tool templates with GoClaw (manual)
- [ ] Add `--help` examples showing GoClaw usage patterns

## Success Criteria
- GoClaw can execute `agentbrain search --query "test" --output json` and parse result
- Tool templates are copy-pasteable into GoClaw config
- Documentation covers setup to first query in < 5 minutes
- JSON output is stable and predictable for machine parsing
- Error responses include exit codes (0=success, 1=error)

## Risk Assessment
- **GoClaw tool format changes:** Templates may need updating — keep them in a versioned directory
- **npx cold start:** First run via npx is slow (package download) — recommend global install for production
