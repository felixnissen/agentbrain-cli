---
title: "AgentBrain CLI Implementation"
description: "TypeScript CLI for AI agents to interact with AgentBrain enterprise data hub"
status: pending
priority: P1
effort: 40h
branch: feat/agentbrain-cli
tags: [cli, typescript, agentbrain, goclaw, api-client]
created: 2026-03-05
---

# AgentBrain CLI - Implementation Plan

## Overview

CLI tool (`@agentbrain/cli`) that wraps all AgentBrain API endpoints as shell commands. Primary consumers: GoClaw AI agents (JSON output) and humans (table output).

**Stack:** TypeScript, Commander.js, undici, tsup, pnpm

## Architecture

```
src/
  index.ts              # Entry point, Commander setup
  config/               # Config management (~/.agentbrain/)
  client/               # HTTP client, auth, error handling
  commands/             # Command modules (org, connector, kb, workflow, etc.)
  formatters/           # Output formatting (json, table, yaml)
  types/                # API types/interfaces
  utils/                # Shared utilities
```

## Phases

| # | Phase | Effort | Status | Dependencies |
|---|-------|--------|--------|--------------|
| 1 | [Project Setup](./phase-01-project-setup.md) | 3h | pending | none |
| 2 | [Core Infrastructure](./phase-02-core-infrastructure.md) | 6h | pending | Phase 1 |
| 3 | [Organization Commands](./phase-03-organization-commands.md) | 4h | pending | Phase 2 |
| 4 | [Connector Commands](./phase-04-connector-commands.md) | 6h | pending | Phase 2 |
| 5 | [Knowledge Base Commands](./phase-05-knowledge-base-commands.md) | 5h | pending | Phase 2 |
| 6 | [Workflow Commands](./phase-06-workflow-commands.md) | 5h | pending | Phase 2 |
| 7 | [Utility Commands](./phase-07-utility-commands.md) | 3h | pending | Phase 2 |
| 8 | [GoClaw Integration](./phase-08-goclaw-integration.md) | 4h | pending | Phases 3-7 |
| 9 | [Testing & CI/CD](./phase-09-testing-and-ci-cd.md) | 4h | pending | Phases 3-7 |

## Key Decisions

- **Commander.js over oclif**: Simpler, no framework lock-in, lighter bundle
- **undici over axios/node-fetch**: Built into Node, fastest HTTP client
- **tsup**: Fast esbuild-based bundler, single-file output for npm bin
- **cosmiconfig**: Standard config resolution (.agentbrainrc, config.toml, etc.)
- **API key auth only**: CLI uses API key auth (no JWT browser flows)

## Global Flags (all commands)

```
--output, -o    Output format: json | table | yaml (default: table, auto-detects piped → json)
--org           Override active organization ID
--api-url       Override API base URL
--api-key       Override API key
--verbose, -v   Verbose output (show request details)
--no-color      Disable color output
```

## Critical Path

Phase 1 → Phase 2 → Phases 3-7 (parallel) → Phase 8 → Phase 9
