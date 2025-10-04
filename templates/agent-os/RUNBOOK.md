# 📖 Operational Runbook

## Overview

This runbook provides step-by-step procedures for operating and maintaining the Agent-OS + OOS integrated system. Follow these procedures for safe operations.

## Core Operations

### 🔄 Standard Workflow: Pause → Snapshot → Edit → Resume

**When to Use**:
- Database schema changes
- System maintenance
- Critical bug fixes
- Major configuration updates

**Procedure**:

#### 1. Pause Workers
```bash
# Stop all automated processes
sudo systemctl stop atlas-export.timer
sudo systemctl stop atlas-import.timer
sudo systemctl stop atlas-backup.timer

# Verify timers are stopped
sudo systemctl status atlas-*.timer

# Check for running processes
ps aux | grep atlas
```

#### 2. Create Snapshot
```bash
# Create local backup
/opt/atlas/bin/backup.sh

# Create OCI block volume snapshot (if needed)
oci bv volume-backup create \
  --volume-id <volume-ocid> \
  --display-name "maintenance-$(date +%Y%m%d-%H%M%S)"

# Verify backup
ls -la /opt/atlas/backups/
```

#### 3. Perform Edit/Maintenance
```bash
# Enable maintenance mode
touch /opt/atlas/data/.maintenance

# Access sqlite-web for direct edits
ssh -L 8002:127.0.0.1:8002 user@your-oci-vm
sqlite_web /opt/atlas/data/atlas.db --host 127.0.0.1 --port 8002
# Browse to http://localhost:8002

# OR use sqlite3 CLI
sqlite3 /opt/atlas/data/atlas.db
```

#### 4. Resume Operations
```bash
# Disable maintenance mode
rm -f /opt/atlas/data/.maintenance

# Restart timers
sudo systemctl start atlas-export.timer
sudo systemctl start atlas-import.timer
sudo systemctl start atlas-backup.timer

# Verify all services are running
sudo systemctl status atlas-*.timer
/opt/atlas/bin/health-check.sh
```

## Emergency Procedures

### 🚨 Database Corruption Recovery

**Symptoms**:
- SQLite errors in logs
- Data inconsistencies
- Sync failures

**Recovery Steps**:

1. **Immediate Response**:
   ```bash
   # Stop all services immediately
   sudo systemctl stop atlas-*.timer

   # Check database integrity
   sqlite3 /opt/atlas/data/atlas.db "PRAGMA integrity_check;"
   ```

2. **Assess Damage**:
   ```bash
   # Try to open database
   sqlite3 /opt/atlas/data/atlas.db ".tables"

   # Check WAL file
   ls -la /opt/atlas/data/atlas.db*

   # Check recent backups
   ls -la /opt/atlas/backups/
   ```

3. **Recovery Options**:

   **Option A: WAL Recovery**
   ```bash
   # Try WAL checkpoint
   sqlite3 /opt/atlas/data/atlas.db "PRAGMA wal_checkpoint(FULL);"
   ```

   **Option B: Backup Restore**
   ```bash
   # Find latest good backup
   LATEST_BACKUP=$(ls -t /opt/atlas/backups/atlas_*.db | head -1)

   # Restore backup
   cp "$LATEST_BACKUP" /opt/atlas/data/atlas.db.restored

   # Test restored database
   sqlite3 /opt/atlas/data/atlas.db.restored "PRAGMA integrity_check;"

   # If good, replace current
   mv /opt/atlas/data/atlas.db /opt/atlas/data/atlas.db.corrupted
   mv /opt/atlas/data/atlas.db.restored /opt/atlas/data/atlas.db
   ```

   **Option C: OCI Snapshot Restore**
   ```bash
   # Use OCI Console or CLI to restore from snapshot
   # This replaces the entire block volume
   # Follow OCI documentation for block volume restore
   ```

### 🔌 Google Sheets API Outage

**Symptoms**:
- Sync errors in logs
- 401/403/429 HTTP errors
- Service account authentication failures

**Response**:

1. **Verify Connectivity**:
   ```bash
   # Test basic connectivity
   curl -I https://sheets.googleapis.com

   # Check service account credentials
   /opt/atlas/bin/test-sheets-auth.py
   ```

2. **Fallback to Read-Only Mode**:
   ```bash
   # Stop import/export
   sudo systemctl stop atlas-export.timer
   sudo systemctl stop atlas-import.timer

   # Continue with local operations only
   # Alert team that approvals are offline
   ```

3. **Manual Sync When Restored**:
   ```bash
   # Test connectivity
   /opt/atlas/bin/test-sheets-auth.py

   # Manual export to catch up
   /opt/atlas/bin/export-to-sheets.py --full-sync

   # Manual import of pending approvals
   /opt/atlas/bin/import-from-sheets.py --force-check
   ```

### 💾 Disk Space Emergency

**Symptoms**:
- Disk space warnings
- SQLite write failures
- Backup failures

**Response**:

1. **Immediate Triage**:
   ```bash
   # Check disk usage
   df -h /opt/atlas/

   # Find large files
   du -sh /opt/atlas/* | sort -hr

   # Check log sizes
   ls -lah /opt/atlas/logs/
   ```

2. **Quick Cleanup**:
   ```bash
   # Rotate logs immediately
   sudo logrotate -f /etc/logrotate.d/atlas

   # Clean old backups (keep only 3 most recent)
   cd /opt/atlas/backups/
   ls -t atlas_*.db | tail -n +4 | xargs rm -f

   # Clean system logs if needed
   sudo journalctl --vacuum-time=1d
   ```

3. **Long-term Solution**:
   ```bash
   # Extend OCI block volume (if needed)
   # Configure better log rotation
   # Implement backup archival to Object Storage
   ```

## Routine Maintenance

### Daily Health Checks

**Automated** (via atlas-health.timer):
```bash
# Script runs automatically every 15 minutes
# Check status: sudo systemctl status atlas-health.timer
# View logs: journalctl -u atlas-health.service
```

**Manual Verification**:
```bash
# Run comprehensive health check
/opt/atlas/bin/health-check.sh --verbose

# Check sync status
/opt/atlas/bin/check-sync-health.py

# Review error trends
/opt/atlas/bin/error-summary.py --last-24h
```

### Weekly Tasks

**Every Monday**:
```bash
# Review pending approvals older than 7 days
/opt/atlas/bin/stale-approvals-report.py

# Analyze error patterns
/opt/atlas/bin/error-trend-analysis.py --last-week

# Check backup integrity
/opt/atlas/bin/test-backup-restore.sh

# Update documentation if patterns emerge
```

### Monthly Tasks

**First Friday of Month**:
```bash
# Full system backup test
/opt/atlas/bin/disaster-recovery-test.sh

# Performance analysis
/opt/atlas/bin/performance-report.py --last-month

# Security review
/opt/atlas/bin/security-audit.sh

# Capacity planning review
/opt/atlas/bin/capacity-forecast.py
```

## Monitoring and Alerting

### Key Metrics to Monitor

**System Health**:
- Disk usage: <80%
- Memory usage: <90%
- CPU load: <2.0 (15min average)
- Network connectivity: 100%

**Application Health**:
- Sync success rate: >99%
- Approval response time: <4 hours average
- Error resolution rate: >90% within 24h
- Database response time: <100ms average

**Business Metrics**:
- Tasks completed per day
- Human intervention rate
- Agent efficiency trends
- Learning pattern adoption

### Alert Configuration

**Critical (Immediate)**:
- Database corruption detected
- Sync offline >1 hour
- Disk space >95%
- Security validation failure

**Warning (Next Business Day)**:
- Sync success rate <99%
- Pending approvals >24h old
- Error rate trending up
- Performance degradation

**Info (Weekly Summary)**:
- Usage statistics
- Trend analysis
- Capacity forecasts
- System health summary

## Troubleshooting Guide

### Common Issues

**Issue**: Sync keeps failing
**Symptoms**: Error logs show repeated sync failures
**Solution**:
```bash
# Check network connectivity
ping sheets.googleapis.com

# Verify credentials
/opt/atlas/bin/test-sheets-auth.py

# Check API quotas
# Review Google Cloud Console for API usage

# Restart sync services
sudo systemctl restart atlas-export.timer atlas-import.timer
```

**Issue**: Database locked errors
**Symptoms**: SQLite reports database is locked
**Solution**:
```bash
# Check for hanging processes
ps aux | grep sqlite
ps aux | grep atlas

# Kill hanging processes if found
sudo pkill -f atlas

# Check WAL mode is enabled
sqlite3 /opt/atlas/data/atlas.db "PRAGMA journal_mode;"

# Should return "wal" - if not, re-enable:
sqlite3 /opt/atlas/data/atlas.db "PRAGMA journal_mode=WAL;"
```

**Issue**: Approvals not syncing
**Symptoms**: Changes in Sheets don't appear in database
**Solution**:
```bash
# Check import logs
tail -f /opt/atlas/logs/import.log

# Manual import test
/opt/atlas/bin/import-from-sheets.py --dry-run

# Verify sheet permissions
/opt/atlas/bin/test-sheets-permissions.py
```

### Log Locations

```bash
# Application logs
/opt/atlas/logs/export.log      # DB → Sheets sync
/opt/atlas/logs/import.log      # Sheets → DB sync
/opt/atlas/logs/health.log      # Health checks
/opt/atlas/logs/backup.log      # Backup operations

# System logs
journalctl -u atlas-export.service
journalctl -u atlas-import.service
journalctl -u atlas-health.service

# Database logs
# SQLite doesn't log by default, monitor via application logs
```

## Security Procedures

### Access Review

**Monthly**: Review who has access to:
- SSH keys for the VM
- Google Sheets with project data
- OCI Console for the account
- Database backup locations

### Key Rotation

**Quarterly**: Rotate:
- Google Sheets service account keys
- SSH keys for VM access
- OCI API keys (if used)

```bash
# Update service account key
# 1. Generate new key in Google Cloud Console
# 2. Update /opt/atlas/config/sheets-credentials.json
# 3. Test with /opt/atlas/bin/test-sheets-auth.py
# 4. Revoke old key
```

### Incident Response

1. **Detect**: Monitoring alerts or manual discovery
2. **Assess**: Determine scope and impact
3. **Contain**: Stop automated processes if needed
4. **Investigate**: Collect logs and evidence
5. **Remediate**: Fix the root cause
6. **Recover**: Restore normal operations
7. **Learn**: Document lessons and update procedures

---

*Keep this runbook updated as procedures evolve. Test emergency procedures regularly.*