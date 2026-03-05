# Phase 1: Project Setup

## Context
- [AgentBrain API docs](https://docs.agentbrain.sh)
- [Commander.js](https://github.com/tj/commander.js)

## Overview
- **Priority:** P1
- **Status:** pending
- **Effort:** 3h
- **Description:** Initialize TypeScript project with build toolchain, linting, and npm package config.

## Key Insights
- Single executable bin entry via tsup bundle
- Target Node 20+ (LTS)
- pnpm workspace not needed (standalone package)

## Requirements

### Functional
- Project compiles and produces runnable `agentbrain` binary
- `agentbrain --version` and `agentbrain --help` work

### Non-Functional
- Build time < 5s
- Bundle size < 2MB (excluding node_modules)
- ESM output with CJS compat shim

## Files to Create

```
package.json
tsconfig.json
tsup.config.ts
.gitignore
.npmignore
src/index.ts           # Entry point with shebang
src/version.ts         # Version from package.json
```

## Implementation Steps

### 1. Initialize project
```bash
cd /Users/duynguyen/www/nlb/agentbrain-cli
pnpm init
```

### 2. Install dependencies
```bash
# Runtime
pnpm add commander chalk cli-table3 cosmiconfig undici yaml

# Dev
pnpm add -D typescript tsup @types/node vitest eslint
```

### 3. Configure package.json
```jsonc
{
  "name": "@agentbrain/cli",
  "version": "0.1.0",
  "bin": { "agentbrain": "./dist/index.js" },
  "type": "module",
  "files": ["dist"],
  "engines": { "node": ">=20" },
  "scripts": {
    "build": "tsup",
    "dev": "tsup --watch",
    "lint": "eslint src/",
    "test": "vitest run",
    "prepublishOnly": "pnpm build"
  }
}
```

### 4. Configure tsconfig.json
```jsonc
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "outDir": "dist",
    "rootDir": "src",
    "strict": true,
    "esModuleInterop": true,
    "declaration": true,
    "skipLibCheck": true,
    "resolveJsonModule": true
  },
  "include": ["src"]
}
```

### 5. Configure tsup
```ts
// tsup.config.ts
import { defineConfig } from 'tsup';

export default defineConfig({
  entry: ['src/index.ts'],
  format: ['esm'],
  target: 'node20',
  clean: true,
  dts: false,
  banner: { js: '#!/usr/bin/env node' },
  sourcemap: true,
});
```

### 6. Create entry point
```ts
// src/index.ts
import { Command } from 'commander';

const program = new Command();

program
  .name('agentbrain')
  .description('CLI for AgentBrain enterprise data hub')
  .version('0.1.0');

program.parse();
```

### 7. Build and verify
```bash
pnpm build
chmod +x dist/index.js
./dist/index.js --version
./dist/index.js --help
```

## Todo List
- [ ] Initialize pnpm project
- [ ] Install all dependencies
- [ ] Configure tsconfig.json
- [ ] Configure tsup.config.ts
- [ ] Create src/index.ts entry point
- [ ] Build and verify binary works
- [ ] Add .gitignore / .npmignore

## Success Criteria
- `pnpm build` succeeds with no errors
- `agentbrain --version` prints `0.1.0`
- `agentbrain --help` shows description and available commands
- TypeScript strict mode enabled, no type errors

## Risk Assessment
- **tsup shebang:** Ensure banner injection works for bin execution → test with `node dist/index.js` fallback
- **ESM compat:** Some deps may need CJS → tsup handles interop
