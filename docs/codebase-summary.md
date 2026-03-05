# AgentBrain CLI - Codebase Summary

## Project Statistics

| Metric | Value |
|--------|-------|
| Total TypeScript Files | 20 |
| Total Source Lines of Code | 1,737 |
| Bundle Size | 39.5 KB (ESM) |
| Node.js Version | 20+ |
| Package Manager | pnpm 10.22.0 |
| Build Tool | tsup |
| Test Framework | vitest |

## Directory Structure

```
agentbrain-cli/
├── src/
│   ├── index.ts                      (38 LOC) Entry point & CLI setup
│   ├── config/
│   │   ├── config-schema.ts          (28 LOC) Config interface & defaults
│   │   └── config-manager.ts         (109 LOC) File I/O, env var resolution
│   ├── client/
│   │   ├── api-error.ts              (34 LOC) Error class + messages
│   │   └── http-client.ts            (158 LOC) HTTP client, auth, SSE
│   ├── commands/                     (10 files, ~925 LOC total)
│   │   ├── config-command.ts         (75 LOC) config get/set/list/init
│   │   ├── org-command.ts            (110 LOC) organization CRUD + members
│   │   ├── connector-command.ts      (181 LOC) connector ops + introspection
│   │   ├── connector-subtype-command.ts (57 LOC) subtype management
│   │   ├── knowledge-command.ts      (125 LOC) knowledge base versioning
│   │   ├── workflow-command.ts       (186 LOC) workflow + steps + execution
│   │   ├── search-command.ts         (19 LOC) cross-entity search
│   │   ├── query-log-command.ts      (29 LOC) execution logs
│   │   ├── permission-command.ts     (94 LOC) permission groups + rules
│   │   ├── category-command.ts       (73 LOC) category hierarchy
│   │   └── tag-command.ts            (64 LOC) tag management
│   ├── formatters/
│   │   └── output-formatter.ts       (90 LOC) JSON/YAML/table formatting
│   ├── types/
│   │   └── api-types.ts              (178 LOC) API response interfaces
│   └── utils/
│       ├── global-options.ts         (31 LOC) --output, --org, --api-* flags
│       └── command-helpers.ts        (60 LOC) createClient, fetchAndPrint helpers
├── dist/                             Built ESM bundle (39.5 KB)
├── package.json                      Project metadata, dependencies
├── tsconfig.json                     TypeScript compiler config
├── tsup.config.ts                    Bundle configuration
├── pnpm-lock.yaml                    Dependency lock file
├── .gitignore                        Git ignore patterns
└── .npmignore                        npm publish ignore patterns
```

## File Descriptions

### Entry Point & Setup

**src/index.ts** (38 LOC)
- Imports and registers all 10 command groups
- Creates Commander program instance
- Sets version (0.1.0) and description
- Delegates global option registration to `global-options.ts`
- Final `program.parse()` triggers command execution

### Configuration System

**src/config/config-schema.ts** (28 LOC)
```typescript
interface AgentBrainConfig {
  apiUrl: string;           // API endpoint
  apiKey: string;           // Authentication key
  orgId: string;            // Default organization
  output: "json" | "table" | "yaml";
  timeout: number;          // Request timeout (ms)
}
```

Provides:
- `DEFAULT_CONFIG` — hardcoded defaults
- `ENV_VAR_MAP` — env var names for each config key
- `VALID_CONFIG_KEYS` — whitelist for validation

**src/config/config-manager.ts** (109 LOC)

Core functions:
- `getConfig(overrides)` — Resolve config with priority: defaults < file < env < CLI
- `setConfigValue(key, value)` — Write single key to ~/.agentbrain/config.json (mode 0600)
- `getConfigValue(key)` — Read single resolved value
- `listConfig()` — Return all keys with source info (config file, env var, or default)

Resolution flow:
```
1. Load ~/.agentbrain/config.json
2. Load AGENTBRAIN_* env vars
3. Merge with CLI overrides
4. Apply defaults for missing keys
```

File protection: `chmodSync(CONFIG_FILE, 0o600)` restricts to user-only access.

### HTTP Client

**src/client/api-error.ts** (34 LOC)

`ApiError` class extends Error:
```typescript
class ApiError extends Error {
  constructor(
    public statusCode: number,
    message: string,
    public data?: unknown
  ) {}
}
```

Provides user-friendly error messages:
- 401 → "Unauthorized. Please set API key with: agentbrain config set apiKey"
- 404 → "Not found. Please verify the resource ID."
- 408 → "Request timeout. Increase timeout with: agentbrain config set timeout"

**src/client/http-client.ts** (158 LOC)

`ApiClient` class:
- Builds base URL: `{apiUrl}/v1/cms`
- Auto-adds headers: `X-API-Key`, `X-Org-ID`, `Content-Type: application/json`
- Methods: `get<T>(path, params)`, `post<T>(path, body)`, `put<T>(path, body)`, `delete<T>(path)`

Special features:
- **Response unwrapping** — Automatically extracts from `{ data: T }` envelope
- **SSE streaming** — `stream(path, onEvent)` for real-time workflow logs
- **Timeout handling** — AbortController with configurable timeout
- **Verbose logging** — Stderr output of HTTP method, URL, status, duration

### Output Formatting

**src/formatters/output-formatter.ts** (90 LOC)

`formatOutput(data, format, columns?)` supports:

| Format | Output | Use Case |
|--------|--------|----------|
| json | Pretty-printed JSON | Scripts, pipes, machines |
| table | CLI-table3 formatted | Terminal (default for TTY) |
| yaml | YAML serialization | Kubernetes, config files |

Auto-detection: `resolveOutputFormat()` returns "table" for TTY, "json" for pipes.

Table formatting:
- Single object → key-value pairs
- Array → rows with columns (auto-inferred or explicit)
- Color styling with chalk
- Customizable column widths and transforms

### API Type Definitions

**src/types/api-types.ts** (178 LOC)

Defines all API response types:

**Base:**
```typescript
interface BaseEntity {
  id: string;
  created_at: string;
  updated_at: string;
}

interface ApiResponse<T> { data: T; message?: string; }
interface PaginatedResponse<T> { data: T[]; total: number; page: number; limit: number; }
```

**Entities:**
- `Organization` extends BaseEntity — name, slug, type, status, created_by
- `OrgMember` — org_id, user_id, role (owner/admin/member/viewer), status, joined_at
- `Connector` — type, subtype, metadata, visibility, status
- `ConnectorSubtype` — config schema, sort order
- `Knowledge` — title, description, versions
- `Workflow` — cron_schedule, enabled, steps
- `WorkflowRun` — status, started_at, completed_at, triggered_by
- `PermissionGroup`, `PermissionRule` — action, resource, conditions
- `Category`, `Tag` — name, slug, sort_order
- `QueryLog` — query, executed_at, user_id

### Command Modules

**src/commands/org-command.ts** (110 LOC)
- CRUD: list, me, get, create, update, delete
- Members: members, add-member
- Switch: switch (persists orgId to config file)
- Table columns: ID, Name, Slug, Type, Status

**src/commands/connector-command.ts** (181 LOC)
- CRUD: list, my, get, create, update, delete
- Test: test, test-config (validate connection)
- Introspection: databases, schemas, tables, columns, data, counts
- Sharing: share (list/create/delete)
- Table columns: ID, Name, Type, Subtype, Status

**src/commands/knowledge-command.ts** (125 LOC)
- CRUD: list, get, create, update, delete
- Versions: versions, version, rollback
- Sharing: share (list/create/delete)
- Table columns: ID, Title, Description, Status

**src/commands/workflow-command.ts** (186 LOC)
- CRUD: list, get, create, update, delete
- Steps: steps list, steps create, steps update, steps delete
- Execution: run, runs, run-detail, run-steps, cancel
- Logs: logs (SSE streaming with real-time output)
- Table columns: ID, Name, Enabled, Schedule, Status

**src/commands/permission-command.ts** (94 LOC)
- CRUD: list, get, create, update, delete (permission groups)
- Users: users (list group members)
- Rules: rules (list), rules create, rules delete
- Verify: verify-permission (action + resource check)

**src/commands/category-command.ts** (73 LOC)
- CRUD: list, get, create, update, delete
- Hierarchy: tree (displays parent-child structure)

**src/commands/tag-command.ts** (64 LOC)
- CRUD: list, get, create, update, delete
- Used for entity labeling

**src/commands/connector-subtype-command.ts** (57 LOC)
- CRUD: list, get, create, delete (aliases: cs)

**src/commands/search-command.ts** (19 LOC)
- `search --query <term>` — Batch cross-entity search

**src/commands/query-log-command.ts** (29 LOC)
- `query-log list` — Query execution history
- `query-log get <id>` — Query details

### Utility Modules

**src/utils/global-options.ts** (31 LOC)

Registers global flags on program:
- `--api-url <url>` — Override apiUrl
- `--api-key <key>` — Override apiKey
- `--org <id>` — Override orgId
- `--output <fmt>` — Output format (json, table, yaml)
- `--verbose` — Enable debug logging

**src/utils/command-helpers.ts** (60 LOC)

Helper functions:
- `createClient(cmd)` — Instantiate ApiClient from command context
- `fetchAndPrint<T>(cmd, apiFn, columns?)` — Fetch data and format output
- `withErrorHandler(fn)` — Wrap async handlers with try-catch and ApiError formatting
- `getOutputFormat(cmd)` — Resolve output format with TTY detection

## Build & Bundle

**tsup.config.ts**
```typescript
export default defineConfig({
  entry: ["src/index.ts"],
  format: ["esm"],
  shims: true,
  minify: true,
  splitting: false,
  outDir: "dist",
  target: "node20",
});
```

Output: `dist/index.js` (39.5 KB, ESM, minified)

**package.json bin:**
```json
{
  "bin": {
    "agentbrain": "./dist/index.js"
  }
}
```

Executable installed as `agentbrain` after `npm install -g`.

## Dependencies Analysis

| Package | Size | Purpose | Risk |
|---------|------|---------|------|
| commander | 24 KB | CLI parsing & routing | Low (stable, widely used) |
| chalk | 8 KB | Terminal colors | Low (maintenance only) |
| cli-table3 | 15 KB | ASCII tables | Low (stable) |
| yaml | 60 KB | YAML serialization | Low (standard) |

No external HTTP library — uses Node 18+ built-in `fetch`.

Dev dependencies (not bundled):
- typescript — Type checking
- tsup — Bundling
- vitest — Testing
- @types/node — Type definitions

## Patterns & Conventions

### Command Registration

All commands follow pattern:
```typescript
export function register{Resource}Command(program: Command): void {
  const resource = program.command("{name}").alias("{abbr}").description("{desc}");

  resource
    .command("list")
    .action(withErrorHandler(async (cmd) => {
      await fetchAndPrint<T[]>(cmd, (c) => c.get("/path"));
    }));
}
```

Benefits:
- Consistent error handling via `withErrorHandler`
- Automatic output formatting via `fetchAndPrint`
- CLI client creation handled by `createClient`

### Configuration Resolution

```typescript
// In command handler:
const { client, output } = createClient(cmd);
const config = getConfig({
  apiKey: cmd.opts().apiKey,
  apiUrl: cmd.opts().apiUrl,
  orgId: cmd.opts().org,
  output: cmd.opts().output,
});
```

Priority order enforced in `config-manager.ts`:
```
CLI flags > env vars > config file > defaults
```

### Error Handling

Wrapped handlers catch and format errors:
```typescript
withErrorHandler(async (cmd) => {
  try {
    // command logic
  } catch (err) {
    if (err instanceof ApiError) {
      console.error(chalk.red(`Error ${err.statusCode}: ${err.message}`));
      process.exit(1);
    }
    throw err;
  }
})
```

### Output Formatting

Smart TTY detection:
```typescript
const format = resolveOutputFormat(cmd.opts().output);
// If format == "table" AND isTTY → colored table
// If format == "json" OR !isTTY → JSON string
```

## Testing Coverage

Current: Partial (0% in main branch)

Test structure (planned):
```
tests/
├── config/
│   └── config-manager.test.ts
├── client/
│   └── http-client.test.ts
├── commands/
│   └── org-command.test.ts
└── formatters/
    └── output-formatter.test.ts
```

## Security Considerations

1. **API Key Storage** — Config file mode 0600 (user-only readable)
2. **Key Masking** — Output shows "sk_l****4k" not full key
3. **Header Injection** — X-Org-ID prevents cross-org access
4. **Request Validation** — Command args validated by Commander
5. **Error Messages** — No sensitive data in error strings

## Performance Notes

- **Bundle Size** — 39.5 KB fits well within npm package constraints
- **Startup Time** — Sub-100ms typical (ESM module loading)
- **Memory** — Minimal (under 50 MB typical)
- **SSE Streaming** — No buffering, real-time log output via `stream()` method
- **Large Result Sets** — Pagination support in API, table formatting handles 1000+ rows

## Known Limitations

1. **Pagination** — CLI doesn't expose limit/page params (all results returned)
2. **Batch Operations** — Each command = one API request (no bulk mutations)
3. **Transactions** — No multi-command transactions or rollback
4. **Interactive Mode** — Commands are non-interactive except `config init` wizard
5. **Caching** — No client-side caching of resources
6. **Plugins** — No plugin system for custom commands

## Future Architecture Changes

Planned improvements for v0.2+:
- [ ] Modularized command factory for easier testing
- [ ] Plugin system for community commands
- [ ] Configuration profiles (dev, staging, prod)
- [ ] Command history & replay
- [ ] Batch operation mode for bulk imports
- [ ] Shell completion generation
