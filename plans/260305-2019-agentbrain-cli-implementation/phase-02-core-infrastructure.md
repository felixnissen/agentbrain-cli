# Phase 2: Core Infrastructure

## Context
- Depends on: [Phase 1](./phase-01-project-setup.md)
- AgentBrain API uses `/v1/cms/` base path
- Auth: API key via `X-API-Key` header (APIKeyAuth middleware)

## Overview
- **Priority:** P1
- **Status:** pending
- **Effort:** 6h
- **Description:** HTTP client wrapper, config management, output formatters, error handling. Foundation for all commands.

## Key Insights
- API key auth is simpler than JWT — no token refresh needed
- Auto-detect piped output (no TTY) → default to JSON for machine consumption
- All API responses follow consistent envelope: `{ data, message, error }`
- Config hierarchy: CLI flags > env vars > config file > defaults

## Requirements

### Functional
- Config file at `~/.agentbrain/config.toml` (or cosmiconfig resolution)
- HTTP client handles auth, base URL, error parsing
- Output formatter supports json/table/yaml
- Global error handler with user-friendly messages

### Non-Functional
- HTTP timeout: 30s default, configurable
- Retry: 1 retry on 5xx, no retry on 4xx
- Config file permissions: 0600 (contains API key)

## Architecture

```
src/
  config/
    config-manager.ts     # Load/save/get config values
    config-schema.ts      # Config shape and defaults
  client/
    http-client.ts        # undici wrapper with auth
    api-error.ts          # Error types and parsing
  formatters/
    output-formatter.ts   # Format dispatch (json/table/yaml)
    table-formatter.ts    # cli-table3 wrapper
  types/
    api-types.ts          # Shared API response types
    common-types.ts       # Pagination, filters, etc.
  utils/
    global-options.ts     # Global CLI flags registration
    logger.ts             # Verbose logging
```

## Implementation Steps

### 1. Config Schema (`src/config/config-schema.ts`)
```ts
export interface AgentBrainConfig {
  apiUrl: string;
  apiKey: string;
  orgId: string;
  output: 'json' | 'table' | 'yaml';
  timeout: number;
}

export const DEFAULT_CONFIG: AgentBrainConfig = {
  apiUrl: 'https://api.agentbrain.sh',
  apiKey: '',
  orgId: '',
  output: 'table',
  timeout: 30000,
};
```

### 2. Config Manager (`src/config/config-manager.ts`)
- Use `cosmiconfig` with module name `agentbrain`
- Search: `.agentbrainrc`, `.agentbrainrc.toml`, `~/.agentbrain/config.toml`
- `getConfig()`: Merge defaults < file < env vars < CLI opts
- `setConfig(key, value)`: Write to `~/.agentbrain/config.toml`
- `listConfig()`: Show all resolved values with source
- Env var mapping: `AGENTBRAIN_API_URL`, `AGENTBRAIN_API_KEY`, `AGENTBRAIN_ORG_ID`

### 3. HTTP Client (`src/client/http-client.ts`)
```ts
import { request } from 'undici';

export class ApiClient {
  constructor(private config: AgentBrainConfig) {}

  async get<T>(path: string, params?: Record<string, string>): Promise<T> { ... }
  async post<T>(path: string, body?: unknown): Promise<T> { ... }
  async put<T>(path: string, body?: unknown): Promise<T> { ... }
  async delete<T>(path: string): Promise<T> { ... }

  // SSE streaming for workflow logs
  async stream(path: string, onEvent: (data: string) => void): Promise<void> { ... }
}
```

Key behaviors:
- Base URL: `${config.apiUrl}/v1/cms`
- Headers: `X-API-Key: ${config.apiKey}`, `Content-Type: application/json`
- If `orgId` set, include `X-Org-ID` header (or query param, check API)
- Parse error responses into `ApiError` with status, message, details
- Verbose mode: log method, URL, status, duration

### 4. API Error Handling (`src/client/api-error.ts`)
```ts
export class ApiError extends Error {
  constructor(
    public statusCode: number,
    public apiMessage: string,
    public details?: unknown
  ) {
    super(`[${statusCode}] ${apiMessage}`);
  }
}
```
- 401 → "Invalid API key. Run: agentbrain config set api-key <key>"
- 403 → "Permission denied. Check org access."
- 404 → "Resource not found."
- 429 → "Rate limited. Retry after X seconds."
- 5xx → "Server error. Try again later."

### 5. Output Formatter (`src/formatters/output-formatter.ts`)
```ts
export function formatOutput(data: unknown, format: string, tableConfig?: TableConfig): string {
  if (format === 'json') return JSON.stringify(data, null, 2);
  if (format === 'yaml') return yamlStringify(data);
  return formatTable(data, tableConfig);
}

// Auto-detect: if stdout is not a TTY, default to json
export function resolveOutputFormat(explicit?: string): string {
  if (explicit) return explicit;
  return process.stdout.isTTY ? 'table' : 'json';
}
```

### 6. Global Options (`src/utils/global-options.ts`)
Register on root Command:
```ts
export function addGlobalOptions(program: Command): void {
  program
    .option('-o, --output <format>', 'Output format: json | table | yaml')
    .option('--org <id>', 'Override organization ID')
    .option('--api-url <url>', 'Override API base URL')
    .option('--api-key <key>', 'Override API key')
    .option('-v, --verbose', 'Verbose output')
    .option('--no-color', 'Disable colors');
}
```

### 7. Config Command (`src/commands/config-command.ts`)
```
agentbrain config set <key> <value>
agentbrain config get <key>
agentbrain config list
agentbrain config init    # Interactive setup wizard
```
- `init`: Prompt for API URL, API key, default org (interactive)
- `set`: Validate key names, write to config file
- `get`: Print single value
- `list`: Print all resolved config as table

### 8. Wire into index.ts
- Import and register config command
- Add global options
- Add global error handler (wrap action handlers)

## Todo List
- [ ] Create config schema and defaults
- [ ] Implement config manager with cosmiconfig
- [ ] Implement HTTP client with undici
- [ ] Implement API error handling
- [ ] Implement output formatters (json, table, yaml)
- [ ] Register global CLI options
- [ ] Implement config commands (set/get/list/init)
- [ ] Wire everything into index.ts
- [ ] Test: config set/get round-trip
- [ ] Test: HTTP client error handling

## Success Criteria
- `agentbrain config set api-key test123` writes to `~/.agentbrain/config.toml`
- `agentbrain config get api-key` prints `test123`
- `agentbrain config list` shows all config with sources
- HTTP client sends correct headers, parses errors
- `--output json` flag works on any command
- Piped output auto-detects JSON format

## Risk Assessment
- **cosmiconfig TOML:** Needs `cosmiconfig-toml-loader` — verify it supports TOML write-back. Fallback: use plain JSON config.
- **undici SSE:** No built-in SSE parser — need manual event stream parsing in `stream()` method. Use line-by-line parsing of `data:` frames.

## Security Considerations
- Config file with API key: set `0600` permissions on creation
- Never log API key in verbose mode (mask it)
- Don't include API key in error messages
