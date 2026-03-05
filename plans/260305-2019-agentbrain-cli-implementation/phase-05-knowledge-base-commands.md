# Phase 5: Knowledge Base Commands

## Context
- Depends on: [Phase 2](./phase-02-core-infrastructure.md)
- Knowledge bases use pgvector for semantic search
- Versioning with rollback support
- Sharing similar to connectors

## Overview
- **Priority:** P1
- **Status:** pending
- **Effort:** 5h
- **Description:** Knowledge base CRUD, semantic search, version management, and sharing.

## Files to Create/Modify

```
src/commands/knowledge-command.ts       # KB commands
src/types/knowledge-types.ts            # KB types
```

## API Mapping

| CLI Command | Method | Endpoint |
|-------------|--------|----------|
| `knowledge list` | GET | /knowledges |
| `knowledge get <id>` | GET | /knowledges/:id |
| `knowledge create --name <n> [flags]` | POST | /knowledges |
| `knowledge update <id> [flags]` | PUT | /knowledges/:id |
| `knowledge delete <id>` | DELETE | /knowledges/:id |
| `knowledge versions <id>` | GET | /knowledges/:id/versions |
| `knowledge rollback <id> <versionId>` | POST | /knowledges/:id/rollback/:vid |
| `knowledge share list <id>` | GET | /knowledges/:id/shares |
| `knowledge share add <id> [flags]` | POST | /knowledges/:id/shares |
| `knowledge share update <id> <shareId> [flags]` | PUT | /knowledges/:id/shares/:shareId |
| `knowledge share remove <id> <shareId>` | DELETE | /knowledges/:id/shares/:shareId |

Note: Semantic search is handled via `agentbrain search` (Phase 7), which calls `/search` or `/mcp/search`.

## Implementation Steps

### 1. Define types (`src/types/knowledge-types.ts`)
```ts
export interface KnowledgeBase {
  id: string;
  name: string;
  description?: string;
  type: string;
  entryCount: number;
  status: 'active' | 'building' | 'error';
  createdAt: string;
  updatedAt: string;
}

export interface KBVersion {
  id: string;
  knowledgeId: string;
  version: number;
  createdAt: string;
  entryCount: number;
}

export interface KBShare {
  id: string;
  knowledgeId: string;
  userId?: string;
  groupId?: string;
  permission: 'read' | 'write' | 'admin';
}
```

### 2. Implement knowledge command
Follow same pattern as org/connector. Key specifics:
- `knowledge create`: May require file upload or content input → check API for body format
- `knowledge versions`: Show version history as table (version #, date, entry count)
- `knowledge rollback`: Confirm action with prompt (skip if `--yes` flag or non-TTY)

### 3. Sharing subcommands
Reuse sharing pattern from connector. Consider extracting a shared `createShareCommands(entityName, basePath)` helper to DRY up connector/knowledge sharing code.

### 4. DRY: Extract shared sharing command factory
```ts
// src/commands/share-command-factory.ts
export function createShareSubcommands(parentCmd: Command, entityPath: string): void {
  const share = parentCmd.command('share').description('Manage sharing');
  share.command('list <id>').action(async (id, opts) => {
    const data = await getClient(opts).get(`/${entityPath}/${id}/shares`);
    console.log(formatOutput(data, ...));
  });
  // add, update, remove follow same pattern
}
```

## Todo List
- [ ] Define knowledge base types
- [ ] Implement CRUD commands
- [ ] Implement version/rollback commands
- [ ] Extract share command factory (DRY with connector)
- [ ] Implement sharing subcommands via factory
- [ ] Register in index.ts
- [ ] Test all subcommands

## Success Criteria
- `agentbrain knowledge list` shows all KBs
- `agentbrain knowledge versions <id>` shows version history
- `agentbrain knowledge rollback <id> <vid>` confirms and rolls back
- `agentbrain knowledge share list <id>` shows shares
- Sharing code is shared with connector (no duplication)

## Risk Assessment
- **KB creation payload:** May differ significantly from simple JSON — check API for multipart/form-data needs
- **Rollback confirmation:** Need `--yes` flag for non-interactive use (GoClaw)
