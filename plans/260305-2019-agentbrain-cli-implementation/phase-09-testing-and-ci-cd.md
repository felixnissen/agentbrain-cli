# Phase 9: Testing & CI/CD

## Context
- Depends on: Phases 3-7 (all commands implemented)
- Test framework: Vitest (fast, ESM-native, TypeScript)
- CI: GitHub Actions
- Publish: npm registry as `@agentbrain/cli`

## Overview
- **Priority:** P2
- **Status:** pending
- **Effort:** 4h
- **Description:** Unit tests, integration tests, CI pipeline, and npm publish workflow.

## Files to Create/Modify

```
tests/
  unit/
    config-manager.test.ts
    http-client.test.ts
    output-formatter.test.ts
    sse-parser.test.ts
    crud-command-factory.test.ts
  integration/
    org-commands.test.ts
    connector-commands.test.ts
    knowledge-commands.test.ts
    workflow-commands.test.ts
    search-commands.test.ts
  helpers/
    mock-server.ts              # Mock API server for integration tests
    test-utils.ts               # Shared test utilities
vitest.config.ts
.github/
  workflows/
    ci.yml                      # Test + lint on PR
    publish.yml                 # npm publish on tag
```

## Implementation Steps

### 1. Vitest config (`vitest.config.ts`)
```ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    include: ['tests/**/*.test.ts'],
    coverage: {
      provider: 'v8',
      include: ['src/**/*.ts'],
      exclude: ['src/index.ts', 'src/types/**'],
      thresholds: { lines: 70 },
    },
  },
});
```

### 2. Unit tests

**config-manager.test.ts:**
- Config file read/write round-trip
- Env var override precedence
- Default values
- Invalid key handling

**http-client.test.ts:**
- Request construction (URL, headers, auth)
- Error response parsing (401, 403, 404, 5xx)
- Timeout handling
- Retry on 5xx

**output-formatter.test.ts:**
- JSON output correctness
- Table column rendering
- YAML output
- Auto-detect TTY → format

**sse-parser.test.ts:**
- Complete events
- Partial chunks
- [DONE] termination
- Invalid JSON handling

### 3. Integration tests

Use a lightweight mock HTTP server (undici MockAgent or custom):

```ts
// tests/helpers/mock-server.ts
import { MockAgent, setGlobalDispatcher } from 'undici';

export function createMockApi() {
  const agent = new MockAgent();
  setGlobalDispatcher(agent);
  const pool = agent.get('https://api.agentbrain.sh');

  return {
    mockGet(path: string, response: object, status = 200) {
      pool.intercept({ path: `/v1/cms${path}`, method: 'GET' })
        .reply(status, response);
    },
    mockPost(path: string, response: object, status = 200) {
      pool.intercept({ path: `/v1/cms${path}`, method: 'POST' })
        .reply(status, response);
    },
    close: () => agent.close(),
  };
}
```

**Test pattern:**
```ts
describe('org commands', () => {
  it('org list returns organizations', async () => {
    const mock = createMockApi();
    mock.mockGet('/organizations', { data: [{ id: '1', name: 'Test Org' }] });

    const result = await runCLI(['org', 'list', '--output', 'json']);
    expect(JSON.parse(result.stdout)).toEqual([{ id: '1', name: 'Test Org' }]);

    mock.close();
  });
});
```

### 4. CLI runner helper
```ts
// tests/helpers/test-utils.ts
import { execFile } from 'child_process';

export function runCLI(args: string[]): Promise<{ stdout: string; stderr: string; code: number }> {
  return new Promise((resolve) => {
    execFile('node', ['dist/index.js', ...args], (err, stdout, stderr) => {
      resolve({ stdout, stderr, code: err?.code ?? 0 });
    });
  });
}
```

### 5. GitHub Actions CI (`.github/workflows/ci.yml`)
```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [20, 22]
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: pnpm
      - run: pnpm install --frozen-lockfile
      - run: pnpm lint
      - run: pnpm build
      - run: pnpm test -- --coverage
```

### 6. npm publish workflow (`.github/workflows/publish.yml`)
```yaml
name: Publish
on:
  push:
    tags: ['v*']
jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          registry-url: https://registry.npmjs.org
      - run: pnpm install --frozen-lockfile
      - run: pnpm build
      - run: pnpm test
      - run: pnpm publish --access public --no-git-checks
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
```

## Todo List
- [ ] Configure Vitest
- [ ] Write unit tests for config manager
- [ ] Write unit tests for HTTP client
- [ ] Write unit tests for output formatter
- [ ] Write unit tests for SSE parser
- [ ] Create mock API helper
- [ ] Write integration tests for each command group
- [ ] Create GitHub Actions CI workflow
- [ ] Create npm publish workflow
- [ ] Achieve 70%+ code coverage

## Success Criteria
- `pnpm test` passes all tests
- Code coverage > 70%
- CI runs on Node 20 and 22
- `git tag v0.1.0 && git push --tags` triggers npm publish
- Mock API tests cover happy path + error cases

## Risk Assessment
- **undici MockAgent API changes:** Pin undici version, check docs for MockAgent stability
- **npm org scope:** `@agentbrain` scope must be claimed on npm — do this early
- **Flaky SSE tests:** Use deterministic mock streams, avoid timing-dependent assertions
