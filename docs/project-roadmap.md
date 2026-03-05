# AgentBrain CLI - Project Roadmap

## Current Status

**Version:** 0.1.0 (Alpha)
**Release Date:** March 2025
**Status:** Feature Complete, Testing Phase
**Bundle Size:** 39.5 KB (ESM)

### Completed Features

- [x] All 10 command groups implemented (org, connector, knowledge, workflow, etc.)
- [x] Full API endpoint coverage (/v1/cms/*)
- [x] Authentication system (X-API-Key, X-Org-ID headers)
- [x] Configuration management (file, env vars, CLI flags)
- [x] Output formatting (JSON, YAML, table with TTY detection)
- [x] Error handling with user-friendly messages
- [x] SSE streaming for workflow run logs
- [x] TypeScript strict mode compilation
- [x] ESM bundle generation (tsup)
- [x] Node 20+ support

### In Progress

- [ ] Unit tests (vitest framework set up, tests needed)
- [ ] Integration tests for command flows
- [ ] E2E tests with staging API
- [ ] Documentation (in progress)

### Known Limitations

- Pagination not exposed in CLI (all results returned)
- Batch operations require multiple API calls
- No transaction support across commands
- Interactive mode not available (shell scripting focus)
- No client-side caching
- No plugin system for custom commands

## Phase-Based Roadmap

### Phase 1: Alpha Release (Current - March 2025)

**Focus:** Core functionality, documentation, stabilization

**Goals:**
- [x] All CRUD operations for core entities
- [x] API client with auth and error handling
- [x] Configuration system with multiple sources
- [x] Output formatting for human and machine consumption
- [ ] Test coverage 50%+
- [ ] Comprehensive API documentation
- [ ] Setup guides for common workflows

**Success Metrics:**
- All 10 command groups functional
- 0 critical bugs reported
- Documentation complete and tested

**Timeline:** March - April 2025

---

### Phase 2: Beta Release (April - May 2025)

**Focus:** Testing, performance, advanced features

**Planned Features:**

#### FR-2.1: Comprehensive Test Suite
- Unit tests for all modules (target: 80% coverage)
- Integration tests for command flows
- E2E tests with staging environment
- Mock API server for offline testing

**Implementation:**
```bash
tests/
├── config/config-manager.test.ts
├── client/http-client.test.ts
├── formatters/output-formatter.test.ts
├── commands/
│   ├── org-command.test.ts
│   ├── connector-command.test.ts
│   └── ...
└── integration/
    ├── org-workflow.test.ts
    ├── connector-workflow.test.ts
    └── end-to-end.test.ts
```

**Success Criteria:**
- 80%+ code coverage
- All critical paths tested
- Tests run in CI/CD
- Mock server available for offline testing

#### FR-2.2: Shell Completions
- Bash completion script
- Zsh completion script
- Fish completion script

**Installation:**
```bash
# Bash
agentbrain --completion bash | sudo tee /etc/bash_completion.d/agentbrain

# Zsh
agentbrain --completion zsh | sudo tee /usr/share/zsh/site-functions/_agentbrain

# Fish
agentbrain --completion fish | sudo tee /usr/share/fish/vendor_completions.d/agentbrain.fish
```

#### FR-2.3: Configuration Templates
- [x] Interactive setup wizard (`config init`) — Completed in v0.1.0
- Pre-configured profiles (dev, staging, production)
- Quick-start templates for common setups
- Template inheritance and overrides

**Completed in v0.1.0:**
```bash
agentbrain config init  # Interactive setup wizard
```

**Planned for v0.2.0:**
```bash
agentbrain config init production  # Creates ~/.agentbrain/config.json with profile
agentbrain config profile dev      # Switch profiles
```

#### FR-2.4: Enhanced Output Features
- Custom column selection with `--columns`
- Output filtering with `--filter`
- Sorting options with `--sort`
- Column-width configuration

**Example:**
```bash
agentbrain org list --columns id,name,status --filter status=active --sort name
```

#### FR-2.5: Interactive Mode (Optional)
- Interactive prompts for complex operations
- Command history and replay
- Inline help and suggestions

**Example:**
```bash
agentbrain workflow run --interactive
> Select workflow: [1] Daily ETL [2] Weekly Report
> Enter config (optional):
> Confirm execution? (y/n)
```

**Goals:**
- 80%+ unit test coverage
- Shell completions for 3 shells
- Configuration templates system
- Enhanced output features
- Interactive mode (if time permits)

**Timeline:** April - May 2025

---

### Phase 3: Production Release (June 2025)

**Focus:** npm publication, stability, enterprise support

**Planned Features:**

#### FR-3.1: npm Registry Publication
- Publish to npmjs.com
- Automated release process (GitHub Actions)
- Semantic versioning (SemVer)
- CHANGELOG automation

**Release Process:**
```bash
# GitHub Actions workflow:
1. Tag commit: git tag v0.3.0
2. Run tests and build
3. npm publish
4. Create GitHub release
5. Update CHANGELOG
```

#### FR-3.2: Docker Support
- Official Docker image with AgentBrain CLI pre-installed
- Multi-stage build for minimal size
- Support for CI/CD pipeline integration

**Dockerfile:**
```dockerfile
FROM node:20-alpine
RUN npm install -g agentbrain@latest
ENTRYPOINT ["agentbrain"]
```

**Usage:**
```bash
docker run --rm -e AGENTBRAIN_API_KEY=xxx agentbrain org list
```

#### FR-3.3: GoClaw MCP Integration
- Model Context Protocol (MCP) server wrapper
- Enable Claude IDE integration
- Allow Claude to execute CLI commands

**Architecture:**
```
Claude IDE
    ↓
MCP Client
    ↓
GoClaw MCP Server (Node.js)
    ↓
AgentBrain CLI
    ↓
AgentBrain API
```

**Usage in Claude:**
```
User: "List all connectors in Acme Corp org"
Claude calls: agentbrain connector list --org org_acme
Returns: JSON response
Claude formats: User-friendly summary
```

#### FR-3.4: Kubernetes Integration
- Kubectl plugin for native k8s integration
- CRD definitions for AgentBrain resources
- Helm charts for deployment

**Usage:**
```bash
# After plugin installation:
kubectl agentbrain org list
kubectl agentbrain workflow run my-workflow
```

#### FR-3.5: Terraform Provider
- Official Terraform provider for AgentBrain
- Resource types: organization, connector, knowledge_base, workflow
- State management and drift detection

**Example:**
```hcl
provider "agentbrain" {
  api_key = var.agentbrain_api_key
  api_url = "https://api.agentbrain.sh"
}

resource "agentbrain_connector" "postgres" {
  name      = "production-postgres"
  type      = "postgres"
  subtype   = "standard"
  visibility = "private"

  config = {
    host     = "db.example.com"
    port     = 5432
    database = "analytics"
  }
}
```

**Goals:**
- npm registry publication with CI/CD
- Docker image with 50MB max size
- MCP server for Claude integration
- Kubectl plugin working
- Terraform provider 50%+ complete

**Success Metrics:**
- 10k+ npm downloads/month
- Zero critical security issues
- 99.9% API uptime
- <100ms response time (p99)

**Timeline:** June 2025

---

### Phase 4: Enterprise Features (July - September 2025)

**Focus:** Advanced features, performance, ecosystem

**Planned Features:**

#### FR-4.1: Advanced Caching
- Local SQLite cache for frequently-accessed data
- Cache invalidation strategies
- Offline mode with stale data

#### FR-4.2: Batch Operations
- Bulk import/export with CSV
- Parallel command execution
- Transaction-like behavior (partial rollback support)

#### FR-4.3: Audit & Logging
- Command history log to file
- Audit trail for sensitive operations
- Structured logging (JSON format)

#### FR-4.4: Plugin System
- Community command plugins
- Plugin package management
- Plugin marketplace (future)

#### FR-4.5: Performance Optimization
- Connection pooling
- Request batching
- Caching strategy optimization
- Memory usage reduction

**Goals:**
- Advanced caching system
- Batch operation support
- Audit logging infrastructure
- Plugin system foundation
- 50%+ performance improvement

**Timeline:** July - September 2025

---

### Phase 5: Ecosystem Expansion (Q4 2025 +)

**Long-term Vision:**

#### FR-5.1: Language SDKs
- Python SDK (popular for data engineers)
- Go SDK (for DevOps tools)
- Java SDK (enterprise)
- Rust SDK (systems programming)

#### FR-5.2: IDE Integrations
- VSCode extension
- IntelliJ IDEA plugin
- Neovim plugin

#### FR-5.3: CI/CD Integrations
- GitHub Actions workflow
- GitLab CI template
- Jenkins pipeline plugin

#### FR-5.4: Monitoring & Observability
- Command execution metrics
- Error rate tracking
- Performance monitoring
- Alert integration (Slack, PagerDuty)

#### FR-5.5: Community Programs
- Contributor guidelines
- Bug bounty program
- Sponsorship options
- Annual conference talk

---

## Dependency Updates

### Current Dependencies

| Package | Version | Status |
|---------|---------|--------|
| commander | ^14.0.3 | Stable |
| chalk | ^5.6.2 | Stable |
| cli-table3 | ^0.6.5 | Maintenance |
| yaml | ^2.8.2 | Stable |
| typescript | ^5.9.3 | Latest |
| tsup | ^8.5.1 | Latest |
| vitest | ^4.0.18 | Latest |

### Planned Additions

**Phase 2:**
- `jest` or `vitest` (already have vitest)
- `@commander-js/completion` (shell completions)

**Phase 3:**
- `@mcp/sdk` (GoClaw MCP)
- `docker-cli` (Docker integration)
- `@hashicorp/hcl2` (Terraform provider)

**Phase 4+:**
- `sqlite3` (caching)
- `winston` (logging)
- `node-cache` (in-memory caching)

---

## Metrics & Success Criteria

### Version 0.1.0 (Current)
- [x] Feature completeness: 100%
- [ ] Test coverage: Target 50%, Current ~0%
- [ ] Documentation: Complete
- [ ] API compatibility: 100%
- [ ] Bundle size: <50KB (Currently 39.5KB) ✓

### Version 0.2.0 (Beta)
- [ ] Test coverage: 80%
- [ ] Shell completions: 3 shells
- [ ] Performance: <100ms avg response time
- [ ] User feedback: 10+ beta users

### Version 0.3.0 (Production)
- [ ] npm downloads: 1k+ per week
- [ ] Production users: 10+
- [ ] Support response time: <24h
- [ ] Zero critical bugs (last 30 days)

---

## Risk Assessment & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|-----------|
| API schema changes | High | Medium | Maintain comprehensive API tests |
| Breaking Node.js changes | Medium | Low | Pin Node 20+ in documentation |
| Security vulnerability | Critical | Low | Regular dependency updates, security audit |
| User adoption delays | High | Medium | Community marketing, example workflows |
| npm registry issues | Medium | Very Low | Backup distribution (GitHub releases) |
| GoClaw integration complexity | Medium | Medium | Early prototyping, MCP spec study |

---

## Budget & Resource Allocation

### Development Time (Estimated)

| Phase | Duration | Focus | Developer-Hours |
|-------|----------|-------|-----------------|
| Phase 1 (Current) | 1 month | Features + docs | 160h |
| Phase 2 (Beta) | 1-2 months | Testing + features | 240h |
| Phase 3 (Production) | 1 month | Publishing + ecosystem | 160h |
| Phase 4 (Enterprise) | 3 months | Advanced features | 480h |
| Phase 5+ (Expansion) | Ongoing | SDKs + integrations | 40h/month |

**Total to 1.0.0:** ~880 hours (5.5 months, 1 full-time dev)

---

## External Dependencies & Integration Points

### AgentBrain API
- **Current:** /v1/cms/* endpoints (all required for 0.1.0)
- **Future:** Custom MCP endpoints for enhanced integration
- **Risk:** API breaking changes (mitigation: API versioning)

### npm Registry
- **Current:** Required for distribution (0.3.0+)
- **Alternative:** GitHub releases, direct download
- **Risk:** Registry downtime (mitigation: offline installation guide)

### Docker Hub
- **Current:** Not used
- **Future:** Official image hosting (3.0.0+)
- **Risk:** Image bloat (mitigation: multi-stage builds)

### GitHub
- **Current:** Source code repository
- **Future:** CI/CD automation, release management
- **Risk:** API rate limits (mitigation: GitHub Actions token)

---

## Communication & Launch Plan

### Launch Timeline

**Phase 1 (March 2025):**
- Internal release announcement
- Blog post: "Introducing AgentBrain CLI"
- GitHub repo announcement
- Discord/community notification

**Phase 2 (April-May 2025):**
- Beta user program signup
- Example workflows documentation
- Video tutorials
- Community feedback integration

**Phase 3 (June 2025):**
- npm registry launch announcement
- Press release (if applicable)
- Hacker News / Product Hunt submission
- Conference talk pitch

**Phase 4+ (July 2025+):**
- Monthly feature announcements
- Community highlight series
- Contributor spotlights
- Annual review & vision update

---

## Success Definition

### 0.1.0 Alpha
- Feature complete, well documented
- 0 critical bugs
- Community interest demonstrated

### 0.2.0 Beta
- 80% test coverage
- 100 beta users
- Shell completions working
- Positive feedback trend

### 0.3.0 Production
- Published on npm
- 1k+ downloads/week
- 10+ production customers
- Enterprise support available

### 1.0.0 LTS
- 5k+ downloads/week
- 50+ production customers
- Plugin ecosystem active
- SDKs available (Python, Go, Java)
- Terraform provider v1.0.0
- Industry recognition

---

## Next Steps

### Immediate (This Week)
1. [ ] Complete unit test suite (50%+ coverage)
2. [ ] Document all commands with examples
3. [ ] Create quick-start guide

### Short-term (Next 2 Weeks)
1. [ ] Integration tests for key workflows
2. [ ] Performance benchmarking
3. [ ] Beta user recruitment

### Medium-term (Next Month)
1. [ ] Shell completion implementation
2. [ ] Configuration templates
3. [ ] npm publication preparation

### Long-term (Next 3+ Months)
1. [ ] Docker image release
2. [ ] MCP integration development
3. [ ] Kubernetes plugin development
