# 🤖 Agent Operating Instructions

## How Agents Should Work Here

This project follows Agent-OS patterns with OOS enhancements. Agents should read and follow these specifications.

### Input/Output Formats

**Task Creation**:
```markdown
## Task: [Title]
**Assignee**: User|Archon|AI IDE Agent|prp-executor|prp-validator
**Priority**: 1-100
**Status**: todo|doing|review|done

### Description
[Detailed description with acceptance criteria]

### Sources
- [Documentation links or file paths]
- [API specifications]
- [Related examples]

### Code Examples
- `file:function` - Purpose description
```

**Progress Updates**:
```markdown
## Status Update: [Task Title]
**Status**: [Current status]
**Progress**: [What was completed]
**Next Steps**: [What comes next]
**Blockers**: [Any issues encountered]
```

### Agent Integration Points

1. **Archon MCP**: Use for task management and knowledge queries
2. **OOS Learning**: Capture lessons in both Archon and local specs
3. **SQLite SoT**: All persistent data goes through single source of truth
4. **Approval Workflow**: Critical changes require human approval via Google Sheets

### Guardrails and Safety Rules

1. **Database Safety**:
   - Never modify SQLite directly without backup
   - Use approved schema migration patterns
   - Always validate data before writes

2. **Human Loop Integration**:
   - Submit changes requiring approval to Google Sheets
   - Wait for approval before proceeding with critical operations
   - Provide clear context in approval requests

3. **Code Safety**:
   - Follow existing project patterns and conventions
   - Run tests before marking tasks complete
   - Use established tooling (lints, formatters)

4. **Learning Integration**:
   - Document lessons learned in `~/.agent-os/LEARNING_PATTERNS.md`
   - Reference past solutions before implementing new ones
   - Update project specs when patterns emerge

### Communication Protocols

**With Humans**:
- Use clear, concise status updates
- Provide context and reasoning for decisions
- Ask specific questions when stuck

**With Other Agents**:
- Share context through Archon knowledge base
- Use standardized task formats
- Coordinate through shared project specs

**With Systems**:
- Log all operations for audit trail
- Use structured data formats (JSON, markdown)
- Follow database transaction patterns

### Error Handling

1. **Graceful Degradation**:
   - Continue with available information when possible
   - Document what couldn't be completed and why
   - Provide clear steps for human intervention

2. **Recovery Procedures**:
   - Use backup data when primary source fails
   - Switch to manual approval when automation fails
   - Fall back to read-only mode during maintenance

3. **Escalation Paths**:
   - Auto-escalate after N failed attempts
   - Notify humans of persistent issues
   - Document resolution steps for future reference

### Project-Specific Context

**Technology Stack**: [To be filled by project]
**Development Patterns**: [To be filled by project]
**Testing Requirements**: [To be filled by project]
**Deployment Process**: [To be filled by project]

### Success Metrics

- Tasks completed without human intervention: >80%
- Tasks requiring clarification: <20%
- Critical errors requiring rollback: <5%
- Human approval response time: <4 hours
- Agent learning retention: >90% of documented patterns followed

---

*This file should be customized for each project while maintaining the core Agent-OS compatibility.*