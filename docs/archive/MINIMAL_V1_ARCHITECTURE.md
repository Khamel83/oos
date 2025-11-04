# 🏗️ Minimal v1 Architecture: SQLite SoT on OCI VM

## Architecture Overview

Single OCI VM setup that provides:
- **SQLite** as single source of truth (SoT)
- **Google Sheets** as human approval mirror
- **Datasette** for read-only data browsing
- **sqlite-web** for maintenance (SSH tunnel only)
- **systemd timers** for automation
- **OCI Block Volume** backups (zero extra services)

## Core Components

### 1. Database Foundation

**Location**: `/opt/atlas/data/atlas.db`

**SQLite Configuration**:
```sql
-- Enable WAL mode for concurrent reads
PRAGMA journal_mode=WAL;

-- Set timeouts for reliability
PRAGMA busy_timeout=30000;

-- Optimize for read-heavy workload
PRAGMA cache_size=10000;
PRAGMA synchronous=NORMAL;
```

**Schema Design**:
```sql
-- Projects table
CREATE TABLE projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tasks table
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,
    project_id TEXT REFERENCES projects(id),
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'todo',
    assignee TEXT DEFAULT 'User',
    priority INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    approved_at DATETIME,
    approved_by TEXT
);

-- Approvals table (human loop)
CREATE TABLE approvals (
    id TEXT PRIMARY KEY,
    item_type TEXT NOT NULL, -- 'task', 'project', 'config'
    item_id TEXT NOT NULL,
    action TEXT NOT NULL, -- 'create', 'update', 'delete'
    payload JSON NOT NULL,
    status TEXT DEFAULT 'pending', -- 'pending', 'approved', 'rejected'
    requested_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    reviewed_at DATETIME,
    reviewed_by TEXT,
    notes TEXT
);

-- Runs table (execution tracking)
CREATE TABLE runs (
    id TEXT PRIMARY KEY,
    task_id TEXT REFERENCES tasks(id),
    command TEXT NOT NULL,
    status TEXT DEFAULT 'running', -- 'running', 'success', 'failed'
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    output TEXT,
    error_log TEXT
);

-- Create indexes for performance
CREATE INDEX idx_tasks_project_id ON tasks(project_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_approvals_status ON approvals(status);
CREATE INDEX idx_runs_task_id ON runs(task_id);
CREATE INDEX idx_runs_status ON runs(status);
```

### 2. Human Loop: Google Sheets Integration

**Sheet Structure** (3 tabs):

**Tab 1: Pending_Approvals**
```
| ID | Type | Action | Item | Status | Requested | Notes |
|----|------|--------|------|--------|-----------|-------|
| approval-123 | task | create | "Add OAuth" | pending | 2024-01-15 | |
```

**Tab 2: Runs**
```
| ID | Task | Command | Status | Started | Completed | Output |
|----|------|---------|--------|---------|-----------|---------|
| run-456 | task-123 | npm test | success | 14:30 | 14:32 | All tests passed |
```

**Tab 3: Errors_Hotlist**
```
| ID | Task | Error | Timestamp | Severity | Resolved |
|----|------|-------|-----------|----------|----------|
| err-789 | task-123 | Connection timeout | 14:30 | high | false |
```

### 3. Read-Only Interface: Datasette

**Setup**:
```bash
# Install Datasette
pip install datasette datasette-vega

# Start in immutable mode (read-only)
datasette serve /opt/atlas/data/atlas.db \
  --immutable \
  --host 127.0.0.1 \
  --port 8001 \
  --reload
```

**Access**: SSH port forward to view data safely
```bash
ssh -L 8001:127.0.0.1:8001 user@your-oci-vm
# Then browse http://localhost:8001
```

### 4. Maintenance Interface: sqlite-web

**Setup**:
```bash
# Install sqlite-web
pip install sqlite-web

# Start for maintenance sessions only
sqlite_web /opt/atlas/data/atlas.db \
  --host 127.0.0.1 \
  --port 8002
```

**Access**: SSH tunnel for rare direct edits
```bash
ssh -L 8002:127.0.0.1:8002 user@your-oci-vm
# Then browse http://localhost:8002
```

### 5. Automation: systemd Timers

**DB → Sheets Export** (`/etc/systemd/system/atlas-export.timer`):
```ini
[Unit]
Description=Export Atlas DB to Google Sheets
Requires=atlas-export.service

[Timer]
OnCalendar=hourly
Persistent=true

[Install]
WantedBy=timers.target
```

**Sheets → DB Import** (`/etc/systemd/system/atlas-import.timer`):
```ini
[Unit]
Description=Import approved items from Google Sheets
Requires=atlas-import.service

[Timer]
OnCalendar=hourly
Persistent=true

[Install]
WantedBy=timers.target
```

### 6. Backup Strategy

**OCI Block Volume Backups**:
```bash
# Enable automated backups via OCI CLI or Console
# Daily backups, retain 30 days
# Zero additional services needed
```

**Local Backup Script** (`/opt/atlas/bin/backup.sh`):
```bash
#!/bin/bash
# Create local backup before any maintenance
BACKUP_DIR="/opt/atlas/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/atlas_$TIMESTAMP.db"

mkdir -p "$BACKUP_DIR"
sqlite3 /opt/atlas/data/atlas.db ".backup $BACKUP_FILE"
echo "Backup created: $BACKUP_FILE"

# Cleanup old backups (keep last 7)
find "$BACKUP_DIR" -name "atlas_*.db" -type f | sort | head -n -7 | xargs -r rm
```

## Directory Structure

```
/opt/atlas/
├── data/
│   ├── atlas.db           # SQLite SoT
│   ├── atlas.db-wal       # WAL file
│   └── atlas.db-shm       # Shared memory
├── backups/
│   ├── atlas_20240115_143000.db
│   └── ...
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

## Security & Access

### Local Access Only
- **Datasette**: `127.0.0.1:8001` (read-only)
- **sqlite-web**: `127.0.0.1:8002` (edit mode)
- **Access method**: SSH port forwarding only

### SSH Tunnel Examples
```bash
# Read-only data browsing
ssh -L 8001:127.0.0.1:8001 user@your-oci-vm
# Browse http://localhost:8001

# Maintenance session
ssh -L 8002:127.0.0.1:8002 user@your-oci-vm
# Browse http://localhost:8002

# Combined access
ssh -L 8001:127.0.0.1:8001 -L 8002:127.0.0.1:8002 user@your-oci-vm
```

### Optional: Tailscale Integration
```bash
# For easier access across devices
curl -fsSL https://tailscale.com/install.sh | sh
tailscale up
# Then access via Tailscale IP without port forwarding
```

## Implementation Checklist

### Phase 1: Core Setup
- [ ] Create `/opt/atlas/` directory structure
- [ ] Initialize SQLite database with schema
- [ ] Enable WAL mode and configure timeouts
- [ ] Set up local backup script
- [ ] Test basic database operations

### Phase 2: Interfaces
- [ ] Install and configure Datasette
- [ ] Install and configure sqlite-web
- [ ] Test SSH port forwarding access
- [ ] Verify read-only vs edit modes

### Phase 3: Google Sheets
- [ ] Create Google Sheets with proper structure
- [ ] Set up service account credentials
- [ ] Implement export script (DB → Sheets)
- [ ] Implement import script (Sheets → DB)
- [ ] Test manual sync operations

### Phase 4: Automation
- [ ] Create systemd service files
- [ ] Create systemd timer files
- [ ] Enable and start timers
- [ ] Test automated sync operations
- [ ] Set up log rotation

### Phase 5: Monitoring
- [ ] Create health check script
- [ ] Set up basic alerting (email/Telegram)
- [ ] Configure log monitoring
- [ ] Test backup/restore procedures

### Phase 6: OCI Integration
- [ ] Enable OCI Block Volume backup policy
- [ ] Test backup/restore procedures
- [ ] Configure automatic snapshot retention
- [ ] Document disaster recovery process

## Cost Analysis

**OCI Free Tier Resources Used**:
- 1x VM.Standard.E2.1.Micro (always free)
- Block volume up to 200GB (always free)
- Block volume backups (free tier allowance)

**Additional Costs**:
- $0/month for basic setup
- Minimal costs if exceeding free tier limits
- Google Sheets API: Free for typical usage

**Storage Growth Planning**:
- SQLite database: ~1MB per 1000 tasks
- Backups: 30 days retention = ~30MB storage
- Well within free tier limits

This architecture provides a robust, cost-effective foundation that can scale from personal use to small team collaboration while maintaining simplicity and reliability.