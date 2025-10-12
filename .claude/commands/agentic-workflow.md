---
argument-hint: <arguments>
model: claude-3-5-sonnet-20241022
---

# /agentic-workflow

Complete idea-to-execution pipeline with OOS systematic workflows + Archon knowledge integration.

Takes any idea through a systematic gauntlet: Research → Plan → Build → Validate → Deploy

## Usage

```bash
./bin/agentic-workflow-orchestrator.sh "$ARGUMENTS"
```

## Arguments

- `idea` - Your project idea (optional, will prompt if not provided)
- `mode` - Execution mode: `interactive` (default), `auto`, or `help`

## Examples

```bash
/agentic-workflow "Build a task management app"
/agentic-workflow "Create a Python CLI tool" interactive
/agentic-workflow "" auto  # Will prompt for idea
```

## Workflow Stages

1. **Idea Analysis & Knowledge Gathering**
   - Archon research for similar patterns
   - OOS brain-dump and clarification
   - Context gathering from knowledge base

2. **Systematic Planning with Archon Context**
   - Research planning methodologies
   - Create structured task breakdown
   - Archive learnings for future reference

3. **Development Environment & Setup**
   - Research tooling best practices
   - OOS start-coding and dev-gate validation
   - Environment consistency checks

4. **Systematic Development with Knowledge**
   - Implementation guided by Archon knowledge
   - Continuous OOS validation
   - Progress tracking in structured tasks

5. **Comprehensive Validation**
   - RUAT (Recursive User-Acceptance Testing)
   - OOS validation gauntlet
   - Pre-commit quality checks

6. **Documentation & Completion**
   - Documentation completeness verification
   - Smart commit generation
   - Learning capture back to Archon

## Integration Points

**OOS Commands Used:**
- `/brain-dump` - Process ideas systematically
- `/clarify` - Clarification workflow
- `/start-coding` - Development environment setup
- `/ruat` - User acceptance testing
- `/validate` - Comprehensive validation
- `/pre-commit` - Quality assurance
- `/smart-commit` - Intelligent commits

**Archon Integration:**
- Knowledge research at each stage
- Task management and progress tracking
- Learning accumulation and pattern recognition
- Context-aware decision making

## State Management

Workflow state is saved to `.oos/agentic-workflow-state.json` for:
- Progress tracking
- Resume capability
- Learning analysis
- Process optimization

This is the **complete systematic approach** that takes your vision and executes it through the full OOS+Archon ecosystem.