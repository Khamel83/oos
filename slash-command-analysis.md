# 🎯 OOS Slash Command Consolidation Analysis

## Current State: 45 Commands (TOO MANY!)

### Command Categories & Consolidation Opportunities

#### 🚀 **CORE WORKFLOW (Keep - 6 commands)**
- `/start-coding` - Essential entry point
- `/morning` - Daily startup ritual
- `/evening` - Daily completion
- `/do` - Task execution (Archon-powered)
- `/validate` - Quality assurance
- `/smart-commit` - Intelligent commits

#### 🔧 **DEVELOPMENT UTILITIES (Consolidate to 2-3)**
**Current (8):** dev-setup, pre-commit, auto-fix, modules, optimize, test-debug, test-connection, startup-check
**Proposed:**
- `/dev` - All development setup and validation
- `/test` - All testing and debugging
- `/fix` - All code fixes and optimization

#### 📋 **ARCHON INTEGRATION (Keep but simplify - 2-3)**
**Current (4):** archon-research, archon-status, archon-task-start, archon-complete
**Proposed:**
- `/archon` - General Archon interface (research, status)
- `/task` - Task management (start, complete)

#### 🧠 **AI WORKFLOWS (Consolidate to 2-3)**
**Current (7):** agentic-workflow, brain-dump, clarify, help-me, meta-ai, solve, workflow
**Proposed:**
- `/think` - Brain dump, clarify, solve problems
- `/workflow` - Complete structured workflows
- `/help-me` - Keep as is (unique value)

#### 🏗️ **PROJECT MANAGEMENT (Consolidate to 1-2)**
**Current (6):** complete-workflow, create-project, idea-to-done, provision, update-oos, oos-refresh
**Proposed:**
- `/project` - Create, provision, manage projects
- `/update` - System updates and refresh

#### 🔒 **1PASSWORD (Consolidate to 1-2)**
**Current (7):** op-get, op-secret, op-session, op-session-automated, op-setup, op-signin, op-status
**Proposed:**
- `/op` - Main 1Password interface with subcommands
- `/signin` - Quick signin (most used)

#### 🧪 **TESTING & VALIDATION (Consolidate to 1-2)**
**Current (4):** ruat, test-user-scenarios, doc-check, security-review
**Proposed:**
- `/ruat` - Keep as is (core methodology)
- `/check` - All validation (docs, security, etc.)

#### 🛠️ **UTILITIES (Consolidate to 1-2)**
**Current (3):** context-stats, reload-commands, screenshot
**Proposed:**
- `/util` - General utilities
- `/screenshot` - Keep separate (unique)

## 🎯 PROPOSED SIMPLIFIED STRUCTURE (15-20 commands)

### **Tier 1: Essential Daily Commands (6)**
1. `/start-coding` - Development session setup
2. `/morning` - Daily agentic startup
3. `/evening` - Daily completion
4. `/do` - Execute tasks (Archon-powered)
5. `/validate` - Quality assurance
6. `/smart-commit` - Intelligent commits

### **Tier 2: Core Workflow Commands (6-8)**
7. `/dev` - Development environment management
8. `/test` - Testing and debugging
9. `/archon` - Archon research and status
10. `/task` - Task management (start/complete)
11. `/think` - AI-powered problem solving
12. `/project` - Project creation and management
13. `/ruat` - User acceptance testing
14. `/help-me` - Smart context engineering

### **Tier 3: Specialized Commands (3-6)**
15. `/op` - 1Password operations
16. `/signin` - Quick 1Password signin
17. `/screenshot` - Take and analyze screenshots
18. `/update` - System updates
19. `/check` - Comprehensive validation
20. `/fix` - Code fixes and optimization

## 🔥 COMMANDS TO REMOVE/CONSOLIDATE (25+)

### **Merge into `/dev`:**
- dev-setup, startup-check, modules, reload-commands

### **Merge into `/test`:**
- test-debug, test-connection, test-user-scenarios

### **Merge into `/fix`:**
- auto-fix, optimize, doc-check

### **Merge into `/think`:**
- brain-dump, clarify, solve, meta-ai

### **Merge into `/workflow`:**
- agentic-workflow, complete-workflow, idea-to-done

### **Merge into `/project`:**
- create-project, provision, update-oos, oos-refresh

### **Merge into `/op`:**
- op-get, op-secret, op-session, op-session-automated, op-setup, op-status

### **Merge into `/check`:**
- security-review, context-stats

### **Merge into `/archon`:**
- archon-research, archon-status

### **Merge into `/task`:**
- archon-task-start, archon-complete

## 💡 IMPLEMENTATION STRATEGY

### Phase 1: Create Unified Commands
1. Create new consolidated commands with subcommand support
2. Use argument parsing: `/dev setup`, `/dev check`, `/dev modules`
3. Maintain backward compatibility temporarily

### Phase 2: Migration
1. Update documentation to show new consolidated commands
2. Add deprecation warnings to old commands
3. Provide migration guide

### Phase 3: Cleanup
1. Remove deprecated commands
2. Clean up documentation
3. Update Archon integration

## 🎯 BENEFITS OF CONSOLIDATION

1. **Cognitive Load**: 15-20 commands vs 45 (60% reduction)
2. **Discoverability**: Logical grouping makes features findable
3. **Maintainability**: Fewer files to maintain and update
4. **User Experience**: Clear mental model of what each command does
5. **Archon Integration**: Cleaner MCP interface with fewer endpoints

## 🔍 ARCHON MCP ALIGNMENT

The consolidated structure aligns perfectly with Archon MCP capabilities:
- `/archon` and `/task` provide clean MCP interfaces
- `/do` leverages Archon task execution
- `/think` uses Archon knowledge base
- Fewer commands = simpler MCP tool definitions
- Clear separation of concerns for MCP permissions