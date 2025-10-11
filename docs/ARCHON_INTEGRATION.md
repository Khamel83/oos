# Archon Integration for OOS

## CRITICAL: Mandatory Archon Usage

OOS requires explicit use of Archon tools for all knowledge queries and task management. This document defines how Claude Code must interact with Archon when working in an OOS environment.

## The Problem OOS Solves

Without explicit instructions, Claude Code won't automatically use Archon tools. This integration ensures systematic use of your brain extension's knowledge base and task tracking.

## Archon Tools Available

When connected to Archon (archon.khamel.com), you have these tools:

### Knowledge Base Tools
- `archon_query_knowledge` - Search uploaded docs, crawled websites
- `archon_list_sources` - See available data sources for filtering

### Task Management Tools
- `archon_create_task` - Add new tasks
- `archon_read_task` - Get task details
- `archon_update_task` - Update task status/details
- `archon_delete_task` - Remove tasks
- `archon_list_tasks` - See all project tasks

### Project Tools
- `archon_create_project` - Initialize project structure
- `archon_read_project` - Get project metadata
- `archon_update_project` - Modify project settings

## Mandatory Usage Rules

### Rule 1: Search Archon Before Answering

**BEFORE answering ANY question about:**
- OOS documentation → `archon_query_knowledge("OOS [topic]")`
- USC policies/procedures → `archon_query_knowledge("USC [topic]")`
- Project-specific patterns → `archon_query_knowledge("[project] patterns")`
- Python best practices for THIS project → Search Archon first

**Never answer from general knowledge if project-specific info exists in Archon.**

### Rule 2: Check Tasks Before Suggesting Work

**BEFORE suggesting what to work on:**
```
archon_list_tasks(project_id="[current-project]")
```

**BEFORE starting coding session:**
```
archon_list_tasks(status="in_progress")
```

### Rule 3: Update Tasks During Work

**AFTER completing work:**
```
archon_update_task(task_id="...", status="completed")
```

**WHEN starting new work:**
```
archon_update_task(task_id="...", status="in_progress")
```

## Integration with OOS Commands

### /start-coding Integration

When user runs `/start-coding`, automatically:
1. Check Archon connection status
2. List current project tasks
3. Query Archon for project context
4. Show what's in progress

### /help-me Integration

When user runs `/help-me`:
1. Search Archon knowledge base for relevant docs
2. Check if there are related tasks
3. Use Archon context to provide specific help

### /archon-* Commands

These commands are explicitly about Archon:
- `/archon-status` → Call `archon_read_project` and `archon_list_tasks`
- `/archon-task-start` → Call `archon_update_task` with status="in_progress"
- `/archon-complete` → Call `archon_update_task` with status="completed"
- `/archon-research` → Call `archon_query_knowledge`

## Response Patterns

### Pattern 1: Documentation Questions

User: "How do I handle database connections in OOS?"

CORRECT:
```
Let me search your OOS documentation in Archon.
[calls archon_query_knowledge("OOS database connection patterns")]
Based on your project docs: [answer from Archon results]
```

INCORRECT:
```
❌ "Typically in Python you'd use SQLAlchemy..."
```

### Pattern 2: Task Planning

User: "What should I work on next?"

CORRECT:
```
[calls archon_list_tasks(project_id="oos", status="todo")]
Based on your Archon task list: [list top priorities]
```

INCORRECT:
```
❌ "You could work on improving error handling..."
```

### Pattern 3: USC-Specific Questions

User: "What's the vacation policy?"

CORRECT:
```
[calls archon_query_knowledge("USC vacation policy HR")]
According to your uploaded USC HR docs: [answer]
```

INCORRECT:
```
❌ "I don't have access to USC-specific policies..."
```

## Default Behavior

### Always Assume Archon is Available

Never say:
- ❌ "I don't have access to your docs"
- ❌ "I can't see your task list"
- ❌ "Let me check if Archon is connected"

Instead:
- ✅ Use Archon tools immediately
- ✅ If tool fails, THEN explain the connection issue

### Always Be Specific

Don't say:
- ❌ "Check your task manager"
- ❌ "Look at your documentation"

Instead:
- ✅ "I checked your Archon task list and found..."
- ✅ "According to your Archon knowledge base..."

## What's in Archon for OOS

### Expected Knowledge Base Content

- OOS documentation (README, guides, system vision)
- USC HR policies and procedures
- Python patterns and best practices for this workflow
- Project-specific conventions and standards
- 1Password integration docs
- Archon integration docs (this file)

### Expected Project Structure

- Project Name: `oos`
- Features organized by component (core, integrations, commands)
- Tasks tracking development work
- Status tracking (todo, in_progress, done, blocked)

## Testing Integration

### Verify Archon Connection

In Claude Code:
```
Search my Archon docs for OOS start-coding command
```

Should return documentation about `/start-coding`.

### Verify Task Management

In Claude Code:
```
What's on my Archon task list for OOS?
```

Should list actual tasks from Archon.

## Troubleshooting

### "Archon tools not working"

1. Check MCP connection: `claude mcp list`
2. Should show: `archon: http://archon.khamel.com:8051/mcp`
3. If missing, reconnect: `claude mcp add --transport http archon https://archon.khamel.com:8051/mcp`

### "Can't find docs in Archon"

1. Verify docs are uploaded at archon.khamel.com:3737
2. Check Knowledge Base tab
3. Upload missing documentation
4. Retry query after upload

### "Tasks not showing"

1. Verify project exists in Archon
2. Check project name matches (case-sensitive)
3. Ensure tasks are created in correct project

## Future Enhancements

- Automatic Archon query injection in all OOS commands
- Smart context loading from Archon on `/start-coding`
- Automatic task creation from commit messages
- Integration with `/brain-dump` for task extraction

## 🏗️ Project Architecture

### Project Isolation Model

```
Archon Server
├── Project Alpha (ID: 550e8400-...)
│   ├── Tasks (filtered by project_id)
│   ├── Documents (scoped to project)
│   ├── Features (project-specific)
│   └── Versions (project history)
├── Project Beta (ID: 7a8b9c0d-...)
│   ├── Tasks (completely separate)
│   ├── Documents (independent)
│   ├── Features (isolated)
│   └── Versions (separate history)
└── Project Gamma (ID: 2f3e4d5c-...)
    └── (fully isolated scope)
```

### Environment Configuration

Each project maintains its own `.env` file with unique identifiers:

```bash
# Each project's .env contains:
ARCHON_PROJECT_ID=<unique-project-id-from-archon>
ARCHON_URL=<your-archon-server-url>
PROJECT_NAME=<project-name>
PROJECT_TYPE=<project-type>
```

## ✅ Current Implementation Status

**OOS v1.0+ includes full Archon integration:**
- ✅ Automatic MCP server registration
- ✅ Project creation helpers
- ✅ Task management via Claude Code MCP tools
- ✅ Environment configuration
- 🟡 CLI task management (in development)
- 🟡 Archon-aware slash commands (in development)

## 🚀 Automatic Integration (Default)

### 1. Archon Integration is Now Automatic

**As of OOS v1.0+, Archon integration happens automatically during bootstrap.**

#### Quick Setup for New Projects
```bash
# Navigate to your project directory
cd /home/ubuntu/dev/my-project

# Initialize OOS (Archon integration happens automatically)
eval "$(op signin)"
/path/to/oos/scripts/bootstrap_enhanced.sh

# The bootstrap script automatically:
# - Adds ARCHON_PROJECT_ID= to .env
# - Adds ARCHON_URL=http://your-archon-server:8051/mcp to .env
# - Creates bin/create_archon_project.sh helper script
# - Registers Archon MCP server with Claude Code
```

#### Complete Archon Project Creation
```bash
# Use the generated helper script (auto-detects GitHub repo)
./bin/create_archon_project.sh "My Project Title" "Project description"

# Follow the instructions to create the project in Claude Code:
# mcp__archon__create_project({
#     title: "My Project Title",
#     description: "Project description",
#     github_repo: "https://github.com/username/my-project" // auto-detected
# })

# Update .env with the returned project_id
echo "ARCHON_PROJECT_ID=<returned-project-id>" >> .env
```

### 2. Manual Integration (For Existing Projects)

If you have an existing project that needs Archon integration:

```bash
# Re-run bootstrap to add Archon integration
/path/to/oos/scripts/bootstrap_enhanced.sh --force

# Or manually add to existing .env:
echo "
# Archon MCP Integration
ARCHON_PROJECT_ID=
ARCHON_URL=http://your-archon-server:8051/mcp" >> .env
```

### 2. Task Management Integration

#### Create Project Tasks with Proper Scoping

```javascript
// Authentication Feature Tasks
mcp__archon__create_task({
    project_id: "$ARCHON_PROJECT_ID",
    title: "Design JWT token architecture",
    description: `Design JWT token structure with:
- Access token (15 min expiry)
- Refresh token (30 day expiry)
- Token rotation strategy
- Secure token storage patterns`,
    assignee: "AI IDE Agent",
    feature: "authentication",
    task_order: 5,
    sources: [
        {
            url: "https://tools.ietf.org/rfc/rfc7519.txt",
            type: "specification",
            relevance: "JWT standard specification"
        }
    ]
})

mcp__archon__create_task({
    project_id: "$ARCHON_PROJECT_ID",
    title: "Implement user login endpoint",
    description: `Create POST /auth/login endpoint:
- Email/password validation
- Rate limiting (5 attempts per minute)
- JWT generation on success
- Secure password hashing verification`,
    assignee: "AI IDE Agent",
    feature: "authentication",
    task_order: 10,
    code_examples: [
        {
            file: "examples/auth/login.py",
            function: "login_handler",
            purpose: "Reference implementation pattern"
        }
    ]
})

// Database Feature Tasks
mcp__archon__create_task({
    project_id: "$ARCHON_PROJECT_ID",
    title: "Create user database schema",
    description: `PostgreSQL schema design:
- users table (id, email, password_hash, created_at, updated_at)
- user_sessions table (token_id, user_id, expires_at, created_at)
- oauth_tokens table (provider, provider_id, user_id, tokens)
- Proper indexes and constraints`,
    assignee: "AI IDE Agent",
    feature: "database",
    task_order: 3
})

// OAuth Integration Tasks
mcp__archon__create_task({
    project_id: "$ARCHON_PROJECT_ID",
    title: "Implement Google OAuth2 provider",
    description: `OAuth2 integration with PKCE:
- Authorization URL generation
- Code exchange implementation
- User info retrieval and mapping
- Account linking logic`,
    assignee: "AI IDE Agent",
    feature: "oauth",
    task_order: 20
})
```

#### Task Workflow Management

```javascript
// Get project-specific tasks
mcp__archon__list_tasks({
    project_id: "$ARCHON_PROJECT_ID",
    filter_by: "status",
    filter_value: "todo"
})

// Start working on a task
mcp__archon__update_task({
    task_id: "task-uuid-from-above",
    status: "doing"
})

// Complete a task
mcp__archon__update_task({
    task_id: "task-uuid",
    status: "done"
})

// Move task to review
mcp__archon__update_task({
    task_id: "task-uuid",
    status: "review"
})
```

### 3. Documentation Management

#### Create Project Documentation

```javascript
// Technical Specification
mcp__archon__create_document({
    project_id: "$ARCHON_PROJECT_ID",
    title: "Authentication API Specification v1.0",
    document_type: "spec",
    content: {
        version: "1.0.0",
        base_url: "https://api.example.com/auth",
        authentication: "Bearer JWT tokens",
        endpoints: [
            {
                path: "/login",
                method: "POST",
                description: "User authentication",
                request: {
                    email: "string (required)",
                    password: "string (required)"
                },
                responses: {
                    200: "Login successful with tokens",
                    401: "Invalid credentials",
                    429: "Rate limit exceeded"
                }
            },
            {
                path: "/refresh",
                method: "POST",
                description: "Token refresh",
                headers: {
                    "Authorization": "Bearer <refresh_token>"
                },
                responses: {
                    200: "New access token provided",
                    401: "Invalid refresh token"
                }
            },
            {
                path: "/logout",
                method: "POST",
                description: "User logout",
                headers: {
                    "Authorization": "Bearer <access_token>"
                },
                responses: {
                    200: "Logout successful",
                    401: "Invalid token"
                }
            }
        ],
        security: {
            rate_limiting: "5 requests per minute per IP",
            cors: "Enabled for allowed origins",
            csrf: "Required for state-changing operations"
        }
    },
    tags: ["api", "authentication", "specification"],
    author: "Development Team"
})

// Architecture Design Document
mcp__archon__create_document({
    project_id: "$ARCHON_PROJECT_ID",
    title: "Authentication System Architecture",
    document_type: "design",
    content: {
        overview: "JWT-based authentication system with OAuth2 integration",
        components: [
            {
                name: "AuthController",
                responsibility: "Handle authentication endpoints",
                dependencies: ["UserService", "TokenService", "RateLimiter"]
            },
            {
                name: "TokenService",
                responsibility: "JWT generation and validation",
                dependencies: ["SecretManager", "DatabaseService"]
            },
            {
                name: "OAuth2Service",
                responsibility: "OAuth provider integration",
                dependencies: ["HttpClient", "UserService"]
            }
        ],
        data_flow: [
            "User submits credentials",
            "AuthController validates input",
            "UserService verifies credentials",
            "TokenService generates JWT tokens",
            "Response sent with tokens"
        ],
        security_considerations: [
            "Password hashing with bcrypt",
            "JWT tokens signed with RS256",
            "Refresh token rotation",
            "Rate limiting on auth endpoints",
            "CORS configuration",
            "Input validation and sanitization"
        ]
    },
    tags: ["architecture", "design", "authentication"]
})

// Implementation Guide
mcp__archon__create_document({
    project_id: "$ARCHON_PROJECT_ID",
    title: "Development Setup Guide",
    document_type: "guide",
    content: {
        prerequisites: [
            "Python 3.9+",
            "PostgreSQL 13+",
            "Redis 6+",
            "1Password CLI access"
        ],
        setup_steps: [
            "Clone repository",
            "Run OOS bootstrap: ./scripts/scripts/bootstrap_enhanced.sh",
            "Install dependencies: pip install -r requirements.txt",
            "Setup database: ./bin/setup_db.sh",
            "Run tests: ./bin/run_tests.sh all",
            "Start development server: ./bin/dev_server.sh"
        ],
        environment_variables: {
            "DATABASE_URL": "PostgreSQL connection string",
            "REDIS_URL": "Redis connection string",
            "JWT_SECRET": "JWT signing secret",
            "OAUTH_GOOGLE_CLIENT_ID": "Google OAuth client ID",
            "OAUTH_GOOGLE_CLIENT_SECRET": "Google OAuth client secret"
        },
        testing: {
            unit_tests: "./bin/run_tests.sh unit",
            integration_tests: "./bin/run_tests.sh integration",
            security_tests: "./bin/run_tests.sh security"
        }
    },
    tags: ["guide", "setup", "development"]
})
```

### 4. Version Control Integration

#### Document Versioning
```javascript
// Create version snapshots for important milestones
mcp__archon__create_version({
    project_id: "$ARCHON_PROJECT_ID",
    field_name: "docs",
    content: [
        // Current state of all documents
    ],
    change_summary: "Initial API specification and architecture design",
    created_by: "Development Team"
})

// Version project features
mcp__archon__create_version({
    project_id: "$ARCHON_PROJECT_ID",
    field_name: "features",
    content: {
        authentication: {
            status: "in_progress",
            completion: 60,
            components: ["login", "logout", "token_refresh"],
            tests_passing: true
        },
        oauth: {
            status: "planned",
            providers: ["google", "github"],
            completion: 0
        },
        database: {
            status: "completed",
            schema_version: "1.0",
            migrations_applied: 5
        }
    },
    change_summary: "Authentication 60% complete, database schema finalized"
})
```

## 🔒 Security & Isolation Best Practices

### Environment Isolation
```bash
# Each project has isolated environment
# Project Alpha
cat /home/ubuntu/dev/auth-service/.env
ARCHON_PROJECT_ID=$ARCHON_PROJECT_ID
PROJECT_SECRETS_PREFIX=AUTH_SERVICE_

# Project Beta
cat /home/ubuntu/dev/ecommerce-web/.env
ARCHON_PROJECT_ID=$ARCHON_PROJECT_ID_B
PROJECT_SECRETS_PREFIX=ECOMMERCE_WEB_

# No cross-project access possible
```

### Access Control Validation
```bash
# Verify project isolation in each project directory

# Project Alpha - should only see its own data
cd /home/ubuntu/dev/auth-service
# In Claude Code:
# mcp__archon__list_tasks(project_id="$ARCHON_PROJECT_ID")
# Result: Only auth-service tasks

# Project Beta - completely isolated
cd /home/ubuntu/dev/ecommerce-web
# In Claude Code:
# mcp__archon__list_tasks(project_id="$ARCHON_PROJECT_ID_B")
# Result: Only ecommerce-web tasks
```

### Security Monitoring Per Project
```bash
# Each project maintains separate security audit trails
./bin/security_audit.sh scan --report auth-service-security.json
./bin/security_audit.sh compliance --report auth-service-compliance.json

# Separate monitoring logs
tail -f security_audit.log | grep "PROJECT_ID=550e8400"
```

## 🖥️ OOS CLI Integration (v1.1+)

### Task Management Commands

```bash
# List project tasks
./oos task list
./oos task list --status todo
./oos task list --feature authentication

# Start working on a task
./oos task start <task-id>

# Complete a task
./oos task complete <task-id>

# Create new task
./oos task create "Implement OAuth" "Add Google OAuth2 integration"

# Project status
./oos project status
```

### Capability Layer Integration

```bash
# Search capabilities
./oos capabilities
./oos capabilities "api documentation"

# Execute actions
./oos act "search for JWT best practices"
./oos act "list available API endpoints"
```

## 🤖 Claude Code Integration

### Current MCP Tools Available

```javascript
// Project Management
mcp__archon__create_project({title, description, github_repo})
mcp__archon__list_projects()
mcp__archon__get_project(project_id)
mcp__archon__update_project(project_id, {...updates})

// Task Management
mcp__archon__create_task({project_id, title, description, ...})
mcp__archon__list_tasks({project_id, filter_by, filter_value})
mcp__archon__get_task(task_id)
mcp__archon__update_task(task_id, {status, ...})

// Knowledge & Research
mcp__archon__perform_rag_query({query, source_domain, match_count})
mcp__archon__search_code_examples({query, match_count})

// Documentation
mcp__archon__create_document({project_id, title, document_type, content})
mcp__archon__list_documents(project_id)
mcp__archon__get_document(project_id, doc_id)
```

### Planned Slash Commands (v1.1)

```bash
/archon-status        # Show current project and tasks
/archon-task-start    # Create and start new task
/archon-research      # Search Archon knowledge base
/archon-complete      # Mark current work complete
```

## 🔄 Workflow Integration

### Development Workflow with Archon

#### 1. Daily Standup Workflow
```bash
# Morning routine - check project status
./bin/health_monitor.sh check

# In Claude Code - review project tasks:
# mcp__archon__list_tasks(
#     project_id="$ARCHON_PROJECT_ID",
#     filter_by="status",
#     filter_value="doing"
# )

# Start work on priority task
# mcp__archon__update_task(task_id="uuid", status="doing")
```

#### 2. Feature Development Workflow
```bash
# 1. Get task details
# mcp__archon__get_task(task_id="uuid")

# 2. Research phase - query knowledge base
# mcp__archon__perform_rag_query(
#     query="JWT authentication best practices",
#     match_count=5
# )

# 3. Code implementation
# Use task description and research findings

# 4. Testing and validation
./bin/run_tests.sh unit
./bin/security_audit.sh scan

# 5. Task completion
# mcp__archon__update_task(task_id="uuid", status="review")
```

#### 3. Code Review Workflow
```bash
# 1. Move task to review
# mcp__archon__update_task(task_id="uuid", status="review")

# 2. Create review documentation
# mcp__archon__create_document(
#     project_id="$ARCHON_PROJECT_ID",
#     title="JWT Implementation Review",
#     document_type="note",
#     content={
#         "implementation_summary": "...",
#         "security_review": "...",
#         "test_coverage": "...",
#         "performance_analysis": "..."
#     }
# )

# 3. Mark as completed after review
# mcp__archon__update_task(task_id="uuid", status="done")
```

### Multi-Project Coordination

#### Project Dependencies
```javascript
// Project Alpha (auth-service) creates shared authentication
// Project Beta (ecommerce-web) depends on Project Alpha

// In Project Beta - reference auth service
mcp__archon__create_task({
    project_id: "$ARCHON_PROJECT_ID_B",
    title: "Integrate with authentication service",
    description: "Connect frontend to auth-service API endpoints",
    sources: [
        {
            url: "http://localhost:3001/auth-service/docs",
            type: "api_documentation",
            relevance: "Authentication API endpoints from Project Alpha"
        }
    ],
    assignee: "AI IDE Agent",
    feature: "authentication_integration"
})
```

#### Cross-Project Communication
```bash
# Projects remain isolated but can reference each other's public interfaces
# Document inter-project dependencies

# Project Alpha exposes API documentation
mcp__archon__create_document({
    project_id: "$ARCHON_PROJECT_ID",
    title: "Public API Documentation",
    document_type: "api",
    content: {
        public_endpoints: [...],
        authentication_flow: [...],
        integration_guide: [...]
    },
    tags: ["public", "api", "integration"]
})
```

## 📊 Monitoring & Analytics

### Project-Specific Monitoring
```bash
# Each project maintains independent monitoring
cd /home/ubuntu/dev/auth-service
./bin/health_monitor.sh daemon --profile auth-service

cd /home/ubuntu/dev/ecommerce-web
./bin/health_monitor.sh daemon --profile ecommerce-web

# Separate log files and monitoring data
tail -f health_monitor.log | grep "PROJECT=auth-service"
tail -f health_monitor.log | grep "PROJECT=ecommerce-web"
```

### Performance Tracking
```javascript
// Track project-specific performance metrics
mcp__archon__update_project({
    project_id: "$ARCHON_PROJECT_ID",
    data: {
        performance_metrics: {
            api_response_time: "120ms avg",
            database_query_time: "45ms avg",
            memory_usage: "256MB",
            cpu_utilization: "15%"
        },
        last_updated: new Date().toISOString()
    }
})
```

### Analytics and Reporting
```bash
# Generate project-specific reports
./bin/performance_monitor.sh report --project auth-service
./bin/security_audit.sh compliance --project auth-service --report compliance.json
./bin/run_tests.sh report --project auth-service --format json > test-results.json
```

## 🚀 Advanced Integration Patterns

### Template Integration with Archon
```bash
# Create Archon-aware templates
./bin/template_manager.sh create archon-api-service my-service \
  --archon-integration \
  --auto-create-project \
  --project-title "My Service API" \
  --project-description "RESTful API service with authentication"

# Template automatically:
# 1. Creates Archon project
# 2. Sets ARCHON_PROJECT_ID in .env
# 3. Creates initial task structure
# 4. Sets up project documentation
```

### Automated Task Creation
```bash
# Hook into OOS bootstrap to create standard tasks
# In scripts/bootstrap_enhanced.sh integration:

create_standard_archon_tasks() {
    local project_id="$1"
    local project_type="$2"

    case "$project_type" in
        "api-service")
            # Create API-specific tasks
            ;;
        "web-app")
            # Create web app tasks
            ;;
        "cli-tool")
            # Create CLI tool tasks
            ;;
    esac
}
```

### CI/CD Integration
```yaml
# .github/workflows/archon-integration.yml
name: Archon Integration
on: [push, pull_request]

jobs:
  update-archon:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Update Archon Project
        run: |
          # Update project status in Archon
          # Mark relevant tasks as completed
          # Update project metrics
```

---

This integration guide ensures that OOS and Archon work together seamlessly while maintaining complete project isolation and providing clear operational procedures for multi-project development environments.