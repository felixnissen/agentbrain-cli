# AgentBrain CLI - Code Standards & Conventions

## TypeScript Configuration

**tsconfig.json** settings:
```json
{
  "target": "ES2020",
  "module": "ESNext",
  "lib": ["ES2020"],
  "moduleResolution": "bundler",
  "strict": true,
  "skipLibCheck": true,
  "declaration": true,
  "declarationMap": true,
  "sourceMap": true
}
```

Enforces:
- Strict null checks enabled
- All implicit `any` flagged as errors
- ESNext output for modern Node 20 runtime
- Module resolution via bundler (supports ESM imports)

## File Structure

### Naming Conventions

**TypeScript Files** — kebab-case with descriptive names
```
src/
├── config/
│   ├── config-schema.ts       # Type definitions, constants
│   └── config-manager.ts      # File I/O, config resolution
├── client/
│   ├── api-error.ts           # Error class
│   └── http-client.ts         # HTTP client implementation
├── commands/
│   ├── org-command.ts         # Organization commands
│   ├── connector-command.ts   # Connector commands
│   └── ...
├── formatters/
│   └── output-formatter.ts    # Output formatting logic
├── types/
│   └── api-types.ts           # API response types
└── utils/
    ├── command-helpers.ts     # Helper functions
    └── global-options.ts      # CLI option registration
```

**Rationale:** Long, descriptive names ensure LLM tools (grep, glob) can understand file purpose without opening them.

### Directory Organization

```
src/
├── index.ts              # Entry point only
├── config/               # Configuration system
├── client/               # HTTP client & error handling
├── commands/             # Command implementations (10 files)
├── formatters/           # Output formatting
├── types/                # TypeScript type definitions
└── utils/                # Shared utilities
```

**Max file size:** 200 LOC per file
- Larger files split by concern (e.g., connector CRUD in one file, subtype in separate)
- Commands kept modular for testability

## Code Style

### Imports

**Pattern:** Absolute imports with `.js` extension (ESM)
```typescript
import { Command } from "commander";
import { createClient } from "../utils/command-helpers.js";
import { Organization } from "../types/api-types.js";
```

**Why:** ESM requires explicit extensions; bundlers handle `.js` → `.ts` mapping.

### Interfaces & Types

**Naming:** PascalCase for interfaces
```typescript
export interface AgentBrainConfig {
  apiUrl: string;
  apiKey: string;
  orgId: string;
}

export interface Organization extends BaseEntity {
  name: string;
  slug: string;
  type?: string;
}
```

**Fields:** snake_case for API-aligned fields (matches backend)
```typescript
interface Organization {
  id: string;           // from API
  created_at: string;   // from API (snake_case)
  user_id: string;      // from API (snake_case)
  first_name: string;   // from API
}
```

**Nullable fields:** Use optional (`?`) for optional, `null` in union for nullable
```typescript
interface Connector {
  id: string;           // Required
  metadata?: Record<string, unknown>;  // Optional
  deleted_at: string | null;           // Nullable
}
```

### Classes & Functions

**Classes:** PascalCase, named exports
```typescript
export class ApiClient {
  constructor(config: AgentBrainConfig) { }
  async get<T>(path: string): Promise<T> { }
}

export class ApiError extends Error {
  constructor(public statusCode: number, message: string) {
    super(message);
  }
}
```

**Functions:** camelCase, named exports
```typescript
export function createClient(cmd: any): { client: ApiClient; output: string } {
  // implementation
}

export function formatOutput(data: unknown, format: string): string {
  // implementation
}

// Private functions: prefix with underscore
function _buildUrl(path: string, params?: Record<string, string>): string {
  // implementation
}
```

### Variables & Constants

**Constants:** UPPER_SNAKE_CASE at module level
```typescript
const DEFAULT_API_URL = "https://api.agentbrain.sh";
const REQUEST_TIMEOUT_MS = 30000;
const CONFIG_DIR = join(homedir(), ".agentbrain");

export const ENV_VAR_MAP: Record<string, string> = {
  apiUrl: "AGENTBRAIN_API_URL",
  apiKey: "AGENTBRAIN_API_KEY",
};
```

**Variables:** camelCase
```typescript
const config = getConfig();
const response = await client.get("/organizations");
let retryCount = 0;
```

### Comments & Documentation

**Module-level comments:** Explain module purpose
```typescript
// AgentBrain HTTP client with auth, error handling, and SSE streaming
export class ApiClient { }

// Format data according to output format (json, yaml, or table)
export function formatOutput(data: unknown, format: string): string { }
```

**Inline comments:** Explain non-obvious logic
```typescript
// Auto-detect TTY: non-TTY defaults to json for machine consumption
export function resolveOutputFormat(explicit?: string): "json" | "table" | "yaml" {
  if (explicit) return explicit as "json" | "table" | "yaml";
  return process.stdout.isTTY ? "table" : "json";  // Detects terminal vs pipe
}

// Unwrap envelope if present: { data: T } -> T
if (data && typeof data === "object" && "data" in (data as Record<string, unknown>)) {
  return (data as Record<string, unknown>).data as T;
}
```

**TODO/FIXME:** Use sparingly, include issue context
```typescript
// TODO: Add support for custom column widths (issue #42)
// FIXME: SSE stream hangs on network timeout (issue #18)
```

## Error Handling

### API Errors

**ApiError class:** User-friendly messages
```typescript
export class ApiError extends Error {
  constructor(
    public statusCode: number,
    message: string,
    public data?: unknown
  ) {
    super(message);
    this.name = "ApiError";
  }
}
```

**Error messages:** Clear, actionable
```typescript
// GOOD: Tells user what to do
if (statusCode === 401) {
  throw new ApiError(401, "Unauthorized. Please set API key with: agentbrain config set apiKey");
}

if (statusCode === 404) {
  throw new ApiError(404, "Not found. Please verify the resource ID.");
}

if (statusCode === 408) {
  throw new ApiError(408, `Request timed out after ${this.timeout}ms. Increase timeout with: agentbrain config set timeout`);
}

// BAD: Vague error
throw new ApiError(500, "Server error");
```

### Command Error Wrapping

**Pattern:** withErrorHandler wraps async handlers
```typescript
export function withErrorHandler(
  fn: (cmd: any, ...args: any[]) => Promise<void>
): (...args: any[]) => Promise<void> {
  return async (...args: any[]) => {
    try {
      await fn(...args);
    } catch (err) {
      if (err instanceof ApiError) {
        console.error(chalk.red(`Error ${err.statusCode}: ${err.message}`));
        if (cmd.opts().verbose && err.data) {
          console.error(chalk.dim(JSON.stringify(err.data, null, 2)));
        }
      } else {
        console.error(chalk.red(`Unexpected error: ${(err as Error).message}`));
      }
      process.exit(1);
    }
  };
}
```

**Benefits:**
- Consistent error formatting
- Colored output via chalk
- Verbose mode for debugging
- Proper exit codes

### Try-Catch Usage

**Rules:**
- Always catch in async functions (no unhandled promise rejections)
- Re-throw or handle — don't silently fail
- Use specific error types when possible

```typescript
async function loadConfigFile(): Promise<Partial<AgentBrainConfig>> {
  try {
    if (!existsSync(CONFIG_FILE)) return {};
    const raw = readFileSync(CONFIG_FILE, "utf-8");
    return JSON.parse(raw);
  } catch {
    // Silently return empty config on read/parse errors
    // User will get helpful message when trying to use missing apiKey
    return {};
  }
}
```

## API Integration Patterns

### Client Creation

**Pattern:** createClient helper centralizes config resolution
```typescript
export function createClient(cmd: any): { client: ApiClient; output: string } {
  const config = getConfig({
    apiKey: cmd.opts().apiKey,
    apiUrl: cmd.opts().apiUrl,
    orgId: cmd.opts().org,
    output: cmd.opts().output,
    timeout: cmd.opts().timeout,
  });

  const client = new ApiClient(config, cmd.opts().verbose);
  const output = resolveOutputFormat(config.output);

  return { client, output };
}
```

### API Calls

**Pattern:** fetchAndPrint centralizes HTTP + formatting
```typescript
export async function fetchAndPrint<T>(
  cmd: any,
  apiFn: (client: ApiClient) => Promise<T>,
  columns?: TableColumnDef[]
): Promise<void> {
  const { client, output } = createClient(cmd);
  const data = await apiFn(client);
  printOutput(data, output, columns);
}
```

**Usage:**
```typescript
org
  .command("list")
  .action(withErrorHandler(async (cmd) => {
    await fetchAndPrint<Organization[]>(
      cmd,
      (c) => c.get("/organizations"),
      ORG_COLUMNS  // Optional: custom columns
    );
  }));
```

### Response Handling

**Pattern:** Auto-unwrap envelope in ApiClient
```typescript
private async request<T>(method: string, url: string, body?: unknown): Promise<T> {
  const response = await fetch(url, { /* ... */ });
  const text = await response.text();
  const data = JSON.parse(text);  // May throw if invalid JSON

  if (!response.ok) {
    throw new ApiError(response.status, (data as any)?.error ?? response.statusText);
  }

  // Unwrap envelope: { data: T } -> T
  if (data && typeof data === "object" && "data" in data) {
    return data.data as T;
  }
  return data as T;
}
```

**Benefit:** Commands don't need to know about envelope structure.

## Output Formatting Conventions

### Table Formatting

**Column definitions:** Explicit for important tables
```typescript
const ORG_COLUMNS = [
  { key: "id", header: "ID" },
  { key: "name", header: "Name" },
  { key: "slug", header: "Slug" },
  { key: "type", header: "Type" },
  { key: "status", header: "Status" },
];

const MEMBER_COLUMNS = [
  { key: "id", header: "ID" },
  { key: "user_id", header: "User ID" },
  { key: "role", header: "Role" },
  { key: "status", header: "Status" },
  { key: "joined_at", header: "Joined" },
];
```

**Auto-inferred:** For simple object displays
```typescript
// Single object → key-value table
await fetchAndPrint<Organization>(cmd, (c) => c.get(`/organizations/${id}`));
// No columns arg = auto-infer from object keys
```

**Transforms:** Custom formatting for values
```typescript
const WORKFLOW_COLUMNS = [
  { key: "id", header: "ID" },
  { key: "enabled", header: "Enabled", transform: (v: unknown) => v ? "yes" : "no" },
  { key: "cron_schedule", header: "Schedule" },
];
```

### Output Format Detection

**Priority:**
1. Explicit `--output` flag
2. TTY detection (terminal vs pipe)
3. Config file setting
4. Default (table for TTY, json for pipes)

```typescript
export function resolveOutputFormat(explicit?: string): "json" | "table" | "yaml" {
  if (explicit) return explicit as "json" | "table" | "yaml";
  return process.stdout.isTTY ? "table" : "json";
}
```

## Configuration System Patterns

### Config Resolution

**Order enforced in getConfig():**
```typescript
return { ...DEFAULT_CONFIG, ...fileConfig, ...envConfig, ...cleanOverrides };
```

1. **Defaults** — Lowest priority
2. **File config** — ~/.agentbrain/config.json
3. **Env vars** — AGENTBRAIN_*
4. **CLI flags** — Highest priority

### Env Var Mapping

**Explicit mapping:** Prevents typos, documents all vars
```typescript
export const ENV_VAR_MAP: Record<string, string> = {
  apiUrl: "AGENTBRAIN_API_URL",
  apiKey: "AGENTBRAIN_API_KEY",
  orgId: "AGENTBRAIN_ORG_ID",
  output: "AGENTBRAIN_OUTPUT",
  timeout: "AGENTBRAIN_TIMEOUT",
};
```

### Config Persistence

**Reading and Writing:**
- `getConfigValue(key)` — Reads from config file (or defaults)
- `setConfigValue(key, value)` — Writes single key to config file
- `config init` — Interactive wizard prompts for initial setup (uses readline/promises)

**Security:** Restrict file permissions
```typescript
writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2) + "\n", "utf-8");
chmodSync(CONFIG_FILE, 0o600);  // User-only readable
```

**Masking:** Don't expose full API key
```typescript
if (key === "apiKey" && value && value.length > 8) {
  value = value.slice(0, 4) + "****" + value.slice(-4);  // sk_l****4k
}
```

## Testing Patterns

### Test Structure

**Naming:** `{module}.test.ts`
```
tests/
├── config/config-manager.test.ts
├── client/http-client.test.ts
├── commands/org-command.test.ts
└── formatters/output-formatter.test.ts
```

### Mocking Strategy

**Mock ApiClient:** Avoid network calls in tests
```typescript
import { describe, it, expect, vi } from "vitest";

describe("org-command", () => {
  it("should list organizations", async () => {
    const mockClient = {
      get: vi.fn().mockResolvedValue([
        { id: "org_1", name: "Acme Corp", status: "active" },
      ]),
    };

    await fetchAndPrint(mockCmd, (c) => c.get("/organizations"));
    expect(mockClient.get).toHaveBeenCalledWith("/organizations");
  });
});
```

### Coverage Goals

- **Unit tests** — 80%+ for business logic (config, formatting, error handling)
- **Integration tests** — Key command flows with mocked API
- **E2E tests** — Real API calls (staging environment)

## Performance Considerations

### Bundle Size

**Target:** Under 50 KB (currently 39.5 KB)

**Optimization strategies:**
- Tree-shaking unused code (tsup handles)
- Avoid large dependencies (use Node built-ins)
- Minify output (tsup configured)

### Memory Usage

**Streaming for large outputs:**
```typescript
// Don't buffer: stream logs in real-time
async stream(path: string, onEvent: (data: string) => void): Promise<void> {
  const reader = response.body?.getReader();
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    onEvent(decoder.decode(value));  // Process immediately
  }
}
```

### Request Timeouts

**Default:** 30 seconds
**Configurable:** Via `AGENTBRAIN_TIMEOUT` or `agentbrain config set timeout`

```typescript
const controller = new AbortController();
const timeoutId = setTimeout(() => controller.abort(), this.timeout);
try {
  await fetch(url, { signal: controller.signal });
} finally {
  clearTimeout(timeoutId);
}
```

## Security Best Practices

### Secrets Management

1. **API Keys** — Stored in config file (mode 0600)
2. **No hardcoded keys** — Use env vars or config file only
3. **Masking in output** — Never show full key in logs
4. **HTTPS only** — API URL should use https://

### Input Validation

**Command args:** Validated by Commander automatically
```typescript
.option("--role <role>", "Member role", "member")  // Constrained by choice
.option("--action <action>", "Permission action")   // May need enum validation
```

**Headers:** Automatically added by ApiClient
```typescript
this.headers["X-API-Key"] = config.apiKey;    // Always included
this.headers["X-Org-ID"] = config.orgId;      // Always included
```

### Data Sanitization

**URL encoding:** Done by `new URL()` constructor
```typescript
const url = new URL(`${this.baseUrl}${path}`);
url.searchParams.set(k, v);  // Automatically URL-encodes
```

**JSON serialization:** Safe via `JSON.stringify()`
```typescript
body: body ? JSON.stringify(body) : undefined  // No risk of injection
```

## Debugging & Logging

### Verbose Mode

**Enabled with `--verbose` flag**
```bash
agentbrain org list --verbose
```

**Outputs to stderr (doesn't pollute JSON output):**
```typescript
if (this.verbose) {
  console.error(`${method} ${url}`);              // HTTP details
  console.error(`${response.status} ... (${duration}ms)`);
  if (err.data) console.error(JSON.stringify(err.data, null, 2));
}
```

### Error Debugging

**Full context in verbose mode:**
```typescript
if (cmd.opts().verbose && err.data) {
  console.error(chalk.dim(JSON.stringify(err.data, null, 2)));
}
```

## Backwards Compatibility

### API Contract

- **Semantic versioning:** MAJOR.MINOR.PATCH
- **MAJOR:** Breaking CLI/API changes
- **MINOR:** New features, backwards-compatible
- **PATCH:** Bug fixes

### Envelope Handling

**Auto-unwrap:** Commands don't break if API changes envelope
```typescript
if (data && typeof data === "object" && "data" in data) {
  return data.data as T;  // Works for { data: T } or bare T
}
```

### Graceful Degradation

**Optional fields:** Use `?` for graceful handling
```typescript
interface Organization {
  id: string;
  name: string;
  logo_url?: string;  // Optional in older API versions
}
```
