# 🧠 Cross-Project Learning Patterns

## Overview

This document captures patterns, anti-patterns, and lessons learned across all Agent-OS + OOS projects. It serves as institutional memory to prevent repeating mistakes and promote successful approaches.

## Architecture Patterns

### ✅ Successful Patterns

**Pattern: SQLite + WAL for Single-Writer Systems**
```
Context: Task management, logging, configuration storage
Problem: Need ACID compliance with concurrent reads
Solution: SQLite with WAL mode + read-only interfaces
Outcome: Zero maintenance, excellent performance, easy backup

Triggers:
- Single logical writer (agent/service)
- Multiple concurrent readers (humans, dashboards)
- <100GB data size
- Local or small-scale deployment

Anti-pattern to avoid:
- Don't use PostgreSQL for simple single-writer scenarios
- Don't build custom file-based storage solutions
```

**Pattern: Google Sheets as Human Interface**
```
Context: Non-technical users need to review/approve automated actions
Problem: Building custom admin interfaces is time-consuming
Solution: Bidirectional sync with Google Sheets for approvals
Outcome: Instant familiarity, zero UI development, built-in collaboration

Triggers:
- Human approval workflows needed
- Non-technical stakeholders
- <10k rows of data
- Collaborative decision-making required

Anti-pattern to avoid:
- Don't make Sheets the source of truth
- Don't sync everything—only what humans need to see/edit
```

**Pattern: SSH Tunnels for Service Access**
```
Context: Need web access to services without public exposure
Problem: Public web interfaces require complex security
Solution: Local-only binding + SSH port forwarding
Outcome: Simple security model, leverages existing SSH infrastructure

Triggers:
- Development/admin interfaces
- Sensitive data access
- Team already has SSH access
- Services don't need public access

Anti-pattern to avoid:
- Don't expose admin interfaces publicly
- Don't build complex authentication when SSH suffices
```

### ❌ Anti-Patterns to Avoid

**Anti-Pattern: Over-Engineering for Scale**
```
Problem: Building distributed systems for single-user workloads
Symptoms:
- Microservices for simple CRUD operations
- Message queues for synchronous operations
- Container orchestration for single services
- Complex caching for small datasets

Better approach:
- Start with monolith + SQLite
- Scale complexity only when needed
- Measure before optimizing
- Use managed services before building
```

**Anti-Pattern: Configuration Explosion**
```
Problem: Making everything configurable "just in case"
Symptoms:
- 50+ configuration options
- Configs that are never changed
- Complex validation and documentation
- Decision paralysis for users

Better approach:
- Provide good defaults
- Make common cases zero-config
- Add configuration only when there's proven need
- Prefer convention over configuration
```

**Anti-Pattern: Premature Abstraction**
```
Problem: Building generic solutions before understanding requirements
Symptoms:
- Abstract base classes with single implementations
- Configuration files with single values
- Plugins systems with no plugins
- Generic APIs with single client

Better approach:
- Solve specific problems first
- Abstract after seeing 3+ similar use cases
- Keep abstractions minimal and focused
- Refactor when patterns emerge, not before
```

## Integration Patterns

### ✅ Successful Integration Approaches

**Pattern: MCP Server Integration**
```
Context: AI agents need structured project/task management
Problem: Agents need persistent context and coordination
Solution: Archon MCP server + standardized protocols
Outcome: Agents can manage projects across sessions

Implementation:
- Single MCP server per team/organization
- Standardized task schemas
- Knowledge base integration
- Session persistence

Triggers:
- Multi-session agent work
- Cross-project knowledge sharing
- Team coordination needs
- Persistent task management

Lessons learned:
- Start with simple schemas, evolve based on usage
- Make MCP server optional for basic functionality
- Provide CLI tools alongside MCP for debugging
```

**Pattern: Learning System Integration**
```
Context: Prevent repeating the same mistakes across projects
Problem: Agents and humans forget lessons learned
Solution: Structured learning capture + easy retrieval
Outcome: Improved decision-making over time

Implementation:
- ~/.agent-os/LEARNING_PATTERNS.md for global patterns
- Project-specific .agent-os/LESSONS.md
- Archon knowledge base for searchable examples
- Pre-development learning enforcement

Triggers:
- Repeated issues across projects
- Knowledge loss during team changes
- Need for pattern reuse
- Cross-project learnings

Lessons learned:
- Force learning review before starting new work
- Structure lessons with triggers and anti-patterns
- Make examples searchable and discoverable
- Update patterns based on new evidence
```

### ❌ Integration Anti-Patterns

**Anti-Pattern: Tool Proliferation**
```
Problem: Adding new tools for every minor need
Symptoms:
- 10+ services for simple workflows
- Tools that solve similar problems
- Integration complexity exceeding value
- "Tool fatigue" in the team

Better approach:
- Maximize utility of existing tools
- Add tools only when clear value exceeds complexity
- Consolidate similar functions
- Choose tools that integrate well together
```

**Anti-Pattern: Data Duplication Without Sync**
```
Problem: Same data stored in multiple places without consistency
Symptoms:
- Manual copy-paste between systems
- Conflicting information
- No clear source of truth
- Data drift over time

Better approach:
- Designate single source of truth
- Build automated sync for necessary duplicates
- Minimize data duplication
- Make inconsistency impossible, not just unlikely
```

## Operational Patterns

### ✅ Successful Operations

**Pattern: Backup Before Every Schema Change**
```
Context: Database schema evolution in production
Problem: Schema changes can break existing data
Solution: Automated backup + validation before changes
Outcome: Confident iteration with easy rollback

Process:
1. Stop automated processes
2. Create backup (local + cloud)
3. Test change on backup copy
4. Apply change to production
5. Validate data integrity
6. Resume automated processes

Triggers:
- Any ALTER TABLE operation
- Index creation/deletion
- Trigger modifications
- Data type changes

Lessons learned:
- Always test migrations on real data copies
- Document rollback procedures before applying changes
- Monitor for unexpected side effects after changes
```

**Pattern: Health Checks Before Automation**
```
Context: Automated processes can fail in various ways
Problem: Cascading failures from unhealthy systems
Solution: Comprehensive health checks before every automated operation
Outcome: Early failure detection and graceful degradation

Implementation:
- Database connectivity and integrity
- API availability and authentication
- Disk space and system resources
- Dependencies and external services

Triggers:
- Before any automated sync
- After system restarts
- During maintenance windows
- When errors are reported

Lessons learned:
- Check dependencies, not just direct services
- Include business logic validation, not just technical
- Fail fast and clearly when health checks fail
```

### ❌ Operational Anti-Patterns

**Anti-Pattern: Silent Failures**
```
Problem: Systems failing without notification
Symptoms:
- Processes stop without alerts
- Data gets out of sync silently
- Errors logged but not acted upon
- Problems discovered days later

Better approach:
- Alert on all failures, not just critical ones
- Use dead man's switches for regular processes
- Monitor business metrics, not just technical ones
- Test alerting regularly
```

**Anti-Pattern: Manual Recovery Procedures**
```
Problem: Recovery requires manual intervention
Symptoms:
- Scripts that need human decision-making
- Recovery procedures that aren't tested
- Multiple manual steps in sequence
- Knowledge trapped in one person's head

Better approach:
- Automate recovery where possible
- Test recovery procedures regularly
- Document every step clearly
- Make recovery procedures runnable by anyone on team
```

## Technology Decisions

### ✅ Technology Choices That Worked

**Choice: Python for Automation Scripts**
```
Context: Building data processing and integration scripts
Alternatives considered: Shell, Node.js, Go
Decision: Python 3.8+ with standard libraries

Why it worked:
- Excellent library ecosystem (requests, pandas, etc.)
- Good balance of readability and capability
- Strong SQLite integration
- Easy Google Sheets API integration
- Familiar to most developers

When to reconsider:
- Performance becomes critical (consider Go/Rust)
- Heavy frontend integration needed (consider Node.js)
- System administration focus (consider shell)
```

**Choice: systemd Timers over Cron**
```
Context: Scheduling automated tasks
Alternatives considered: cron, external schedulers
Decision: systemd timers with service units

Why it worked:
- Better logging and monitoring
- Dependency management
- Integrated with system startup/shutdown
- More flexible scheduling options
- Better error handling

When to reconsider:
- Simple schedules on older systems (use cron)
- Complex orchestration needs (consider workflow systems)
- Cloud-native deployment (consider cloud schedulers)
```

### ❌ Technology Choices That Didn't Work

**Choice: Custom Web UI for Simple Admin Tasks**
```
Context: Needed interface for reviewing automated decisions
Problem: Built custom React app for simple CRUD operations
Why it failed:
- Months of development for basic functionality
- Constant maintenance for browser compatibility
- Required specialized frontend knowledge
- Poor mobile experience

Better approach that worked:
- Google Sheets for human interface
- Datasette for read-only data exploration
- sqlite-web for occasional direct editing
- SSH tunnels for secure access

Lesson: Use existing tools for standard operations
```

**Choice: PostgreSQL for Single-Writer Applications**
```
Context: Task management system with one writer process
Problem: Set up PostgreSQL for what SQLite could handle
Why it failed:
- Unnecessary operational complexity
- Required database administration knowledge
- Backup and recovery more complex
- No performance benefit for the use case

Better approach that worked:
- SQLite with WAL mode
- Block volume snapshots for backup
- Datasette for read-only access
- Simple file-based recovery

Lesson: Match technology complexity to problem complexity
```

## Decision Framework

### When to Add New Technology

**Questions to Ask**:
1. What specific problem does this solve that existing tools don't?
2. How much operational complexity does this add?
3. Who on the team can maintain this?
4. What's the migration path if we need to change later?
5. How does this fit with our existing patterns?

**Red Flags** (usually indicate wrong choice):
- "It might be useful someday"
- "Everyone else is using it"
- "It's the latest/greatest technology"
- "We can learn it as we go"
- "It's probably more scalable"

**Green Flags** (usually indicate good choice):
- "This solves a specific problem we have today"
- "This reduces complexity while maintaining functionality"
- "We understand how to operate and troubleshoot this"
- "This integrates well with our existing stack"
- "We can easily revert if it doesn't work"

### Pattern Evolution Process

1. **Capture**: Document new patterns as they emerge
2. **Validate**: Test patterns across multiple projects
3. **Refine**: Update based on real-world experience
4. **Share**: Add to global learning patterns
5. **Enforce**: Include in pre-development learning

---

*This document should be updated regularly as new patterns emerge and old ones are validated or disproven. The goal is to capture institutional knowledge and prevent repeated mistakes while remaining open to better approaches.*