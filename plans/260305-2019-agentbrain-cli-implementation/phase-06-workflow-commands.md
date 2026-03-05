# Phase 6: Workflow Commands

## Context
- Depends on: [Phase 2](./phase-02-core-infrastructure.md)
- Workflows = visual ETL pipelines with steps
- Run execution with SSE real-time log streaming
- Most complex runtime behavior (streaming, cancellation)

## Overview
- **Priority:** P1
- **Status:** pending
- **Effort:** 5h
- **Description:** Workflow CRUD, step management, execution, run history, and SSE log streaming.

## Files to Create/Modify

```
src/commands/workflow-command.ts     # Workflow commands
src/types/workflow-types.ts          # Workflow + run types
src/client/sse-parser.ts             # SSE stream parser (extracted from http-client)
```

## API Mapping

| CLI Command | Method | Endpoint |
|-------------|--------|----------|
| `workflow list` | GET | /workflows |
| `workflow get <id>` | GET | /workflows/:id |
| `workflow create --name <n> [flags]` | POST | /workflows |
| `workflow update <id> [flags]` | PUT | /workflows/:id |
| `workflow delete <id>` | DELETE | /workflows/:id |
| `workflow steps <id>` | GET | /workflows/:id/steps |
| `workflow add-step <id> [flags]` | POST | /workflows/:id/steps |
| `workflow update-step <id> <stepId> [flags]` | PUT | /workflows/:id/steps/:stepId |
| `workflow delete-step <id> <stepId>` | DELETE | /workflows/:id/steps/:stepId |
| `workflow replace-steps <id> --file <f>` | PUT | /workflows/:id/steps/replace |
| `workflow run <id>` | POST | /workflows/:id/run |
| `workflow runs <id>` | GET | /workflows/:id/runs |
| `workflow run-detail <runId>` | GET | /workflow-runs/:runId |
| `workflow cancel <runId>` | POST | /workflow-runs/:runId/cancel |
| `workflow run-steps <runId>` | GET | /workflow-runs/:runId/steps |
| `workflow logs <runId>` | GET (SSE) | /workflow-runs/:runId/stream |

## Implementation Steps

### 1. Define types (`src/types/workflow-types.ts`)
```ts
export interface Workflow {
  id: string;
  name: string;
  description?: string;
  stepCount: number;
  status: 'draft' | 'active' | 'archived';
  createdAt: string;
}

export interface WorkflowStep {
  id: string;
  workflowId: string;
  type: string;
  config: Record<string, unknown>;
  order: number;
}

export interface WorkflowRun {
  id: string;
  workflowId: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  startedAt: string;
  completedAt?: string;
  duration?: number;
}
```

### 2. SSE Parser (`src/client/sse-parser.ts`)
```ts
/**
 * Parse SSE stream from undici response body.
 * SSE format: "data: {...}\n\n"
 */
export async function parseSSEStream(
  body: AsyncIterable<Uint8Array>,
  onEvent: (event: SSEEvent) => void,
  onDone?: () => void,
): Promise<void> {
  const decoder = new TextDecoder();
  let buffer = '';

  for await (const chunk of body) {
    buffer += decoder.decode(chunk, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() ?? '';

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = line.slice(6);
        if (data === '[DONE]') { onDone?.(); return; }
        try {
          onEvent(JSON.parse(data));
        } catch {
          onEvent({ raw: data });
        }
      }
    }
  }
  onDone?.();
}
```

### 3. Implement workflow command

Key specifics:
- `workflow run <id>`: Execute and optionally stream logs.
  - `--wait`: Block until run completes, print final status
  - `--follow` / `-f`: Stream SSE logs in real-time (default if TTY)
  - Without flags in non-TTY: Print run ID as JSON and exit immediately
- `workflow logs <runId>`: Stream logs for existing run (SSE)
- `workflow replace-steps <id> --file steps.json`: Read JSON file, PUT to replace all steps
- `workflow cancel <runId>`: Cancel running workflow

```ts
workflow.command('run <id>')
  .description('Execute a workflow')
  .option('--wait', 'Wait for completion')
  .option('-f, --follow', 'Follow logs in real-time')
  .action(async (id, opts) => {
    const client = getClient(opts);
    const run = await client.post(`/workflows/${id}/run`);

    if (opts.follow || (process.stdout.isTTY && !opts.wait)) {
      // Stream SSE logs
      await client.stream(`/workflow-runs/${run.id}/stream`, (event) => {
        console.log(formatLogEvent(event));
      });
    } else if (opts.wait) {
      // Poll until complete
      await pollRunStatus(client, run.id);
    }

    console.log(formatOutput(run, resolveOutputFormat(opts.output)));
  });
```

### 4. Log formatting
- Timestamp + level + message
- Color-coded: info=blue, warn=yellow, error=red, success=green
- Step transitions highlighted

## Todo List
- [ ] Define workflow/run/step types
- [ ] Implement SSE parser
- [ ] Implement workflow CRUD commands
- [ ] Implement step management commands
- [ ] Implement run/cancel/run-detail commands
- [ ] Implement SSE log streaming (`workflow logs`)
- [ ] Implement `--wait` and `--follow` modes
- [ ] Register in index.ts
- [ ] Test SSE streaming with mock server

## Success Criteria
- `agentbrain workflow list` shows workflows
- `agentbrain workflow run <id> --follow` streams logs in real-time
- `agentbrain workflow run <id> -o json` prints run ID JSON and exits
- `agentbrain workflow cancel <runId>` cancels running workflow
- `agentbrain workflow logs <runId>` streams historical/live logs
- SSE parser handles partial chunks correctly

## Risk Assessment
- **SSE connection drops:** Implement reconnect with `Last-Event-ID` header if API supports it
- **Long-running workflows:** `--wait` needs timeout flag (default 5min)
- **Large step configs:** `replace-steps` reads from file — validate JSON before sending

## Security Considerations
- Workflow steps may contain credentials in config — mask sensitive fields in output
