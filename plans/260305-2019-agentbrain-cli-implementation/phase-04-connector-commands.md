# Phase 4: Connector Commands

## Context
- Depends on: [Phase 2](./phase-02-core-infrastructure.md)
- Connectors = database connections (Postgres, MySQL, MongoDB, etc.)
- Most complex entity: CRUD + test + schema introspection + sharing + permissions

## Overview
- **Priority:** P1
- **Status:** pending
- **Effort:** 6h
- **Description:** Full connector management including CRUD, connectivity testing, schema exploration, sharing, and table permissions.

## Files to Create/Modify

```
src/commands/connector-command.ts       # Main connector commands
src/commands/connector-share-command.ts # Sharing subcommands
src/types/connector-types.ts            # Connector + schema types
```

## API Mapping

| CLI Command | Method | Endpoint |
|-------------|--------|----------|
| `connector list` | GET | /connectors |
| `connector my` | GET | /my-connectors |
| `connector counts` | GET | /connectors/counts |
| `connector get <id>` | GET | /connectors/:id |
| `connector create --type <t> --name <n> --host <h> ...` | POST | /connectors |
| `connector update <id> [flags]` | PUT | /connectors/:id |
| `connector delete <id>` | DELETE | /connectors/:id |
| `connector test <id>` | POST | /connectors/:id/test |
| `connector test-config --type <t> --host <h> ...` | POST | /connectors/test-config |
| `connector databases <id>` | GET | /connectors/:id/databases |
| `connector schemas <id>` | GET | /connectors/:id/schemas |
| `connector tables <id>` | GET | /connectors/:id/tables |
| `connector columns <id> <table>` | GET | /connectors/:id/tables/:table/columns |
| `connector data <id> <table>` | GET | /connectors/:id/tables/:table/data |
| `connector share list <id>` | GET | /connectors/:id/shares |
| `connector share add <id> [flags]` | POST | /connectors/:id/shares |
| `connector share update <id> <shareId> [flags]` | PUT | /connectors/:id/shares/:shareId |
| `connector share remove <id> <shareId>` | DELETE | /connectors/:id/shares/:shareId |

## Implementation Steps

### 1. Define types (`src/types/connector-types.ts`)
```ts
export type ConnectorType = 'postgresql' | 'mysql' | 'mongodb' | 'mssql' | 'oracle' |
  'sqlite' | 'redis' | 'elasticsearch' | 'clickhouse' | 'snowflake' | 'bigquery';

export interface Connector {
  id: string;
  name: string;
  type: ConnectorType;
  host: string;
  port: number;
  database: string;
  username: string;
  status: 'connected' | 'disconnected' | 'error';
  createdAt: string;
}

export interface TableColumn {
  name: string;
  type: string;
  nullable: boolean;
  primaryKey: boolean;
}

export interface ConnectorShare {
  id: string;
  connectorId: string;
  userId?: string;
  groupId?: string;
  permission: 'read' | 'write' | 'admin';
}
```

### 2. Implement connector command (`src/commands/connector-command.ts`)

Key patterns:
- `connector create`: Many flags for connection config (host, port, database, user, password, ssl). Group by connector type using `--type` flag.
- `connector test`: Show spinner while testing, print success/failure with latency.
- `connector data <id> <table>`: Add `--limit` (default 10) and `--offset` flags for pagination.
- `connector columns`: Table format showing name, type, nullable, PK markers.

```ts
org.command('create')
  .description('Create a new connector')
  .requiredOption('--type <type>', 'Connector type (postgresql, mysql, ...)')
  .requiredOption('--name <name>', 'Display name')
  .requiredOption('--host <host>', 'Database host')
  .option('--port <port>', 'Port number')
  .option('--database <db>', 'Database name')
  .option('--username <user>', 'Username')
  .option('--password <pass>', 'Password')
  .option('--ssl', 'Enable SSL', false)
  .action(async (opts) => { ... });
```

### 3. Implement sharing subcommands
Nest under `connector share` subcommand group. Include table-permission subcommands if needed.

### 4. Table configs
- `connector list`: id, name, type, host, status
- `connector tables`: tableName, rowCount, schema
- `connector columns`: name, type, nullable (check/cross), primaryKey (star)
- `connector data`: Dynamic columns from actual data

## Todo List
- [ ] Define connector types
- [ ] Implement CRUD commands
- [ ] Implement test/test-config commands
- [ ] Implement schema introspection (databases/schemas/tables/columns/data)
- [ ] Implement sharing subcommands
- [ ] Add pagination flags to data command
- [ ] Register in index.ts
- [ ] Test with real connector

## Success Criteria
- `agentbrain connector list` shows all connectors
- `agentbrain connector test <id>` reports connectivity status
- `agentbrain connector tables <id>` lists tables
- `agentbrain connector columns <id> users` shows column details
- `agentbrain connector data <id> users --limit 5 -o json` returns JSON preview
- `agentbrain connector create --type postgresql --name mydb --host localhost --port 5432` creates connector

## Risk Assessment
- **Password handling:** Don't log passwords in verbose mode. Consider `--password-stdin` flag for piped input.
- **Large data preview:** Limit default to 10 rows, max 100.

## Security Considerations
- Mask password in all output
- `--password-stdin` reads from stdin for scripted use (avoids shell history)
- Never include connection credentials in error logs
