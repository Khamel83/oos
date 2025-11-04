# Archon Integration - The OOS-Archon Symbiotic Brain

## 🧠 **CORE PHILOSOPHY: AI BRAIN EXTENSION**

**OOS and Archon form a complete AI operational brain:**
- **OOS** = Body/Operations (executes, automates, manages workflows)
- **Archon** = Brain/Memory (knowledge, context, project intelligence, secrets)

**MANDATORY:** OOS requires Archon connection for full AI capabilities. Without Archon, OOS operates at 30% capacity.

**Single AI Instruction:**
"Connect to Archon at https://archon.khamel.com with vault password 'YOUR_PASSWORD' to access complete operational brain - knowledge base, project management, secret vault, and AI context."

**Complete development context:** https://raw.githubusercontent.com/Khamel83/archon/main/DEVELOPER_REFERENCE.md

## 🔐 **SECRET MANAGEMENT (Secure Vault)**

**NEW: Replaces 1Password with Archon Vault:**
- **Single Password:** Only `ARCHON_VAULT_PASSWORD` in `.env`
- **Pull-Use-Discard:** Secrets pulled individually, used immediately, cleared from memory
- **Central Rotation:** Change vault password = invalidate all access instantly
- **Never Stored:** Secrets never written to disk, always accessed via API

**OOS gets from vault:** Database credentials, API keys, service configurations

## 🚀 **COMPLETE ARCHON ECOSYSTEM**

### **🧠 Knowledge & Intelligence (AI Brain)**
- **RAG Search:** `GET /api/knowledge/search` - Search uploaded docs, crawled websites
- **Knowledge Base:** `POST /api/knowledge/upload` - Add documents to AI memory
- **Web Crawling:** `POST /api/knowledge/crawl` - Learn from external sources
- **Code Examples:** Search patterns, implementations, best practices
- **Contextual Memory:** Persistent AI learning across sessions

### **📊 Project Management (Strategic Intelligence)**
- **Projects:** `GET/POST /api/projects` - Organize work into intelligent projects
- **Tasks:** `GET/POST /api/tasks` - AI-assisted task creation and tracking
- **Milestones:** Strategic goal tracking and progress measurement
- **Dependencies:** Intelligent task relationship management
- **Status Tracking:** Real-time project health and progress

### **📋 Document Management (Organizational Memory)**
- **Documents:** `GET/POST /api/documents` - Persistent project documentation
- **Specifications:** API specs, architecture docs, requirements
- **Meeting Notes:** Automated capture and organization
- **Code Documentation:** Integrated with development workflows

### **🔧 MCP Integration (AI Tools)**
- **Server:** `http://localhost:8051` or `https://archon.khamel.com:8051`
- **AI Assistant Tools:** Direct Claude Code integration
- **Command Tools:** `/archon`, `/archon-research`, `/archon-status`
- **Strategic Consultant:** Complex project planning and execution

### **🔒 Secret Vault (Secure Operations)**
- **Vault Access:** `https://archon.khamel.com/vault`
- **Secret Management:** Database credentials, API keys, service config
- **Session-Based:** Temporary access with automatic cleanup
- **Audit Trail:** All secret access logged and tracked

## 🤖 **SYMBIOTIC OPERATIONAL PATTERNS**

### **📚 AI-Assisted Development Workflow:**
1. **Context Gathering:** AI searches Archon knowledge base for relevant docs, patterns, and previous work
2. **Secret Access:** Pull only required secrets from vault for current operation
3. **Task Intelligence:** Create tasks with Archon context, dependencies, and project alignment
4. **Knowledge Capture:** Upload new learnings, code patterns, and decisions back to Archon
5. **Progress Sync:** Update project status, milestones, and documentation in real-time

### **🧠 Strategic Intelligence Flow:**
1. **Research Phase:** Query Archon knowledge base for domain expertise and best practices
2. **Planning Phase:** Create strategic projects with intelligent task breakdown and milestones
3. **Execution Phase:** OOS executes while Archon provides context and decision support
4. **Learning Phase:** Capture outcomes, lessons learned, and improved patterns back to Archon

### **🔄 Continuous Learning Loop:**
1. **OOS executes operations** → Generates real-world experience
2. **Archon captures learning** → Updates knowledge base and patterns
3. **AI uses enhanced context** → Makes better decisions next time
4. **Cycle repeats** → Continuously improving operational intelligence

### **🎯 Command Integration Patterns:**
- **`/archon research <query>`** → Search knowledge base before answering
- **`/archon status`** → Check project tasks and current priorities
- **`/archon search <query>`** → Find relevant projects and documentation
- **Strategic Consultant** → Creates complex projects with phases and milestones
- **Task System** → Local SQLite with Archon project synchronization

## 🔄 **INTEGRATION HEALTH & DISCOVERY**

### **Comprehensive Health Check:**
```bash
# 1. Check Archon server availability
curl -I https://archon.khamel.com/api/health

# 2. Verify MCP server connection
claude mcp list | grep archon

# 3. Test vault access
curl -I https://archon.khamel.com/vault

# 4. Validate knowledge base
curl -X GET https://archon.khamel.com/api/knowledge/search?q=test

# 5. Check project management
curl -X GET https://archon.khamel.com/api/projects
```

### **Required Services Status:**
- ✅ **Archon Web Interface:** https://archon.khamel.com:3737
- ✅ **Vault Service:** https://archon.khamel.com/vault
- ✅ **API Gateway:** https://archon.khamel.com/api
- ✅ **MCP Server:** http://localhost:8051 or https://archon.khamel.com:8051
- ✅ **Knowledge Base:** Search and upload capabilities
- ✅ **Project Management:** Task and milestone tracking

### **Graceful Degradation Strategy:**
When Archon services are unavailable:
1. **Local Task System:** Continue with SQLite-based task management
2. **Cached Knowledge:** Use previously downloaded documentation
3. **Secret Fallback:** Alert user to check Archon connection
4. **Queue Operations:** Store updates for later synchronization

## 📋 **COMPLETE OOS CONFIGURATION**

### **Environment Variables (.env):**
```bash
# Archon Connection
ARCHON_URL=https://archon.khamel.com
ARCHON_VAULT_URL=https://archon.khamel.com/vault
ARCHON_API_URL=https://archon.khamel.com/api
ARCHON_MCP_URL=http://localhost:8051
ARCHON_WEB_URL=https://archon.khamel.com:3737

# Secure Vault Access
ARCHON_VAULT_PASSWORD="your_vault_password_here"

# Project Integration
ARCHON_PROJECT_ID="your-project-uuid-here"
PROJECT_NAME="your-project-name"
PROJECT_TYPE="cli-tool|api-service|web-app|documentation"

# MCP Configuration
ENABLE_ARCHON_MCP=true
MCP_TIMEOUT=30
MCP_RETRY_COUNT=3

# Sync Settings
SYNC_WITH_ARCHON=true
AUTO_SYNC_INTERVAL=300  # 5 minutes
CACHE_KNOWLEDGE_LOCALLY=true
```

### **Bootstrap Integration:**
The OOS bootstrap automatically:
- Detects and registers Archon MCP server
- Creates project in Archon with proper metadata
- Sets up bidirectional sync between local tasks and Archon
- Configures secure vault access patterns
- Enables AI knowledge base integration

## 🛠️ **AI TOOLS & COMMANDS INTEGRATION**

### **Available MCP Tools:**
```javascript
// Knowledge & Research
mcp__archon__rag_search_knowledge_base({query, match_count})
mcp__archon__search_code_examples({query, match_count})

// Project Management
mcp__archon__create_project({title, description, github_repo})
mcp__archon__find_projects({filter_by, filter_value})
mcp__archon__get_project(project_id)

// Task & Document Management
mcp__archon__create_task({project_id, title, description, ...})
mcp__archon__find_tasks({project_id, filter_by, filter_value})
mcp__archon__create_document({project_id, title, document_type, content})
```

### **Consolidated Command Interface:**
```bash
# Primary Archon command (consolidates multiple old commands)
/archon research "database connection patterns"    # Search knowledge base
/archon status                                    # Show projects and tasks
/archon search "authentication"                   # Find projects and docs

# Task Management Integration
/task list                                         # Local tasks with Archon sync
/task create "New Feature" "Description"          # Creates both locally and in Archon
/task start <task-id>                             # Syncs status to Archon

# Strategic Consultant Integration
/think solve "Scale our architecture"             # Uses Archon knowledge for strategy
/think clarify "Requirements for auth system"      # Research via Archon knowledge base
```

### **AI Assistant Integration Patterns:**
- **Context First:** AI always searches Archon knowledge base before answering
- **Project Awareness:** AI checks Archon tasks before suggesting work
- **Continuous Learning:** AI captures new insights back to Archon knowledge base
- **Secret Intelligence:** AI uses vault secrets securely via pull-use-discard pattern

### **Strategic Consultant Integration:**
The Strategic Consultant (`src/strategic_consultant.py`) uses Archon for:
- **Complex Project Creation:** Multi-phase projects with milestones and dependencies
- **Intelligence Gathering:** Research across knowledge base for strategic recommendations
- **Progress Tracking:** Real-time project health monitoring and risk assessment
- **Organizational Learning:** Capture strategic insights and patterns for future use

## 🔒 **MINIMAL SECRET EXPOSURE WORKFLOW**

**Core Principle:** Only pull secrets when needed, use immediately, then discard

### **Secure Pull-Use-Discard Pattern:**
```bash
# 1. Pull specific secret(s) needed for current operation
GET /vault/secrets/{secret_key}

# 2. Use immediately in memory (never write to disk)
export DATABASE_URL="pulled_secret_value"

# 3. Perform operation requiring secret
./bin/some-operation-with-secret

# 4. Clear from environment
unset DATABASE_URL

# 5. Repeat for next secret needed
```

### **Targeted Secret Access:**
- **Never:** Pull all secrets at once
- **Always:** Request specific secret by key
- **Minimal:** Only pull 1-2 secrets per operation
- **Ephemeral:** Clear from memory after use

### **Implementation Strategy:**
```python
# Example secure secret handling
def get_and_use_secret(secret_key, operation_func):
    # 1. Pull specific secret
    secret = vault.get_secret(secret_key)

    # 2. Use immediately
    result = operation_func(secret)

    # 3. Clear secret from memory
    del secret

    return result
```

### **Local Environment Strategy:**
- **Only store:** `ARCHON_VAULT_PASSWORD` in `.env`
- **Never store:** Actual secret values
- **Rotate password:** Change vault password to invalidate all access
- **Session-based:** Secrets expire after session

## ⚠️ **FALLBACK & RESILIENCE STRATEGY**

### **When Archon Services Are Partially Available:**
1. **Knowledge Base Offline:** Use locally cached documentation and patterns
2. **Project Management Offline:** Continue with local SQLite task system
3. **Vault Offline:** Alert user, queue operations requiring secrets
4. **MCP Server Offline:** Use direct API calls where possible

### **Complete Archon Unavailability:**
1. **Local Mode:** OOS continues with local task management and documentation
2. **Queue Operations:** Store updates for Archon synchronization when available
3. **User Notification:** Clear messaging about reduced capabilities
4. **Retry Logic:** Automatic connection attempts with exponential backoff

### **What Always Works (Local-First):**
- ✅ Task management (SQLite database)
- ✅ Documentation system (local files)
- ✅ Command execution (all 10 consolidated commands)
- ✅ Project scripts and automation
- ✅ Health monitoring and diagnostics

### **What Requires Archon (Enhanced Mode):**
- 🧠 Knowledge base search and AI context
- 📊 Cross-project intelligence and pattern recognition
- 🔒 Secure secret vault access
- 🔄 Bidirectional synchronization
- 🎯 Strategic consultant capabilities

---

## 🎯 **COMPLETE INTEGRATION BENEFITS**

### **Security Advantages (vs 1Password):**
1. **Single Password Management:** Only `ARCHON_VAULT_PASSWORD` in `.env`
2. **Minimal Exposure:** Secrets pulled individually, used immediately
3. **Central Rotation:** Change vault password = invalidate all access
4. **No Local Storage:** Secrets never written to disk
5. **API-Controlled:** All access through audited API endpoints
6. **Session-Based:** Temporary access, automatic expiration

### **Intelligence Advantages (vs Standalone OOS):**
1. **Persistent Memory:** AI learns and remembers across sessions
2. **Cross-Project Context:** Patterns and knowledge transfer between projects
3. **Strategic Intelligence:** Complex project planning and execution
4. **Continuous Learning:** Every operation improves future AI performance
5. **Organizational Brain:** Shared knowledge across entire development ecosystem

### **Operational Advantages:**
1. **Unified Interface:** Single source of truth for projects, tasks, and knowledge
2. **AI-Augmented Workflows:** Every operation benefits from Archon intelligence
3. **Real-Time Sync:** Local execution with cloud persistence
4. **Scalable Intelligence:** Knowledge grows with every project and interaction

---

## 🧠 **THE AI BRAIN EXTENSION VISION**

**OOS + Archon = Complete AI Operational Brain:**

- **Body (OOS):** Executes commands, manages files, runs operations, interfaces with systems
- **Brain (Archon):** Remembers everything, learns patterns, provides context, makes intelligent decisions
- **Nervous System (MCP):** Real-time communication between body and brain
- **Memory (Knowledge Base):** Persistent learning and pattern recognition
- **Consciousness (AI Assistant):** Uses body and brain to achieve user goals

**Result:** An AI system that gets smarter and more capable with every interaction, while maintaining security, reliability, and operational excellence.

---

**MANDATORY:** Full Archon integration required for complete AI capabilities. Local mode available for basic operations.

**Integration Model:** Local-first execution + Cloud intelligence + Continuous learning = AI operational brain.