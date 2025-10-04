# 🛠️ Preferred Stack Configuration

## Architecture Overview

This project uses the Agent-OS minimal v1 architecture with OOS enhancements:

- **Source of Truth**: SQLite with WAL mode
- **Human Loop**: Google Sheets for approvals and checklists
- **Read-Only Access**: Datasette (immutable mode)
- **Maintenance**: sqlite-web behind SSH tunnel
- **Automation**: systemd timers
- **Backups**: OCI Block Volume snapshots

## Core Components

### Database Layer

**Primary Database**: SQLite
```bash
Location: /opt/atlas/data/atlas.db
Mode: WAL (Write-Ahead Logging)
Access: Concurrent reads, single writer
Backup: Automated OCI Block Volume snapshots
```

**Configuration**:
```sql
PRAGMA journal_mode=WAL;
PRAGMA busy_timeout=30000;
PRAGMA cache_size=10000;
PRAGMA synchronous=NORMAL;
```

### Human Interface Layer

**Google Sheets Integration**:
- **Sheet Name**: `[Project Name] - Atlas`
- **Tabs**: `Pending_Approvals`, `Runs`, `Errors_Hotlist`
- **Sync**: Bidirectional hourly via systemd timers
- **Role**: Approval workflow, not source of truth

### Data Access Layer

**Read-Only Browsing**: Datasette
```bash
Service: datasette
Port: 127.0.0.1:8001
Mode: --immutable (read-only)
Access: SSH port forwarding only
```

**Direct Editing**: sqlite-web
```bash
Service: sqlite-web
Port: 127.0.0.1:8002
Mode: Full edit capabilities
Access: SSH tunnel for maintenance only
```

### Automation Layer

**Scheduler**: systemd timers
```bash
atlas-export.timer  # DB → Sheets (hourly)
atlas-import.timer  # Sheets → DB approved items (hourly)
atlas-backup.timer  # Local backups (daily)
atlas-health.timer  # Health checks (every 15min)
```

## Development Stack

### Required Tools

**Core Dependencies**:
```bash
sqlite3           # Database CLI
python3           # Automation scripts
pip               # Python package manager
systemd           # Timer management
```

**Optional Tools**:
```bash
datasette         # Read-only web interface
sqlite-web        # Maintenance web interface
```

### OOS Integration

**Archon MCP Server**:
```bash
Service: Archon MCP
URL: http://localhost:8051/mcp
Integration: Task management and knowledge base
```

**Learning System**:
```bash
Scripts: ./bin/development_guide.sh, ./bin/archon_learning.sh
Storage: ~/.agent-os/LEARNING_PATTERNS.md + Archon knowledge base
```

## Deployment Architecture

### Single VM Setup (OCI Free Tier)

**Compute**: VM.Standard.E2.1.Micro
**Storage**: Block volume (up to 200GB free)
**Network**: Private subnet with SSH access
**Backup**: Automated block volume snapshots

### Directory Structure

```
/opt/atlas/
├── data/
│   ├── atlas.db              # SQLite SoT
│   ├── atlas.db-wal          # WAL file
│   └── atlas.db-shm          # Shared memory
├── backups/
│   └── atlas_YYYYMMDD_HHMMSS.db
├── bin/
│   ├── backup.sh
│   ├── export-to-sheets.py
│   ├── import-from-sheets.py
│   └── health-check.sh
├── config/
│   ├── sheets-credentials.json
│   └── atlas.conf
└── logs/
    ├── export.log
    ├── import.log
    └── health.log
```

## Security Configuration

### Access Control

**Database Access**:
- Direct: sqlite3 CLI (local users only)
- Web Read: Datasette via SSH tunnel
- Web Edit: sqlite-web via SSH tunnel
- API: None (internal only)

**Network Security**:
- Services bind to 127.0.0.1 only
- SSH key-based authentication
- No public web interfaces
- Optional: Tailscale for device access

### Data Protection

**Backup Strategy**:
- Local: Daily SQLite backups (retain 7 days)
- Remote: OCI Block Volume snapshots (retain 30 days)
- Offsite: Weekly exports to OCI Object Storage (optional)

**Audit Trail**:
- All operations logged to /opt/atlas/logs/
- Google Sheets maintains approval history
- systemd journal for service operations

## Integration Patterns

### Task Management

**Create Task**:
1. Agent submits to Archon MCP
2. Archon creates task in SQLite
3. Task appears in Google Sheets for visibility
4. Human can approve/modify via Sheets
5. Approved changes sync back to SQLite

**Execute Task**:
1. Agent queries current tasks from SQLite
2. Updates status to 'doing'
3. Performs work with progress logging
4. Updates status to 'review' when complete
5. Human reviews and marks 'done' if approved

### Knowledge Management

**Capture Learning**:
1. Document patterns in ~/.agent-os/LEARNING_PATTERNS.md
2. Store examples in Archon knowledge base
3. Reference in future task descriptions
4. Update project specs when patterns emerge

### Error Handling

**Automatic Recovery**:
1. Health check detects issues
2. Attempt automatic remediation
3. Fall back to read-only mode if needed
4. Alert humans via configured channels
5. Document incident for learning

## Performance Expectations

### Response Times
- SQLite queries: <10ms
- Datasette page load: <1s
- Sheets sync: <30s
- Backup operations: <5min

### Scalability Limits
- Max tasks: ~100,000 (SQLite limit much higher)
- Max concurrent reads: 50+ (WAL mode)
- Storage growth: ~1MB per 1000 tasks
- Sheets API: 100 requests/100s (sufficient for hourly sync)

### Upgrade Paths
- **More users**: Add Postgres option
- **Heavy search**: Add FTS or external search service
- **Real-time**: Add WebSocket layer
- **Mobile**: Add REST API with authentication

---

*This stack prioritizes simplicity, cost-effectiveness, and reliability over features. Scale complexity only when needed.*