# Phase 3: Organization Commands

## Context
- Depends on: [Phase 2](./phase-02-core-infrastructure.md)
- API base: `GET/POST/PUT/DELETE /v1/cms/organizations`
- Org context required for most other commands

## Overview
- **Priority:** P1
- **Status:** pending
- **Effort:** 4h
- **Description:** Organization CRUD, member management, and active org switching.

## Requirements

### Functional
- List, get, create, update, delete organizations
- List/add/update/remove org members
- Switch active org (persisted to config)
- `org me` — list user's own orgs

### Non-Functional
- Table output: columns = ID, Name, Role, Created

## Files to Create/Modify

```
src/commands/org-command.ts         # All org subcommands
src/types/organization-types.ts     # Org + Member types
```

## API Mapping

| CLI Command | Method | Endpoint |
|-------------|--------|----------|
| `org list` | GET | /organizations |
| `org me` | GET | /organizations/me |
| `org get <id>` | GET | /organizations/:id |
| `org create --name <n>` | POST | /organizations |
| `org update <id> --name <n>` | PUT | /organizations/:id |
| `org delete <id>` | DELETE | /organizations/:id |
| `org members <id>` | GET | /organizations/:id/members |
| `org add-member <id> --email <e> --role <r>` | POST | /organizations/:id/members |
| `org update-member <id> <memberId> --role <r>` | PUT | /organizations/:id/members/:memberId |
| `org remove-member <id> <memberId>` | DELETE | /organizations/:id/members/:memberId |
| `org switch <id>` | - | Config write (set orgId) |

## Implementation Steps

### 1. Define types (`src/types/organization-types.ts`)
```ts
export interface Organization {
  id: string;
  name: string;
  description?: string;
  createdAt: string;
  updatedAt: string;
}

export interface OrgMember {
  id: string;
  userId: string;
  email: string;
  role: 'owner' | 'admin' | 'member' | 'viewer';
  joinedAt: string;
}
```

### 2. Implement org command (`src/commands/org-command.ts`)

Pattern for each subcommand:
```ts
import { Command } from 'commander';
import { getClient } from '../client/http-client.js';
import { formatOutput, resolveOutputFormat } from '../formatters/output-formatter.js';

export function createOrgCommand(): Command {
  const org = new Command('org').description('Manage organizations');

  org.command('list')
    .description('List all accessible organizations')
    .action(async (opts) => {
      const client = getClient(opts);
      const data = await client.get('/organizations');
      console.log(formatOutput(data, resolveOutputFormat(opts.output), {
        columns: ['id', 'name', 'createdAt'],
      }));
    });

  org.command('switch <id>')
    .description('Switch active organization')
    .action(async (id) => {
      await setConfig('orgId', id);
      console.log(`Switched to organization: ${id}`);
    });

  // ... other subcommands follow same pattern
  return org;
}
```

### 3. Register in index.ts
```ts
import { createOrgCommand } from './commands/org-command.js';
program.addCommand(createOrgCommand());
```

### 4. Table configs
- `org list`: id (8 chars), name, description (truncated), createdAt
- `org members`: id, email, role, joinedAt

## Todo List
- [ ] Define organization types
- [ ] Implement `org list` and `org me`
- [ ] Implement `org get`, `org create`, `org update`, `org delete`
- [ ] Implement `org members`, `org add-member`, `org update-member`, `org remove-member`
- [ ] Implement `org switch`
- [ ] Register command in index.ts
- [ ] Test all subcommands

## Success Criteria
- `agentbrain org list` shows orgs in table
- `agentbrain org list -o json` returns JSON array
- `agentbrain org switch <id>` persists to config
- `agentbrain org members <id>` lists members
- Error: `org get nonexistent` shows 404 message

## Risk Assessment
- **Org ID format:** Could be UUID or integer — use string type, validate non-empty
