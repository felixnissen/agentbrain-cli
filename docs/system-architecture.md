# AgentBrain CLI - System Architecture

## High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    User (Terminal/Shell)                      │
└────────────────────────────┬─────────────────────────────────┘
                             │
                    CLI Input (agentbrain org list)
                             │
        ┌────────────────────▼────────────────────┐
        │   Commander.js Argument Parser           │
        │ Parses command, subcommand, flags, args  │
        └────────────────┬─────────────────────────┘
                         │
        ┌────────────────▼────────────────────┐
        │    Global Options Handler            │
        │ Extracts --output, --org, --api-*   │
        └────────────────┬─────────────────────┘
                         │
        ┌────────────────▼────────────────────┐
        │   Config Resolution System           │
        │ defaults < file < env < CLI flags    │
        └────────────────┬─────────────────────┘
                         │
        ┌────────────────▼────────────────────┐
        │   Command Handler Function           │
        │ (e.g., registerOrgCommand)           │
        └────────────────┬─────────────────────┘
                         │
        ┌────────────────▼────────────────────┐
        │   Error Handler Wrapper              │
        │ try-catch, ApiError formatting       │
        └────────────────┬─────────────────────┘
                         │
        ┌────────────────▼────────────────────┐
        │   API Client Creation                │
        │ Instantiate ApiClient with config    │
        └────────────────┬─────────────────────┘
                         │
        ┌────────────────▼────────────────────┐
        │   HTTP Request (Fetch API)           │
        │ GET/POST/PUT/DELETE /v1/cms/*        │
        │ Headers: X-API-Key, X-Org-ID        │
        └────────────────┬─────────────────────┘
                         │
        ┌────────────────▼─────────────────────┐
        │   AgentBrain API (/v1/cms/*)         │
        │ (External Service)                   │
        └────────────────┬──────────────────────┘
                         │
        ┌────────────────▼────────────────────┐
        │   Response Handling                  │
        │ Status check, envelope unwrap        │
        └────────────────┬─────────────────────┘
                         │
        ┌────────────────▼────────────────────┐
        │   Output Formatting                  │
        │ JSON/YAML/Table (TTY detection)      │
        └────────────────┬─────────────────────┘
                         │
        ┌────────────────▼────────────────────┐
        │   Console Output (stdout/stderr)     │
        └────────────────────────────────────────┘
```

## Component Architecture

### Layer 1: CLI Input & Parsing

**File:** `src/index.ts`

```typescript
const program = new Command();
program
  .name("agentbrain")
  .description("CLI for AgentBrain...")
  .version("0.1.0");

addGlobalOptions(program);
registerConfigCommand(program);
registerOrgCommand(program);
// ... 8 more command registrations
program.parse();
```

**Responsibilities:**
- Create Commander program instance
- Register all command groups
- Delegate option handling
- Trigger parsing on process.argv

**Entry Points:**
- `agentbrain org list` → triggers org subcommand
- `agentbrain --help` → Commander outputs help
- `agentbrain --version` → Outputs "0.1.0"

### Layer 2: Global Options & Argument Processing

**File:** `src/utils/global-options.ts`

```typescript
export function addGlobalOptions(program: Command): void {
  program
    .option("--api-url <url>", "API endpoint")
    .option("--api-key <key>", "API key")
    .option("--org <id>", "Organization ID")
    .option("--output <format>", "Output format: json, table, yaml")
    .option("--verbose", "Enable debug logging");
}
```

**Processing:**
- Commander parses all options into `cmd.opts()`
- Global options available to all subcommands
- Values passed to config resolution system

**Example Flow:**
```bash
$ agentbrain --api-key sk_live_xxx org list --output json

cmd.opts() = {
  apiKey: "sk_live_xxx",
  output: "json",
  org: undefined,  // not provided
  // ...
}
```

### Layer 3: Configuration Resolution

**Files:** `src/config/config-schema.ts`, `src/config/config-manager.ts`

**Creating Initial Config:**
The `config init` command provides an interactive setup wizard to generate the initial config file:
```bash
$ agentbrain config init

AgentBrain CLI Setup

For on-premise deployments, enter your internal API URL.
For cloud, press Enter to use the default.

API URL [https://api.agentbrain.sh]:
API Key: sk_live_xxxxx
Default Organization ID (optional): org_xxxxx

Configuration saved to ~/.agentbrain/config.json
```

**Resolution Priority:**
```
Priority (highest to lowest):
1. CLI Flags (cmd.opts())
2. Environment Variables (process.env)
3. Config File (~/.agentbrain/config.json)
4. Defaults
```

**Implementation:**

```typescript
export function getConfig(cliOverrides: Partial<AgentBrainConfig> = {}): AgentBrainConfig {
  const fileConfig = loadConfigFile();      // Parse JSON from ~/.agentbrain/config.json
  const envConfig = loadEnvConfig();        // Read AGENTBRAIN_* env vars
  const cleanOverrides = /* filter undefined */;

  return { ...DEFAULT_CONFIG, ...fileConfig, ...envConfig, ...cleanOverrides };
}
```

**Config Structure:**
```typescript
interface AgentBrainConfig {
  apiUrl: string;           // "https://api.agentbrain.sh"
  apiKey: string;           // "sk_live_xxxxx"
  orgId: string;            // "org_xxxxx"
  output: "json" | "table" | "yaml";
  timeout: number;          // 30000 (ms)
}
```

**Env Var Mapping:**
```
apiUrl      ← AGENTBRAIN_API_URL
apiKey      ← AGENTBRAIN_API_KEY
orgId       ← AGENTBRAIN_ORG_ID
output      ← AGENTBRAIN_OUTPUT
timeout     ← AGENTBRAIN_TIMEOUT
```

**File Persistence:**
```
~/.agentbrain/config.json (mode 0600)

{
  "apiUrl": "https://api.agentbrain.sh",
  "apiKey": "sk_live_xxxxx",
  "orgId": "org_xxxxx",
  "output": "table",
  "timeout": 30000
}
```

### Layer 4: Command Handler & Error Wrapping

**Pattern:** Every command wrapped with `withErrorHandler`

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
        if (verbose) console.error(JSON.stringify(err.data, null, 2));
      } else {
        console.error(chalk.red(`Unexpected error: ${(err as Error).message}`));
      }
      process.exit(1);
    }
  };
}
```

**Example Command:**
```typescript
org
  .command("list")
  .description("List all organizations")
  .action(withErrorHandler(async (cmd) => {
    await fetchAndPrint<Organization[]>(cmd, (c) => c.get("/organizations"));
  }));
```

**Flow:**
1. User enters `agentbrain org list`
2. Commander routes to handler function
3. `withErrorHandler` wraps the async function
4. Handler calls `fetchAndPrint`
5. If error occurs → caught, formatted, exit(1)
6. On success → output printed, exit(0)

### Layer 5: API Client Creation & HTTP Requests

**File:** `src/client/http-client.ts`

```typescript
export class ApiClient {
  private baseUrl: string;           // {apiUrl}/v1/cms
  private headers: Record<string, string>;
  private timeout: number;
  private verbose: boolean;

  constructor(config: AgentBrainConfig, verbose = false) {
    this.baseUrl = `${config.apiUrl.replace(/\/$/, "")}/v1/cms`;
    this.headers = {
      "Content-Type": "application/json",
      "Accept": "application/json",
      "X-API-Key": config.apiKey,    // Auth
      "X-Org-ID": config.orgId,      // Org context
    };
    this.timeout = config.timeout;
    this.verbose = verbose;
  }

  async get<T>(path: string, params?: Record<string, string>): Promise<T> {
    const url = this.buildUrl(path, params);
    return this.request<T>("GET", url);
  }

  async post<T>(path: string, body?: unknown): Promise<T> {
    const url = this.buildUrl(path);
    return this.request<T>("POST", url, body);
  }

  async stream(path: string, onEvent: (data: string) => void): Promise<void> {
    // SSE streaming for workflow logs
  }

  private async request<T>(method: string, url: string, body?: unknown): Promise<T> {
    // Actual fetch call with timeout, error handling
  }
}
```

**Request Flow:**
```
1. buildUrl(path, params)
   ↓
2. fetch(url, { headers, body, signal })
   ↓
3. Handle response.ok
   ↓
4. Parse JSON, check for error fields
   ↓
5. Unwrap envelope: { data: T } → T
   ↓
6. Return typed result
```

**Timeout Handling:**
```typescript
const controller = new AbortController();
const timeoutId = setTimeout(() => controller.abort(), this.timeout);

try {
  await fetch(url, { signal: controller.signal });
} finally {
  clearTimeout(timeoutId);
}
```

### Layer 6: Output Formatting & Display

**File:** `src/formatters/output-formatter.ts`

```typescript
export function formatOutput(
  data: unknown,
  format: string,
  columns?: TableColumnDef[]
): string {
  switch (format) {
    case "json":
      return JSON.stringify(data, null, 2);
    case "yaml":
      return yamlStringify(data);
    case "table":
    default:
      return formatTable(data, columns);
  }
}
```

**TTY Auto-Detection:**
```typescript
export function resolveOutputFormat(explicit?: string): "json" | "table" | "yaml" {
  if (explicit) return explicit as "json" | "table" | "yaml";
  return process.stdout.isTTY ? "table" : "json";
}
```

**Table Formatting:**
```
Input: Array<Organization>
  ↓
Infer columns from keys (or use explicit columns)
  ↓
Create cli-table3 instance with headers
  ↓
Add rows with chalk colors
  ↓
Output: Formatted ASCII table
```

**Example Output:**
```bash
$ agentbrain org list --output table

┌────────┬──────────────┬──────────┬────────────┬────────┐
│ ID     │ Name         │ Slug     │ Type       │ Status │
├────────┼──────────────┼──────────┼────────────┼────────┤
│ org_1  │ Acme Corp    │ acme     │ enterprise │ active │
│ org_2  │ Beta Labs    │ beta     │ startup    │ active │
└────────┴──────────────┴──────────┴────────────┴────────┘
```

## Authentication & Authorization Flow

```
┌─────────────────────────────────────────┐
│ User provides credentials               │
│ - apiKey (via flag, env var, or config) │
│ - orgId (via flag, env var, or config)  │
└──────────────────┬──────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │ Create ApiClient      │
        │ with config           │
        └──────────┬────────────┘
                   │
        ┌──────────▼──────────────────┐
        │ Add headers to ALL requests  │
        │ X-API-Key: {apiKey}          │
        │ X-Org-ID: {orgId}            │
        └──────────┬──────────────────┘
                   │
        ┌──────────▼──────────────────┐
        │ Send to AgentBrain API       │
        │ /v1/cms/organizations/...    │
        └──────────┬──────────────────┘
                   │
        ┌──────────▼──────────────────┐
        │ API validates headers        │
        │ Returns 401 if invalid key   │
        │ Filters by X-Org-ID          │
        └──────────┬──────────────────┘
                   │
        ┌──────────▼──────────────────┐
        │ Response to CLI              │
        └──────────────────────────────┘
```

**Security Features:**
- API key stored in config file (mode 0600)
- Headers set automatically for every request
- X-Org-ID prevents cross-org data access
- No sensitive data in error messages (default)
- Verbose mode for debugging (shows raw response)

## SSE Streaming for Workflow Logs

**File:** `src/client/http-client.ts` → `stream()` method

```
User runs: agentbrain workflow logs <id> <runId>
                ↓
           fetchAndPrint calls:
           client.stream("/workflows/{id}/runs/{runId}/logs", onEvent)
                ↓
         Fetch with Accept: text/event-stream
                ↓
         Response body is readable stream
                ↓
         Read chunks from stream
                ↓
         Parse SSE format: "data: {json}"
                ↓
         onEvent callback fires for each event
                ↓
         Print to stdout in real-time
                ↓
         Stream closes when workflow completes
```

**Implementation:**
```typescript
async stream(path: string, onEvent: (data: string) => void): Promise<void> {
  const response = await fetch(url, {
    headers: { ...this.headers, Accept: "text/event-stream" }
  });

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        onEvent(line.slice(6));  // Call with JSON data
      }
    }
  }
}
```

**Advantages:**
- No buffering → low memory footprint
- Real-time output → user sees logs as they happen
- Connection cleanup → properly releases resources

## Configuration File Management

```
~/.agentbrain/config.json
├── Created on first `agentbrain config set`
├── Permissions: 0600 (user-only readable)
├── Format: JSON
└── Persisted across sessions
```

**Full Resolution Example:**

```bash
# 1. Start with defaults
Config = {
  apiUrl: "https://api.agentbrain.sh",
  apiKey: "",
  orgId: "",
  output: "table",
  timeout: 30000
}

# 2. Check ~/.agentbrain/config.json
File contains: { apiKey: "sk_live_xxx", orgId: "org_123" }
Config = { ..., apiKey: "sk_live_xxx", orgId: "org_123", ... }

# 3. Check environment variables
Env has: AGENTBRAIN_OUTPUT=json
Config = { ..., output: "json", ... }

# 4. Apply CLI flags
User ran: agentbrain --api-key sk_staging_yyy org list
Config = { ..., apiKey: "sk_staging_yyy", ... }

# Final resolved config:
{
  apiUrl: "https://api.agentbrain.sh",
  apiKey: "sk_staging_yyy",           (from CLI)
  orgId: "org_123",                   (from file)
  output: "json",                     (from env)
  timeout: 30000                      (default)
}
```

## Command Execution Flow Example

```bash
$ agentbrain org list --output json --verbose

1. index.ts: program.parse()
   ↓
2. Commander routes to org command → list subcommand
   ↓
3. Action handler invoked:
   withErrorHandler(async (cmd) => {
     await fetchAndPrint<Organization[]>(
       cmd,
       (c) => c.get("/organizations")
     );
   })
   ↓
4. createClient(cmd) resolves config:
   - Defaults loaded
   - ~/.agentbrain/config.json read
   - AGENTBRAIN_* env vars checked
   - cmd.opts() applied
   ↓
5. ApiClient instantiated with resolved config
   ↓
6. apiClient.get("/organizations") called
   ↓
7. HTTP request to https://api.agentbrain.sh/v1/cms/organizations
   Headers: X-API-Key, X-Org-ID, Content-Type
   ↓
8. Response received, envelope unwrapped
   ↓
9. resolveOutputFormat(cmd.opts().output) → "json"
   ↓
10. formatOutput(data, "json") → JSON.stringify(data, null, 2)
    ↓
11. console.log(formatted output)
    ↓
12. process.exit(0)
```

## Error Handling Architecture

```
┌───────────────────────────────────┐
│ HTTP Request Fails                │
├───────────────────────────────────┤
│ - Network error                   │
│ - Response not ok (4xx, 5xx)      │
│ - Timeout (AbortError)            │
│ - JSON parse error                │
└──────────────┬────────────────────┘
               │
        ┌──────▼────────┐
        │ ApiError class│
        │ {             │
        │  statusCode,  │
        │  message,     │
        │  data         │
        │ }             │
        └──────┬────────┘
               │
        ┌──────▼─────────────────┐
        │ withErrorHandler       │
        │ catches and formats    │
        │ ApiError              │
        └──────┬─────────────────┘
               │
        ┌──────▼──────────────────┐
        │ Output error to stderr  │
        │ chalk.red for styling   │
        │ Verbose: raw response   │
        └──────┬──────────────────┘
               │
        ┌──────▼──────────────────┐
        │ process.exit(1)         │
        │ Signal failure to shell │
        └─────────────────────────┘
```

**Specific Error Messages:**

| Status | Message | Action |
|--------|---------|--------|
| 401 | Unauthorized. Set API key with: agentbrain config set apiKey | User provides key |
| 404 | Not found. Verify the resource ID | User checks ID |
| 408 | Request timed out. Increase timeout with: agentbrain config set timeout | User adjusts timeout |
| 500 | Server error. Try again later | Inform user to retry |

## Dependencies & External Integrations

```
agentbrain-cli
├── commander (CLI parsing & routing)
├── chalk (colored terminal output)
├── cli-table3 (ASCII table formatting)
├── yaml (YAML serialization)
├── Node.js built-in modules
│   ├── fetch (HTTP client)
│   ├── fs (file I/O for config)
│   └── os, path (OS utilities)
└── AgentBrain API (external service)
    ├── Base URL: https://api.agentbrain.sh
    ├── Protocol: HTTP/REST
    ├── Auth: X-API-Key header
    └── Version: /v1/cms/*
```

## Deployment Architecture

```
Development
│
├── npm script: pnpm build
│   ├── TypeScript compilation
│   ├── tsup bundling → dist/index.js
│   └── ESM output (39.5 KB)
│
├── Local testing
│   ├── pnpm test (vitest)
│   └── Manual CLI testing
│
Production
│
├── npm registry (npmjs.com)
│   ├── Package: agentbrain@0.1.0
│   ├── Files: dist/*, package.json, README
│   └── Bin: agentbrain → dist/index.js
│
├── User installation
│   └── npm install -g agentbrain
│
└── Execution
    └── /path/to/node_modules/.bin/agentbrain <command>
```

## Scalability & Performance

**Memory Usage:** 40-60 MB typical
- Small startup footprint
- No caching → memory freed after each command
- Streaming for large outputs (no buffering)

**Network:** Single connection per command
- HTTP/1.1 keep-alive (Node 18+)
- Timeout 30s default, configurable
- No connection pooling (single req per invocation)

**Output Performance:**
- TTY table rendering: <100ms (up to 1000 rows)
- JSON serialization: <50ms (typical response)
- YAML serialization: <100ms (typical response)

**Future Improvements:**
- Batch operations (multiple resources in one request)
- Client-side caching (for frequently-accessed data)
- Parallel command execution (independent requests)
