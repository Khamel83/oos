# User Testing Framework (RUAT)

## Overview

Recursive User-Acceptance Testing (RUAT) ensures every OOS feature works from a real user perspective, not just technically. This mandatory framework prevents shipping features that are technically correct but provide poor user experiences.

## Philosophy

**Technical correctness ≠ User success**

A feature can:
- ✅ Pass all unit tests
- ✅ Have perfect documentation
- ✅ Integrate properly with other systems
- ❌ **Still be terrible for users**

RUAT catches this gap by validating features through realistic user scenarios.

## When to Use RUAT

### Mandatory Usage Points

1. **Before marking Archon tasks "done"**
2. **Before any commit that adds/changes user-facing features**
3. **As part of comprehensive validation (`./bin/validate-oos`)**
4. **When onboarding new features to OOS**

### Task Completion Flow

```
Standard Flow (WRONG):
todo → doing → review → done

RUAT Flow (CORRECT):
todo → doing → technical-complete → ruat-validation → review → done
```

## Running RUAT

### Test Single Feature

```bash
# Test specific feature scenarios
./bin/test-user-scenarios start-coding
./bin/test-user-scenarios help-me
./bin/test-user-scenarios screenshot
```

### Test All Features

```bash
# Run all user scenarios
./bin/test-user-scenarios --all
```

### Create New Scenarios

```bash
# Generate scenario template for new feature
./bin/test-user-scenarios --create new-feature-name
```

## Scenario Format

### File Structure

```
tests/scenarios/
├── start-coding.scenarios
├── help-me.scenarios
├── screenshot.scenarios
├── provision.scenarios
└── [feature-name].scenarios
```

### Scenario Syntax

```bash
# Comment describing the scenario
GIVEN [initial state/context]
WHEN [user action]
THEN [expected outcome]
AND [additional validation]
AND [more validation as needed]

# Next scenario
GIVEN [different context]
WHEN [different action]
THEN [different outcome]
```

### Example Scenario

```bash
# New user tries to get help
GIVEN user is new to OOS and encounters error
WHEN user runs /help-me with error message
THEN formatted prompt is generated for Claude Code
AND prompt contains actual error text
AND output is ready to copy-paste
AND user immediately knows what to do next
```

## Validation Process

### Interactive Testing

RUAT uses interactive validation because user experience is subjective:

1. **GIVEN/WHEN steps**: Set up scenario context
2. **THEN/AND steps**: Human validates if expectation matches reality
3. **Pass/Fail/Skip**: User decides if scenario passes
4. **Failure logging**: Failed scenarios are documented for fixing

### Example Session

```
🧪 Testing User Scenarios: help-me
==================================

📋 Scenario: Error troubleshooting scenario
----------------------------------------

Step 1:
GIVEN: user encounters error in terminal

Step 2:
WHEN: user copies error and runs /help-me
💡 Try running the actual command now and observe the behavior
   Suggested: /help-me
   Press ENTER when you've tested this step...

Step 3:
THEN: formatted prompt is generated for Claude Code
Did this expectation match reality? (y/n/skip)
Expected: formatted prompt is generated for Claude Code
> y
  ✅ Validated

✅ SCENARIO PASSED: Error troubleshooting scenario
```

## Creating Effective Scenarios

### Focus Areas

1. **Discovery**: Can users find the feature?
2. **Understanding**: Do users know how to use it?
3. **Success Path**: Does the common use case work perfectly?
4. **Edge Cases**: Are unusual situations handled gracefully?
5. **Error Handling**: Are error messages helpful and actionable?
6. **Integration**: Does feature work naturally with other tools?

### Scenario Categories

#### Discovery Scenarios
```bash
GIVEN user doesn't know [feature] exists
WHEN user looks for solution to [problem]
THEN feature is discoverable in documentation
AND clearly explains how it solves [problem]
```

#### First-Time User Scenarios
```bash
GIVEN user has never used [feature] before
WHEN user runs [feature] for first time
THEN experience is intuitive and self-explanatory
AND user immediately understands value
```

#### Error Handling Scenarios
```bash
GIVEN user makes common mistake with [feature]
WHEN error occurs
THEN error message is helpful and actionable
AND user knows exactly how to fix it
```

#### Integration Scenarios
```bash
GIVEN user is in normal development workflow
WHEN user runs [feature]
THEN feature integrates seamlessly
AND doesn't disrupt existing tools
```

## RUAT Failure Handling

### When Scenarios Fail

1. **Document the Issue**: Failure is logged to `ruat_failures.log`
2. **Create Fix Task**: New Archon task to address UX problem
3. **Block Completion**: Original task stays "technical-complete"
4. **Fix Experience**: Address root cause of poor UX
5. **Re-test**: Run RUAT again until scenarios pass

### Example Failure Log Entry

```
2025-10-10 20:30: FEATURE=help-me EXPECTED='formatted prompt is generated' ACTUAL='command crashed with unclear error'
```

## Integration with OOS Workflows

### /start-coding Integration

```bash
# Before marking work complete, /start-coding runs:
./bin/test-user-scenarios [feature-being-developed]
```

### Validation Framework Integration

```bash
# RUAT is part of comprehensive validation:
./bin/validate-oos
```

The validation framework checks:
- ✅ RUAT script exists and is executable
- ✅ Scenario files exist for features
- ✅ Scenario files have valid format
- ✅ Framework is ready for use

### Pre-commit Integration

Critical features are validated before commit:

```bash
# Pre-commit hook runs RUAT for changed features
./bin/test-user-scenarios [modified-feature]
```

## Best Practices

### Writing Scenarios

1. **Be Specific**: Vague scenarios lead to meaningless validation
2. **Think Like Users**: What would real users actually do?
3. **Include Edge Cases**: Users hit edge cases constantly
4. **Test Integration**: Features don't exist in isolation
5. **Validate Discoverability**: Can users find the feature?

### Running RUAT

1. **Run Often**: Don't let scenarios get stale
2. **Be Honest**: If UX is bad, mark scenarios as failed
3. **Fix Issues**: Don't ignore failed scenarios
4. **Update Scenarios**: Keep them current with feature changes
5. **Create Missing Scenarios**: Every feature needs scenarios

### Maintaining Scenarios

1. **Review Regularly**: Ensure scenarios match current features
2. **Add New Scenarios**: Based on user feedback and bug reports
3. **Remove Obsolete Scenarios**: When features are removed
4. **Improve Clarity**: Make scenarios easier to understand and execute

## Meta-Testing: RUAT Tests RUAT

The RUAT framework itself must pass user scenarios:

```bash
# Test the testing framework
./bin/test-user-scenarios test-user-scenarios
```

Scenarios include:
- Creating new scenario files
- Running scenarios interactively
- Handling failed validations
- Integrating with OOS workflows

## Success Metrics

### Project Level
- All features have scenario files
- RUAT runs cleanly without errors
- Failed scenarios are addressed promptly
- UX issues decrease over time

### Feature Level
- All scenarios pass for each feature
- New scenarios added for new use cases
- Edge cases documented and handled
- User feedback becomes test scenarios

### Team Level
- RUAT is run before marking tasks done
- UX issues caught before shipping
- Features work for real users, not just tests
- Continuous improvement based on real usage

## Troubleshooting

### "No scenarios found"
```bash
# Create scenarios for your feature
./bin/test-user-scenarios --create [feature-name]
```

### "Invalid scenario format"
Check that scenario file includes GIVEN/WHEN/THEN/AND statements.

### "RUAT takes too long"
RUAT is intentionally interactive. Quality UX validation takes time.

### "Scenarios keep failing"
That's the point! Fix the UX issues, don't ignore the scenarios.

## Example: Complete RUAT Workflow

1. **Develop Feature**: Implement new /example-command
2. **Create Scenarios**: `./bin/test-user-scenarios --create example-command`
3. **Edit Scenarios**: Add realistic user workflows to scenario file
4. **Run RUAT**: `./bin/test-user-scenarios example-command`
5. **Fix Issues**: Address any failed scenarios
6. **Re-test**: Run RUAT until all scenarios pass
7. **Mark Complete**: Move Archon task from "technical-complete" to "review"
8. **Continuous**: Add new scenarios based on user feedback

## Conclusion

RUAT ensures OOS features work the way users actually use them, not just how we think they should work. This mandatory validation prevents the "technically correct but terrible UX" problem that plagues many development tools.

By validating from the user perspective, OOS maintains its commitment to being a truly systematic thinking environment that enhances rather than hinders developer workflows.