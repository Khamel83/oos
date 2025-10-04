# 🤖 AI-First Development Guidelines

## Overview

This document provides specific guidelines for AI systems participating in OOS development. It assumes AI systems are active collaborators with full access to documentation and codebase.

## 🎯 AI Development Role

### Primary Responsibilities
1. **Code Review and Analysis**: Comprehensive codebase understanding and improvement suggestions
2. **Documentation Maintenance**: Keep human+AI documentation synchronized and complete
3. **Testing and Validation**: Ensure all functionality works for both human and AI users
4. **Architecture Evolution**: Suggest improvements based on usage patterns and capabilities

### Decision-Making Authority
- AI can make autonomous decisions for:
  - Code consistency improvements
  - Documentation updates for clarity
  - Test coverage enhancements
  - Performance optimizations
- AI should consult with humans for:
  - Breaking changes to public interfaces
  - Major architectural decisions
  - Changes that affect user workflows
  - Security-related modifications

## 📚 Documentation Standards for AI

### When Creating Documentation

#### 1. Dual-Audience Structure
```markdown
## Feature Name

**For Humans:** [Clear, concise explanation of purpose and value]

**For AI:** [Complete technical specifications in JSON format]
```json
{
  "feature": "feature_name",
  "purpose": "technical_purpose",
  "interface": {
    "inputs": ["param1", "param2"],
    "outputs": "result_type",
    "side_effects": ["effect1", "effect2"]
  },
  "implementation": {
    "dependencies": ["dep1", "dep2"],
    "error_handling": {
      "error_codes": [1, 2, 3],
      "recovery_strategies": ["strategy1", "strategy2"]
    }
  }
}
```

#### 2. Complete Technical Specifications
Always include:
- Input/output schemas
- Error codes and handling procedures
- Performance characteristics
- Dependencies and constraints
- Side effects and implications

#### 3. Decision Context
Explain the "why" behind decisions:
```json
{
  "decision": "chosen_approach",
  "alternatives_considered": ["alt1", "alt2"],
  "reasoning": "detailed_explanation",
  "trade_offs": {
    "pros": ["benefit1", "benefit2"],
    "cons": ["drawback1", "drawback2"]
  },
  "constraints": ["constraint1", "constraint2"]
}
```

### When Updating Documentation

#### 1. Maintain Consistency
- Update both human-readable and machine-readable sections
- Ensure JSON schemas match actual implementation
- Verify all examples work as documented
- Keep terminology consistent across all documentation

#### 2. Version Control
- Document breaking changes clearly
- Provide migration paths for API changes
- Update all related documentation simultaneously
- Tag releases with documentation versions

#### 3. Validation Requirements
Before committing documentation changes:
- [ ] All JSON is valid and parseable
- [ ] All code examples execute successfully
- [ ] Human sections remain clear and understandable
- [ ] AI sections contain complete specifications
- [ ] Cross-references are accurate and up-to-date

## 🔧 Code Development Standards

### Module Development

#### 1. Module Structure
```bash
#!/usr/bin/env bash
# Module: category/module_name
# Purpose: One-line description for humans
# AI Context: Complete technical specification

set -euo pipefail

# AI-specified interface
main() {
    local target="${1:-.}"
    local options="${2:-}"

    # Validation
    if ! validate_inputs "$target" "$options"; then
        return 2
    fi

    # Execution
    if execute_module "$target" "$options"; then
        echo "✅ Module completed: $(basename "$0")" >&2
        return 0
    else
        echo "❌ Module failed: $(basename "$0")" >&2
        return 1
    fi
}

# Implement validation and execution functions
validate_inputs() { ... }
execute_module() { ... }

# Execute if run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
```

#### 2. Error Handling Standards
```bash
# Standard exit codes for AI understanding
EXIT_SUCCESS=0           # Operation completed successfully
EXIT_MODULE_ERROR=1      # Module encountered expected error
EXIT_USAGE_ERROR=2       # Invalid input or usage
EXIT_DEPENDENCY_ERROR=3  # Required tool not found
EXIT_PERMISSION_ERROR=4  # Insufficient permissions
EXIT_NETWORK_ERROR=5     # Network-related failure

# Consistent error reporting
error_exit() {
    local exit_code="$1"
    local error_message="$2"
    echo "❌ $error_message" >&2
    exit "$exit_code"
}
```

#### 3. Output Format Standards
- **Human output**: Send to stderr with clear status indicators
- **Machine output**: Send to stdout in structured format when requested
- **Logging**: Use consistent log levels and formats

### Integration Development

#### 1. Slash Command Implementation
```json
{
  "command": "command_name",
  "implementation": {
    "script": "path/to/script.sh",
    "parameters": [
      {
        "name": "param1",
        "type": "string",
        "required": true,
        "description": "Human-readable description"
      }
    ],
    "behavior": {
      "execution_mode": "synchronous",
      "timeout": 30,
      "retry_logic": {
        "max_attempts": 3,
        "backoff_strategy": "exponential"
      }
    }
  }
}
```

#### 2. Claude Code Integration
- Ensure all slash commands have corresponding working scripts
- Provide clear help text and usage examples
- Handle edge cases gracefully
- Return appropriate exit codes for different scenarios

## 🧪 Testing Standards for AI

### Test Coverage Requirements

#### 1. Unit Tests
- Test individual module functions
- Validate error handling paths
- Verify exit code correctness
- Test with various input combinations

#### 2. Integration Tests
- Test module compositions
- Validate workflow execution
- Test installation and update processes
- Verify slash command functionality

#### 3. Human+AI Tests
- Validate documentation accuracy
- Test human-readability of outputs
- Verify AI can parse all structured data
- Test both audiences can achieve goals

### Test Implementation Standards

#### 1. Test Structure
```bash
#!/usr/bin/env bash
# Test: module_name_test
# Purpose: Validate module_name functionality

set -euo pipefail

# Test fixtures and setup
setup_test_environment() {
    export TEST_MODE=true
    mkdir -p test_workspace
    cd test_workspace
}

# Test cases
test_module_success() {
    # Test successful execution
    ../../modules/category/module_name.sh . >/dev/null 2>&1
    assert_equals $? 0 "Module should succeed with valid inputs"
}

test_module_error_handling() {
    # Test error scenarios
    ../../modules/category/module_name.sh /nonexistent 2>/dev/null
    assert_equals $? 2 "Module should return usage error for invalid inputs"
}

# Test execution
main() {
    setup_test_environment
    test_module_success
    test_module_error_handling
    cleanup_test_environment
}
```

#### 2. Assertion Standards
```bash
# Standard assertions for AI test validation
assert_equals() {
    local expected="$1"
    local actual="$2"
    local message="$3"

    if [[ "$expected" -eq "$actual" ]]; then
        echo "✅ $message" >&2
        return 0
    else
        echo "❌ $message (expected: $expected, actual: $actual)" >&2
        return 1
    fi
}

assert_contains() {
    local haystack="$1"
    local needle="$2"
    local message="$3"

    if [[ "$haystack" == *"$needle"* ]]; then
        echo "✅ $message" >&2
        return 0
    else
        echo "❌ $message: '$needle' not found in '$haystack'" >&2
        return 1
    fi
}
```

## 🔄 Workflow Integration

### Development Workflow for AI

#### 1. Before Making Changes
- Read all relevant documentation
- Understand the human and AI contexts
- Identify potential breaking changes
- Plan validation approach

#### 2. During Development
- Write code that serves both audiences
- Include comprehensive error handling
- Add appropriate logging and output
- Test as you write

#### 3. Before Committing
- Run `/pre-commit` workflow
- Test with fresh installation
- Validate documentation accuracy
- Ensure all examples work

#### 4. After Committing
- Monitor for any issues
- Update documentation if needed
- Learn from feedback and usage patterns
- Suggest improvements

### Continuous Improvement

#### 1. Pattern Recognition
- Identify common issues or questions
- Suggest documentation improvements
- Recommend workflow optimizations
- Propose architectural enhancements

#### 2. Capability Evolution
- Monitor AI capabilities and limitations
- Suggest new features enabled by AI advances
- Update development practices as needed
- Maintain compatibility with human workflows

## 📊 Metrics and Validation

### Success Metrics for AI Development

#### 1. Code Quality
- [ ] All modules follow established patterns
- [ ] Error handling is comprehensive and consistent
- [ ] Documentation is complete and accurate
- [ ] Tests cover all functionality

#### 2. Human+AI Collaboration
- [ ] Humans can understand and use AI contributions
- [ ] AI can comprehend and build upon human work
- [ ] Documentation serves both audiences effectively
- [ ] Development is faster and more reliable

#### 3. System Reliability
- [ ] All functionality works as documented
- [ ] Error handling prevents system failures
- [ ] Updates don't break existing functionality
- [ ] Performance remains acceptable

### Validation Procedures

#### 1. Automated Validation
```bash
# Run comprehensive validation
validate_ai_development() {
    echo "🔍 Validating AI development standards..."

    # Check code quality
    validate_code_standards || return 1

    # Check documentation
    validate_documentation || return 1

    # Check tests
    run_test_suite || return 1

    # Check installation
    test_installation || return 1

    echo "✅ AI development validation passed"
    return 0
}
```

#### 2. Human Review
- Review AI contributions for clarity and usefulness
- Validate that human understanding is maintained
- Ensure changes align with project goals
- Provide feedback for AI improvement

---

**These guidelines enable AI systems to participate effectively in OOS development while maintaining the human+AI partnership ethos. AI systems should reference these guidelines when making development decisions and contributing to the codebase.**