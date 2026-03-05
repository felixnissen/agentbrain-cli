# AgentBrain CLI

TypeScript command-line tool for interacting with AgentBrain enterprise data hub API.

Manage organizations, connectors, knowledge bases, workflows, permissions, and more from the terminal.

## Installation

Install via npm:

```bash
npm install -g agentbrain
```

Or with pnpm:

```bash
pnpm add -g agentbrain
```

Requires Node 20+.

## Quick Start

### Option 1: Interactive Setup (Recommended)

Run the interactive setup wizard:

```bash
agentbrain config init
```

This prompts you for:
- API URL (default: https://api.agentbrain.sh for cloud, custom for on-premise)
- API Key
- Default Organization ID (optional)

### Option 2: Manual Configuration

Set your API credentials via commands:

```bash
agentbrain config set apiKey sk_live_xxxxx
agentbrain config set apiUrl https://api.agentbrain.sh
agentbrain config set orgId org_xxxxx
```

### Verify Setup

```bash
agentbrain org me
```

## Usage

### Organizations

```bash
# List all organizations
agentbrain org list

# Get organization details
agentbrain org get <id>

# Create organization
agentbrain org create --name "Acme Corp" --type "enterprise"

# Switch active organization
agentbrain org switch org_xxxxx

# Manage members
agentbrain org members <id>
agentbrain org add-member <orgId> --user-id user_xxxxx --role admin
```

### Connectors

```bash
# List connectors
agentbrain connector list

# Get connector details
agentbrain connector get <id>

# Create connector
agentbrain connector create --name "PostgreSQL" --type postgres --subtype standard

# Test connector
agentbrain connector test <id> --config '{...}'

# Inspect databases, schemas, tables
agentbrain connector databases <id>
agentbrain connector schemas <id> --database mydb
agentbrain connector tables <id> --database mydb --schema public

# Share connector
agentbrain connector share create <id> --user-id user_xxxxx
```

### Knowledge Bases

```bash
# List knowledge bases
agentbrain knowledge list

# Get knowledge base
agentbrain knowledge get <id>

# Create knowledge base
agentbrain knowledge create --title "Product Docs"

# Manage versions
agentbrain knowledge versions <id>
agentbrain knowledge version <id> <versionId>
agentbrain knowledge rollback <id> <versionId>
```

### Workflows

```bash
# List workflows
agentbrain workflow list

# Create workflow
agentbrain workflow create --name "ETL Job" --cron "0 0 * * *"

# Manage steps
agentbrain workflow steps list <id>
agentbrain workflow steps create <id> --operator transform --config '{...}'

# Execute and monitor
agentbrain workflow run <id>
agentbrain workflow runs <id>
agentbrain workflow logs <id> <runId>

# Cancel running workflow
agentbrain workflow cancel <id> <runId>
```

### Permissions

```bash
# List permission groups
agentbrain permission-group list

# Create permission group
agentbrain permission-group create --name "Analysts"

# Add rules
agentbrain permission-group rules create <groupId> --action read --resource connector

# Verify permissions
agentbrain permission-group verify-permission <groupId> --action write --resource knowledge
```

### Other Commands

```bash
# Categories
agentbrain category list
agentbrain category tree

# Tags
agentbrain tag list
agentbrain tag create --name "production"

# Search across entities
agentbrain search --query "my-connector"

# Query logs
agentbrain query-log list
agentbrain query-log get <id>
```

## Configuration

Config stored at `~/.agentbrain/config.json` (mode 0600 for security).

Resolution order (highest to lowest priority):

1. CLI flags (`--api-key`, `--api-url`, `--org`, `--output`)
2. Environment variables (`AGENTBRAIN_API_KEY`, `AGENTBRAIN_API_URL`, etc.)
3. Config file (`~/.agentbrain/config.json`)
4. Defaults

View current config:

```bash
agentbrain config list
agentbrain config get apiKey
agentbrain config set timeout 60000
```

Supported config keys:

- `apiUrl` - API endpoint (default: https://api.agentbrain.sh)
- `apiKey` - API authentication key
- `orgId` - Default organization ID
- `output` - Output format: json, table, yaml (default: table for TTY, json for pipes)
- `timeout` - Request timeout in ms (default: 30000)

## Output Formats

Default behavior:

- **TTY (interactive terminal)** → table format (colored, human-readable)
- **Pipe/redirect** → json format (machine-readable)

Override with `--output`:

```bash
agentbrain org list --output json
agentbrain org list --output yaml
agentbrain org list --output table
```

## Global Options

All commands support:

```bash
--api-url <url>      Override API endpoint
--api-key <key>      Override API key
--org <id>           Override organization ID
--output <fmt>       Output format: json, table, yaml
--verbose            Enable request logging
```

## Error Handling

Errors include:

- HTTP status code (4xx, 5xx)
- Error message from API
- Full response data in verbose mode (`--verbose`)

Example:

```bash
agentbrain org get invalid-id 2>&1
# Error 404: Organization not found
```

## Development

Clone and build:

```bash
git clone https://github.com/nextlevelbuilder/agentbrain-cli
cd agentbrain-cli
pnpm install
pnpm build
pnpm test
```

Dev mode with watch:

```bash
pnpm dev
```

## License

MIT
