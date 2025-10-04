# 🛠️ Global Stack Preferences

## Default Technology Choices

These preferences apply when starting new projects or when project-specific requirements don't dictate otherwise. They prioritize simplicity, cost-effectiveness, and reliability.

### Database Layer

**Primary Choice**: SQLite with WAL mode
```
Rationale:
- Zero configuration and maintenance
- ACID compliance with good performance
- Perfect for single-writer, many-reader patterns
- Excellent tooling ecosystem
- Easy backup and replication

When to use alternatives:
- Multi-writer requirements → PostgreSQL
- Distributed requirements → Consider cloud databases
- Extreme scale → Specialized solutions
```

**Schema Management**:
```sql
-- Always enable WAL mode for concurrency
PRAGMA journal_mode=WAL;

-- Set reasonable timeouts
PRAGMA busy_timeout=30000;

-- Optimize for typical workloads
PRAGMA cache_size=10000;
PRAGMA synchronous=NORMAL;
```

### Human Interface Layer

**Primary Choice**: Google Sheets integration
```
Rationale:
- Universal accessibility (no special software)
- Familiar interface for non-technical users
- Built-in collaboration features
- Free for typical usage levels
- Good API with reasonable limits

When to use alternatives:
- >100k rows → Custom web interface
- Complex workflows → Dedicated apps
- Offline requirements → Local tools
```

**Structure Standards**:
- Fixed headers in row 1
- Data starts in row 2
- Maximum 26 columns (A-Z)
- Use data validation where possible
- Document column purposes clearly

### Data Access Layer

**Read-Only Interface**: Datasette
```
Rationale:
- Zero-config web interface for SQLite
- Rich query capabilities without SQL injection risk
- Plugin ecosystem for extensions
- Automatic API generation
- Perfect for data exploration

Configuration:
datasette serve db.sqlite --immutable --host 127.0.0.1
```

**Direct Edit Interface**: sqlite-web
```
Rationale:
- Full SQLite functionality via web interface
- No installation required on client machines
- Syntax highlighting and query history
- Safe for SSH tunnel access

Usage:
sqlite_web db.sqlite --host 127.0.0.1 --port 8002
```

### Automation Layer

**Primary Choice**: systemd timers
```
Rationale:
- Built into most Linux distributions
- Reliable scheduling with logging
- Better than cron for complex scenarios
- Integrated with system logging
- Good dependency management

Alternative:
- Simple cron for basic tasks
- GitHub Actions for CI/CD
- Cloud functions for event-driven tasks
```

**Timer Pattern**:
```ini
[Unit]
Description=Service description
Requires=service-name.service

[Timer]
OnCalendar=hourly
Persistent=true

[Install]
WantedBy=timers.target
```

### Scripting and Development

**Primary Language**: Python 3.8+
```
Rationale:
- Excellent library ecosystem
- Good SQLite support
- Great for data processing
- Easy Google Sheets integration
- Readable and maintainable

Required packages:
- sqlite3 (built-in)
- requests (HTTP/API)
- pandas (data processing)
- google-api-python-client (Sheets)
```

**Alternative Languages**:
- **Shell/Bash**: System administration tasks
- **JavaScript/Node.js**: When integrating with existing JS projects
- **Go**: Performance-critical applications
- **Rust**: Systems programming needs

### Infrastructure and Deployment

**Preferred Platform**: OCI (Oracle Cloud Infrastructure)
```
Rationale:
- Generous always-free tier
- Good performance for price
- Reliable global infrastructure
- Integrated backup solutions
- ARM-based instances available

Free tier includes:
- 2x VM.Standard.E2.1.Micro instances
- 200GB block storage
- 10GB object storage
- Network and backup allowances
```

**Alternative Platforms**:
- **AWS**: If already invested in AWS ecosystem
- **GCP**: If using Google Workspace heavily
- **Hetzner**: EU-focused, cost-effective
- **DigitalOcean**: Simple pricing and interface

### Backup and Storage

**Primary Strategy**: Block volume snapshots
```
Rationale:
- Atomic point-in-time backups
- Fast recovery times
- Cost-effective for small databases
- Integrated with cloud platform
- No additional services to manage

Schedule:
- Daily snapshots, retain 30 days
- Weekly snapshots, retain 12 weeks
- Monthly snapshots, retain 12 months
```

**Secondary Strategy**: Object storage
```
Rationale:
- Long-term archival storage
- Cross-region durability
- Very low cost for infrequent access
- Can store processed exports (Parquet, CSV)

Usage:
- Weekly SQLite database exports
- Monthly compressed log archives
- Quarterly system state snapshots
```

### Networking and Security

**Access Pattern**: SSH tunnels
```
Rationale:
- No public web interfaces to secure
- Leverages existing SSH infrastructure
- Works with existing access controls
- No additional firewall rules needed
- Can use existing VPN/bastion patterns

Example:
ssh -L 8001:127.0.0.1:8001 user@server
```

**Alternative Access**: Tailscale
```
Rationale:
- Zero-config mesh VPN
- Works across all device types
- Replaces need for complex networking
- Good for team collaboration
- Free tier sufficient for small teams

Setup:
curl -fsSL https://tailscale.com/install.sh | sh
tailscale up
```

### Monitoring and Alerting

**Basic Monitoring**: systemd + journald
```
Rationale:
- Built into most Linux systems
- Centralized logging with retention policies
- Good integration with timers and services
- No additional services to manage

Usage:
journalctl -u service-name -f
journalctl --since "1 hour ago"
```

**Advanced Monitoring**: Uptime Kuma
```
Rationale:
- Self-hosted, no external dependencies
- Simple web interface
- Multiple notification channels
- Light resource usage
- Docker-based deployment

Alternatives:
- Healthchecks.io (hosted)
- Custom scripts + email/SMS
- Cloud platform monitoring
```

### API and Integration Patterns

**HTTP Client**: Python requests
```python
import requests
import time
from functools import wraps

def retry_on_failure(max_retries=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except requests.RequestException as e:
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(delay * (2 ** attempt))
            return wrapper
        return decorator
```

**Authentication**: Service accounts
- Use service accounts, not user credentials
- Rotate keys quarterly
- Minimal required permissions
- Store credentials outside git repository

### Version Control and Configuration

**Repository Structure**:
```
project-root/
├── .agent-os/          # Agent specifications
├── bin/                # Executable scripts
├── config/             # Configuration files
├── data/               # Data files (gitignored)
├── docs/               # Documentation
├── scripts/            # Automation scripts
├── tests/              # Test files
├── .env.template       # Environment template
├── .gitignore          # Standard ignore patterns
└── README.md           # Project documentation
```

**Configuration Management**:
- Use .env files for secrets (gitignored)
- Provide .env.template for documentation
- Use config files for non-secret settings
- Document all configuration options

### Testing and Quality Assurance

**Testing Framework**: pytest (Python) or built-in (shell)
```bash
# Python testing
python -m pytest tests/ -v

# Shell testing
./tests/run-all-tests.sh
```

**Code Quality Tools**:
- **Python**: black (formatting), ruff (linting)
- **Shell**: shellcheck (linting), shfmt (formatting)
- **SQL**: sqlfluff (linting and formatting)

**Documentation Standards**:
- README.md for project overview
- RUNBOOK.md for operational procedures
- API documentation for all scripts
- Decision records for architectural choices

---

*These preferences can be overridden for specific projects, but provide sensible defaults that work well together and minimize operational complexity.*