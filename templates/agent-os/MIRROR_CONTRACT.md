# 📋 Mirror Contract: Google Sheets ↔ SQLite Sync

## Overview

This document defines the exact data flow between Google Sheets (human interface) and SQLite (source of truth). The contract ensures data integrity while enabling human oversight.

## Fundamental Principles

1. **SQLite is Source of Truth**: All persistent data lives in SQLite
2. **Sheets is Human Interface**: Used for approvals, reviews, and visibility only
3. **Bidirectional Sync**: Limited, controlled data flows both ways
4. **Approval Workflow**: Critical changes require human approval
5. **Audit Trail**: All changes are logged and traceable

## Sheet Structure

### Tab 1: Pending_Approvals

**Purpose**: Human approval workflow for critical operations

**Columns** (Fixed Header):
```
A: ID           (Text, Primary Key)
B: Type         (Text, Enum: task|project|config|deployment)
C: Action       (Text, Enum: create|update|delete|execute)
D: Item         (Text, Summary of what's being changed)
E: Status       (Text, Enum: pending|approved|rejected)
F: Requested    (DateTime, When approval was requested)
G: Notes        (Text, Human can add context/reasoning)
H: Payload      (Text, JSON data for the change)
```

**Data Flow**:
- **DB → Sheets**: New approval requests appear automatically
- **Sheets → DB**: Only Status and Notes columns sync back
- **Sync Frequency**: Every hour
- **Validation**: Status must be approved|rejected, Notes optional

**Example Row**:
```
approval-123 | task | create | "Add OAuth integration" | pending | 2024-01-15 14:30 | | {"title":"Add OAuth","assignee":"AI IDE Agent"}
```

### Tab 2: Runs

**Purpose**: Execution tracking and monitoring

**Columns** (Fixed Header):
```
A: ID           (Text, Primary Key)
B: Task         (Text, Task title/reference)
C: Command      (Text, What was executed)
D: Status       (Text, Enum: running|success|failed|cancelled)
E: Started      (DateTime, Execution start time)
F: Completed    (DateTime, Execution end time)
G: Output       (Text, Truncated execution output)
H: Notes        (Text, Human can add observations)
```

**Data Flow**:
- **DB → Sheets**: All run records appear automatically
- **Sheets → DB**: Only Notes column syncs back
- **Sync Frequency**: Every hour
- **Retention**: Last 100 runs (older records archived)

**Example Row**:
```
run-456 | "Setup database" | "sqlite3 atlas.db < schema.sql" | success | 2024-01-15 14:30 | 2024-01-15 14:32 | "Database created successfully" | "Looks good"
```

### Tab 3: Errors_Hotlist

**Purpose**: Error tracking and resolution

**Columns** (Fixed Header):
```
A: ID           (Text, Primary Key)
B: Task         (Text, Related task)
C: Error        (Text, Error summary)
D: Timestamp    (DateTime, When error occurred)
E: Severity     (Text, Enum: low|medium|high|critical)
F: Resolved     (Text, Enum: false|true)
G: Resolution   (Text, How it was resolved)
H: Notes        (Text, Human analysis/context)
```

**Data Flow**:
- **DB → Sheets**: New errors appear automatically
- **Sheets → DB**: Resolved, Resolution, and Notes columns sync back
- **Sync Frequency**: Every 15 minutes for critical errors, hourly for others
- **Retention**: Resolved errors older than 30 days are archived

**Example Row**:
```
err-789 | "Deploy to staging" | "Connection timeout to database" | 2024-01-15 14:30 | high | false | | "Check network connectivity"
```

## Sync Rules and Validation

### Export (DB → Sheets)

**What Syncs**:
- New approval requests (append only)
- Updated run records (status changes)
- New error records (append only)
- Status updates for existing items

**What Doesn't Sync**:
- Deleted records (soft delete only)
- Historical data older than retention period
- Sensitive data (passwords, keys, tokens)
- Large payloads (>1000 characters truncated)

**Validation Rules**:
- All required columns must have values
- Enum fields must match allowed values
- Timestamps must be valid ISO format
- JSON payloads must be valid (or marked as invalid)

### Import (Sheets → DB)

**Allowed Changes**:
- Approval status changes (pending → approved/rejected)
- Notes additions/updates (append-only)
- Error resolution status updates
- Resolution descriptions

**Forbidden Changes**:
- Primary key modifications
- Timestamp alterations
- System-generated data changes
- Status changes that violate workflow rules

**Validation Process**:
1. **Schema Validation**: Check column types and constraints
2. **Business Logic**: Verify workflow state transitions
3. **Data Integrity**: Ensure referential integrity
4. **Audit Trail**: Log all changes with timestamps

## Error Handling

### Sync Failures

**Export Failures** (DB → Sheets):
- Log error details to /opt/atlas/logs/export.log
- Retry with exponential backoff (max 3 attempts)
- Alert on persistent failures
- Continue with next batch (don't block)

**Import Failures** (Sheets → DB):
- Log validation errors with row details
- Skip invalid rows, process valid ones
- Create error report in Errors_Hotlist tab
- Send summary to configured notification channels

### Data Conflicts

**Duplicate IDs**:
- Use database ID as authoritative
- Log conflict details
- Update Sheets with database version
- Notify humans of discrepancy

**Invalid State Transitions**:
- Reject the change
- Log the attempted transition
- Add explanation to Notes field
- Keep original state in database

## Security and Access Control

### Google Sheets Permissions

**Required Access**:
- Read: All tabs, all columns
- Write: Limited columns (Status, Notes, Resolved, Resolution)
- Share: Project team members only
- API: Service account with minimal scope

**Forbidden Operations**:
- Sheet structure changes
- Column additions/deletions
- Formula modifications
- Bulk data imports/exports outside sync process

### Data Sanitization

**Outgoing (DB → Sheets)**:
- Strip sensitive patterns (API keys, passwords)
- Truncate large text fields
- Escape special characters
- Validate JSON before export

**Incoming (Sheets → DB)**:
- Sanitize all text inputs
- Validate against allowed values
- Check for injection patterns
- Limit field lengths

## Monitoring and Alerting

### Success Metrics

- Sync completion rate: >99%
- Data validation pass rate: >95%
- Human response time: <4 hours average
- Error resolution time: <24 hours for critical

### Alert Conditions

**Immediate Alerts** (Critical):
- Sync failures for >1 hour
- Data corruption detected
- Security validation failures
- Critical errors not acknowledged in 2 hours

**Daily Alerts** (Warning):
- Pending approvals >24 hours old
- Validation failure rate >5%
- Unresolved errors trending up
- Sync latency trending up

### Health Checks

**Every 15 Minutes**:
- Verify Sheets API connectivity
- Check last successful sync timestamp
- Validate recent data samples
- Monitor error rates

**Daily**:
- Data integrity checks
- Performance trend analysis
- Approval workflow effectiveness
- Error resolution patterns

## Implementation Scripts

### Export Script: `export-to-sheets.py`

```python
# Reads from SQLite, writes to Google Sheets
# Handles data validation and error logging
# Respects rate limits and retry logic
```

### Import Script: `import-from-sheets.py`

```python
# Reads approved changes from Sheets
# Validates against business rules
# Updates SQLite with audit trail
```

### Health Check: `check-mirror-health.py`

```python
# Validates sync integrity
# Reports on approval workflow health
# Monitors error resolution rates
```

---

*This contract maintains data integrity while enabling effective human oversight of automated systems.*