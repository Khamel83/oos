# 🤖 Agent-OS Integration with OOS

## Overview

This document outlines how OOS incorporates Agent-OS concepts to create a spec-first, markdown-driven workflow system that agents can read and operate on.

## Agent-OS Concepts Adopted

### 1. Spec-First Markdown Workflows

**Project-Level Specs** (`.agent-os/` directory):
```
project-root/
├── .agent-os/
│   ├── AGENT.md           # How agents should work here
│   ├── PREFERRED_STACK.md # SQLite SoT, Sheets mirror, etc.
│   ├── MIRROR_CONTRACT.md # Sheets↔DB sync rules
│   └── RUNBOOK.md         # Operational procedures
├── .oos/                  # OOS runtime data
└── your-project-files/
```

**User-Level Specs** (`~/.agent-os/`):
```
~/.agent-os/
├── GLOBAL_RULES.md       # Universal agent guidelines
├── STACK_PREFERENCES.md  # Default tech choices
└── LEARNING_PATTERNS.md  # Cross-project lessons
```

### 2. Minimal v1 Architecture

**Single OCI VM Setup:**
- **SoT**: SQLite with WAL mode on block volume
- **Human Loop**: Google Sheets as approval/checklist mirror
- **Browse Data**: Datasette (immutable mode) for read-only UI
- **Direct Edits**: sqlite-web behind SSH tunnel for maintenance
- **Scheduler**: systemd timers for automation
- **Backups**: OCI Block Volume snapshots (zero extra services)

### 3. Storage Strategy

**Phase 1 (Start Now)**:
- Keep DB + blobs on VM's block volume
- Enable scheduled block-volume backups
- No Object Storage needed initially

**Phase 2 (Add Later)**:
- Weekly cold exports (Parquet/ZIP) to OCI Object Storage
- Cost optimization for long-term storage

## Implementation Plan

### Immediate (First Part)

1. **Core Database Setup**:
   ```bash
   # Create /opt/atlas/data/atlas.db with WAL + timeouts
   sudo mkdir -p /opt/atlas/data
   sqlite3 /opt/atlas/data/atlas.db "PRAGMA journal_mode=WAL;"
   ```

2. **Read-Only Interface**:
   ```bash
   # Datasette for safe data browsing
   pip install datasette
   datasette --immutable /opt/atlas/data/atlas.db --host 127.0.0.1
   ```

3. **Maintenance Interface**:
   ```bash
   # sqlite-web for rare direct edits (localhost + SSH tunnel)
   pip install sqlite-web
   sqlite_web /opt/atlas/data/atlas.db --host 127.0.0.1
   ```

4. **Google Sheets Integration**:
   - 3 tabs: `Pending_Approvals`, `Runs`, `Errors_Hotlist`
   - Fixed headers for structured data exchange
   - Treat as mirror, not source of truth

5. **Automation**:
   ```bash
   # systemd timers for sync
   # Hourly: DB → Sheets export
   # Hourly: Sheets → DB approved items import
   ```

6. **Backup Policy**:
   ```bash
   # OCI Block Volume backup policy
   # Daily snapshots, retain 7-30 days
   ```

### Documentation Structure

1. **Project-Level Agent Specs**:
   ```markdown
   # .agent-os/AGENT.md
   - Input/output formats agents should use
   - Guardrails and safety rules
   - Integration points with OOS systems

   # .agent-os/PREFERRED_STACK.md
   - SQLite as single source of truth
   - Google Sheets as human approval layer
   - Datasette for read-only access
   - systemd for scheduling

   # .agent-os/MIRROR_CONTRACT.md
   - Exact columns that flow Sheets → DB
   - Approval workflow specifications
   - Data validation rules

   # .agent-os/RUNBOOK.md
   - pause workers → snapshot → edit → resume
   - Emergency procedures
   - Monitoring and alerts
   ```

2. **User-Level Global Specs**:
   ```markdown
   # ~/.agent-os/GLOBAL_RULES.md
   - Never modify primary DB without backup
   - Always use approval workflow for critical changes
   - Maintain audit trail for all operations
   ```

## Integration with Existing OOS

### Enhanced Archon Integration

```bash
# OOS already has Archon MCP - enhance with Agent-OS patterns
./bin/create_archon_project.sh "Project Name" "Description"

# New: Auto-create .agent-os/ specs during project setup
# New: Link Archon tasks to Agent-OS workflow specs
```

### Learning System Enhancement

```bash
# Current: ./bin/development_guide.sh
# Enhanced: Add Agent-OS spec review to learning workflow
# New: Store lessons in both Archon and ~/.agent-os/LEARNING_PATTERNS.md
```

### Bootstrap Integration

```bash
# Enhanced bootstrap process:
./scripts/bootstrap_enhanced.sh --agent-os my-project

# Creates:
# - Standard OOS setup
# - .agent-os/ directory with specs
# - SQLite SoT setup
# - Datasette/sqlite-web configuration
# - systemd timer templates
```

## Benefits

1. **Spec-Driven Development**: Agents read markdown specs to understand how to work
2. **Human-in-Loop**: Google Sheets provides approval workflow without complex UI
3. **Cost Effective**: Single VM, SQLite, free tier services
4. **OOS Compatible**: Builds on existing Archon integration and learning systems
5. **Gradual Migration**: Can implement piece by piece

## Migration Path

### Phase 1: Foundation
- Set up SQLite SoT
- Create .agent-os/ spec structure
- Basic Datasette read-only interface

### Phase 2: Human Loop
- Google Sheets integration
- Approval workflow automation
- systemd timer setup

### Phase 3: Enhancement
- Full backup automation
- Monitoring and alerting
- Performance optimization

### Phase 4: Scale
- Optional Postgres migration
- Advanced search capabilities
- Multi-project coordination

## File Structure After Integration

```
project-root/
├── .agent-os/              # Agent-OS specs (NEW)
│   ├── AGENT.md
│   ├── PREFERRED_STACK.md
│   ├── MIRROR_CONTRACT.md
│   └── RUNBOOK.md
├── .oos/                   # OOS runtime (EXISTING)
│   ├── config/
│   └── cache/
├── data/                   # Data directory (NEW)
│   ├── atlas.db           # SQLite SoT
│   └── backups/
├── bin/                    # Enhanced scripts (EXISTING)
│   ├── setup-agent-os.sh  # NEW
│   └── existing-oos-scripts...
└── docs/                   # Enhanced docs (EXISTING)
    ├── AGENT_OS_INTEGRATION.md  # This file
    └── existing-docs...
```

This integration makes OOS agents truly spec-driven while maintaining its simplicity and cost-effectiveness.