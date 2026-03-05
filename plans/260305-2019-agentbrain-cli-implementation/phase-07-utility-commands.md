# Phase 7: Utility Commands

## Context
- Depends on: [Phase 2](./phase-02-core-infrastructure.md)
- Covers: search, query logs, permission groups, categories, tags
- Simpler entities — mostly list/get/create patterns

## Overview
- **Priority:** P2
- **Status:** pending
- **Effort:** 3h
- **Description:** Search, query logs, permission groups, categories, and tags commands.

## Files to Create/Modify

```
src/commands/search-command.ts           # Batch search
src/commands/query-log-command.ts        # Query log viewer
src/commands/permission-group-command.ts # Permission group mgmt
src/commands/category-command.ts         # Category CRUD + tree
src/commands/tag-command.ts              # Tag CRUD
src/types/utility-types.ts              # Types for all utility entities
```

## API Mapping

### Search
| CLI Command | Method | Endpoint |
|-------------|--------|----------|
| `search --query <q> [flags]` | POST | /search (uses auth) |
| `search --query <q> --mcp` | POST | /mcp/search (uses API key) |

### Query Logs
| CLI Command | Method | Endpoint |
|-------------|--------|----------|
| `query-log list` | GET | /query-logs |
| `query-log get <id>` | GET | /query-logs/:id |

### Permission Groups
| CLI Command | Method | Endpoint |
|-------------|--------|----------|
| `permission-group list` | GET | /permission-groups |
| `permission-group get <id>` | GET | /permission-groups/:id |
| `permission-group create [flags]` | POST | /permission-groups |
| `permission-group update <id> [flags]` | PUT | /permission-groups/:id |
| `permission-group delete <id>` | DELETE | /permission-groups/:id |

### Categories
| CLI Command | Method | Endpoint |
|-------------|--------|----------|
| `category list` | GET | /categories |
| `category tree` | GET | /categories/tree |
| `category get <id>` | GET | /categories/:id |
| `category create [flags]` | POST | /categories |
| `category update <id> [flags]` | PUT | /categories/:id |
| `category delete <id>` | DELETE | /categories/:id |

### Tags
| CLI Command | Method | Endpoint |
|-------------|--------|----------|
| `tag list` | GET | /tags |
| `tag get <id>` | GET | /tags/:id |
| `tag create --name <n>` | POST | /tags |
| `tag update <id> --name <n>` | PUT | /tags/:id |
| `tag delete <id>` | DELETE | /tags/:id |

## Implementation Steps

### 1. Search command
```ts
search.command('search')
  .description('Search across knowledge bases')
  .requiredOption('-q, --query <query>', 'Search query')
  .option('--mcp', 'Use MCP endpoint (API key auth)')
  .option('--limit <n>', 'Max results', '10')
  .option('--knowledge-id <id>', 'Filter by knowledge base')
  .action(async (opts) => {
    const endpoint = opts.mcp ? '/mcp/search' : '/search';
    const data = await client.post(endpoint, {
      query: opts.query,
      limit: parseInt(opts.limit),
      knowledgeId: opts.knowledgeId,
    });
    console.log(formatOutput(data, ...));
  });
```

### 2. Category tree
Special formatting for tree output:
```
Marketing
  Content Marketing
    Blog Posts
    Social Media
  Email Marketing
Sales
  Inbound
  Outbound
```
Use recursive indentation for table mode, nested JSON for json mode.

### 3. CRUD factory pattern
Most utility entities follow identical CRUD pattern. Extract a factory:

```ts
// src/commands/crud-command-factory.ts
export function createCrudCommand(config: {
  name: string;
  plural: string;
  endpoint: string;
  tableColumns: string[];
  createFlags: OptionConfig[];
  updateFlags: OptionConfig[];
}): Command {
  const cmd = new Command(config.name).description(`Manage ${config.plural}`);
  // Generate list, get, create, update, delete subcommands
  return cmd;
}
```

This DRYs up tags, categories, permission-groups (and possibly future entities).

## Todo List
- [ ] Define utility types
- [ ] Extract CRUD command factory
- [ ] Implement search command with --mcp flag
- [ ] Implement query-log commands
- [ ] Implement permission-group commands (via factory)
- [ ] Implement category commands + tree formatter
- [ ] Implement tag commands (via factory)
- [ ] Register all in index.ts

## Success Criteria
- `agentbrain search -q "customer data" -o json` returns search results
- `agentbrain category tree` shows indented tree
- `agentbrain tag list` shows all tags
- CRUD factory eliminates code duplication across simple entities
- `agentbrain query-log list` shows recent queries

## Risk Assessment
- **Search credits:** Each search costs credits — mention in help text
- **Tree depth:** Category tree may be deeply nested — limit rendering depth or add `--depth` flag
