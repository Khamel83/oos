# Agent Operating Spec (OOS)

## Always load (authoritative rules)
- ops/docs/PREFERRED_STACK.md
- ops/docs/MIRROR_CONTRACT.md
- ops/docs/RUNBOOK.md
- ops/docs/BACKUP_POLICY.md
- ops/stack.yaml
- ops/.env.template  (structure only; do not read secrets from git)

## Guardrails
- Source of Truth (SoT) is SQLite (WAL). No routine human edits.
- Google Sheets is a mirror; only `approved`, `notes` flow back to DB.
- Before proposing changes: run `make -C ops preflight` and check timers.

## Kickoff tasks (every session)
1. Validate PRAGMAs: WAL + busy_timeout=5000.
2. Confirm required tables exist: runs, items, admin_changes.
3. Confirm tools installed: datasette (RO), sqlite-web (RW).
4. Confirm timers active: export-to-sheets, writeback-from-sheets, backup-sqlite.
5. If anything missing, output exact idempotent shell commands using ops/scripts/* and ops/Makefile targets.

## Output discipline
- Prefer `make` targets and scripts under ops/.
- Propose minimal, reversible changes. Always show commands.