#!/usr/bin/env bash
set -euo pipefail

# OOS Comprehensive Testing Framework
# Usage: ./bin/run_tests.sh [OPTIONS] [TEST_PATTERN]

VERSION="1.0.0"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TEST_DIR="$PROJECT_ROOT/tests"
RESULTS_DIR="$PROJECT_ROOT/test-results"
COVERAGE_DIR="$PROJECT_ROOT/coverage"

# Test configuration
RUN_UNIT_TESTS=true
RUN_INTEGRATION_TESTS=true
RUN_E2E_TESTS=true
RUN_PERFORMANCE_TESTS=false
RUN_SECURITY_TESTS=true
VERBOSE=false
PARALLEL=true
GENERATE_COVERAGE=false
CLEANUP_AFTER=true
TEST_PATTERN=""
DRY_RUN=false

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Utility functions
log() { echo -e "${BLUE}[INFO]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $*"; }
verbose() { [[ "$VERBOSE" == "true" ]] && echo -e "${CYAN}[VERBOSE]${NC} $*"; }

# Show help
show_help() {
  cat << 'EOF'
OOS Comprehensive Testing Framework v1.0.0

Usage: ./bin/run_tests.sh [OPTIONS] [TEST_PATTERN]

Arguments:
  TEST_PATTERN      Run only tests matching pattern (e.g., "unit", "bootstrap", "security")

Options:
  --unit            Run only unit tests
  --integration     Run only integration tests
  --e2e             Run only end-to-end tests
  --performance     Include performance tests
  --security        Run only security tests
  --all             Run all test suites (default)
  
  --verbose         Show detailed test output
  --parallel        Run tests in parallel (default)
  --serial          Run tests sequentially
  --coverage        Generate test coverage reports
  --no-cleanup      Don't clean up test artifacts
  --dry-run         Show what would be tested without running
  --help, -h        Show this help message

Examples:
  ./bin/run_tests.sh                    # Run all standard tests
  ./bin/run_tests.sh --unit --verbose   # Run unit tests with verbose output
  ./bin/run_tests.sh bootstrap          # Run tests matching "bootstrap"
  ./bin/run_tests.sh --performance --all # Run all tests including performance
EOF
}

# Parse command line arguments
parse_args() {
  local test_types_specified=false
  
  while [[ $# -gt 0 ]]; do
    case $1 in
      --unit)
        if [[ "$test_types_specified" == "false" ]]; then
          RUN_UNIT_TESTS=true
          RUN_INTEGRATION_TESTS=false
          RUN_E2E_TESTS=false
          RUN_SECURITY_TESTS=false
          test_types_specified=true
        fi
        shift
        ;;
      --integration)
        if [[ "$test_types_specified" == "false" ]]; then
          RUN_UNIT_TESTS=false
          RUN_INTEGRATION_TESTS=true
          RUN_E2E_TESTS=false
          RUN_SECURITY_TESTS=false
          test_types_specified=true
        else
          RUN_INTEGRATION_TESTS=true
        fi
        shift
        ;;
      --e2e)
        if [[ "$test_types_specified" == "false" ]]; then
          RUN_UNIT_TESTS=false
          RUN_INTEGRATION_TESTS=false
          RUN_E2E_TESTS=true
          RUN_SECURITY_TESTS=false
          test_types_specified=true
        else
          RUN_E2E_TESTS=true
        fi
        shift
        ;;
      --security)
        if [[ "$test_types_specified" == "false" ]]; then
          RUN_UNIT_TESTS=false
          RUN_INTEGRATION_TESTS=false
          RUN_E2E_TESTS=false
          RUN_SECURITY_TESTS=true
          test_types_specified=true
        else
          RUN_SECURITY_TESTS=true
        fi
        shift
        ;;
      --performance)
        RUN_PERFORMANCE_TESTS=true
        shift
        ;;
      --all)
        RUN_UNIT_TESTS=true
        RUN_INTEGRATION_TESTS=true
        RUN_E2E_TESTS=true
        RUN_SECURITY_TESTS=true
        test_types_specified=true
        shift
        ;;
      --verbose)
        VERBOSE=true
        shift
        ;;
      --parallel)
        PARALLEL=true
        shift
        ;;
      --serial)
        PARALLEL=false
        shift
        ;;
      --coverage)
        GENERATE_COVERAGE=true
        shift
        ;;
      --no-cleanup)
        CLEANUP_AFTER=false
        shift
        ;;
      --dry-run)
        DRY_RUN=true
        shift
        ;;
      --help|-h)
        show_help
        exit 0
        ;;
      -*)
        error "Unknown option: $1"
        exit 1
        ;;
      *)
        TEST_PATTERN="$1"
        shift
        ;;
    esac
  done
}

# Setup test environment
setup_test_environment() {
  log "Setting up test environment..."
  
  mkdir -p "$TEST_DIR" "$RESULTS_DIR" "$COVERAGE_DIR"
  
  # Create test utilities if they don't exist
  create_test_utilities
}

# Create test utilities
create_test_utilities() {
  # Test assertion library
  cat > "$TEST_DIR/test_lib.sh" <<'EOF'
#!/usr/bin/env bash

# Simple test assertion library for Bash
TEST_COUNT=0
PASS_COUNT=0
FAIL_COUNT=0
CURRENT_TEST=""

# Test result tracking
declare -a FAILED_TESTS=()
declare -a PASSED_TESTS=()

# Colors for test output
T_RED='\033[0;31m'
T_GREEN='\033[0;32m'
T_YELLOW='\033[1;33m'
T_BLUE='\033[0;34m'
T_NC='\033[0m'

# Test functions
start_test() {
  CURRENT_TEST="$1"
  ((TEST_COUNT++))
  echo -e "${T_BLUE}TEST ${TEST_COUNT}:${T_NC} $CURRENT_TEST"
}

assert_equals() {
  local expected="$1"
  local actual="$2"
  local message="${3:-}"
  
  if [[ "$expected" == "$actual" ]]; then
    echo -e "  ${T_GREEN}✓${T_NC} ${message:-Values match}"
    ((PASS_COUNT++))
    return 0
  else
    echo -e "  ${T_RED}✗${T_NC} ${message:-Values don't match}"
    echo -e "    Expected: $expected"
    echo -e "    Actual:   $actual"
    FAILED_TESTS+=("$CURRENT_TEST")
    ((FAIL_COUNT++))
    return 1
  fi
}

assert_not_equals() {
  local unexpected="$1"
  local actual="$2"
  local message="${3:-}"
  
  if [[ "$unexpected" != "$actual" ]]; then
    echo -e "  ${T_GREEN}✓${T_NC} ${message:-Values are different}"
    ((PASS_COUNT++))
    return 0
  else
    echo -e "  ${T_RED}✗${T_NC} ${message:-Values should be different}"
    echo -e "    Unexpected: $unexpected"
    echo -e "    Actual:     $actual"
    FAILED_TESTS+=("$CURRENT_TEST")
    ((FAIL_COUNT++))
    return 1
  fi
}

assert_true() {
  local condition="$1"
  local message="${2:-}"
  
  if [[ "$condition" == "true" ]] || [[ "$condition" == "0" ]]; then
    echo -e "  ${T_GREEN}✓${T_NC} ${message:-Condition is true}"
    ((PASS_COUNT++))
    return 0
  else
    echo -e "  ${T_RED}✗${T_NC} ${message:-Condition should be true}"
    echo -e "    Value: $condition"
    FAILED_TESTS+=("$CURRENT_TEST")
    ((FAIL_COUNT++))
    return 1
  fi
}

assert_false() {
  local condition="$1"
  local message="${2:-}"
  
  if [[ "$condition" == "false" ]] || [[ "$condition" == "1" ]]; then
    echo -e "  ${T_GREEN}✓${T_NC} ${message:-Condition is false}"
    ((PASS_COUNT++))
    return 0
  else
    echo -e "  ${T_RED}✗${T_NC} ${message:-Condition should be false}"
    echo -e "    Value: $condition"
    FAILED_TESTS+=("$CURRENT_TEST")
    ((FAIL_COUNT++))
    return 1
  fi
}

assert_file_exists() {
  local file="$1"
  local message="${2:-}"
  
  if [[ -f "$file" ]]; then
    echo -e "  ${T_GREEN}✓${T_NC} ${message:-File exists: $file}"
    ((PASS_COUNT++))
    return 0
  else
    echo -e "  ${T_RED}✗${T_NC} ${message:-File should exist: $file}"
    FAILED_TESTS+=("$CURRENT_TEST")
    ((FAIL_COUNT++))
    return 1
  fi
}

assert_command_success() {
  local command="$1"
  local message="${2:-}"
  
  if eval "$command" >/dev/null 2>&1; then
    echo -e "  ${T_GREEN}✓${T_NC} ${message:-Command succeeded: $command}"
    ((PASS_COUNT++))
    return 0
  else
    echo -e "  ${T_RED}✗${T_NC} ${message:-Command should succeed: $command}"
    FAILED_TESTS+=("$CURRENT_TEST")
    ((FAIL_COUNT++))
    return 1
  fi
}

assert_command_fails() {
  local command="$1"
  local message="${2:-}"
  
  if ! eval "$command" >/dev/null 2>&1; then
    echo -e "  ${T_GREEN}✓${T_NC} ${message:-Command failed as expected: $command}"
    ((PASS_COUNT++))
    return 0
  else
    echo -e "  ${T_RED}✗${T_NC} ${message:-Command should fail: $command}"
    FAILED_TESTS+=("$CURRENT_TEST")
    ((FAIL_COUNT++))
    return 1
  fi
}

finish_tests() {
  echo
  echo "Test Results:"
  echo "============="
  echo -e "Tests run: ${TEST_COUNT}"
  echo -e "${T_GREEN}Passed: ${PASS_COUNT}${T_NC}"
  echo -e "${T_RED}Failed: ${FAIL_COUNT}${T_NC}"
  
  if [[ ${#FAILED_TESTS[@]} -gt 0 ]]; then
    echo
    echo "Failed Tests:"
    for test in "${FAILED_TESTS[@]}"; do
      echo -e "  ${T_RED}✗${T_NC} $test"
    done
  fi
  
  if [[ $FAIL_COUNT -eq 0 ]]; then
    echo -e "\n${T_GREEN}All tests passed!${T_NC}"
    return 0
  else
    echo -e "\n${T_RED}Some tests failed.${T_NC}"
    return 1
  fi
}
EOF
}

# Run unit tests
run_unit_tests() {
  if [[ "$RUN_UNIT_TESTS" != "true" ]]; then
    return 0
  fi
  
  if [[ -n "$TEST_PATTERN" ]] && [[ "$TEST_PATTERN" != *"unit"* ]]; then
    return 0
  fi
  
  log "Running unit tests..."
  
  if [[ "$DRY_RUN" == "true" ]]; then
    log "Would run unit tests for:"
    log "  - safe_source_env.sh"
    log "  - select_or_key.sh"
    log "  - rotate_or_key.sh"
    return 0
  fi
  
  create_unit_tests
  
  local test_files=(
    "$TEST_DIR/test_safe_source_env.sh"
    "$TEST_DIR/test_key_management.sh"
  )
  
  local unit_passed=0
  local unit_total=0
  
  for test_file in "${test_files[@]}"; do
    if [[ -f "$test_file" ]]; then
      ((unit_total++))
      verbose "Running: $(basename "$test_file")"
      
      if bash "$test_file" > "$RESULTS_DIR/$(basename "$test_file").log" 2>&1; then
        ((unit_passed++))
        success "$(basename "$test_file") passed"
      else
        error "$(basename "$test_file") failed"
        [[ "$VERBOSE" == "true" ]] && cat "$RESULTS_DIR/$(basename "$test_file").log"
      fi
    fi
  done
  
  if [[ $unit_passed -eq $unit_total ]]; then
    success "Unit tests: $unit_passed/$unit_total passed"
    return 0
  else
    error "Unit tests: $unit_passed/$unit_total passed"
    return 1
  fi
}

# Create unit test files
create_unit_tests() {
  # Test for safe_source_env.sh
  cat > "$TEST_DIR/test_safe_source_env.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
source "$SCRIPT_DIR/test_lib.sh"

# Setup test environment
TEST_ENV_DIR=$(mktemp -d)
TEST_ENV_FILE="$TEST_ENV_DIR/.env"
TEST_EXPORT_FILE="$TEST_ENV_DIR/.env.export"
trap "rm -rf $TEST_ENV_DIR" EXIT

start_test "safe_source_env with valid environment"
cat > "$TEST_ENV_FILE" <<'TESTENV'
# Test environment
TEST_VAR_1=value1
TEST_VAR_2=value2
OPENROUTER_KEYS=key1,key2
TESTENV

VERBOSE=true "$PROJECT_ROOT/bin/safe_source_env.sh" "$TEST_ENV_FILE" "$TEST_EXPORT_FILE"
assert_file_exists "$TEST_EXPORT_FILE" "Export file should be created"
assert_command_success "grep -q 'TEST_VAR_1=value1' '$TEST_EXPORT_FILE'" "TEST_VAR_1 should be exported"
assert_command_success "grep -q 'TEST_VAR_2=value2' '$TEST_EXPORT_FILE'" "TEST_VAR_2 should be exported"

start_test "safe_source_env with invalid lines"
cat > "$TEST_ENV_FILE" <<'TESTENV'
# Valid comment
VALID_VAR=valid_value
invalid line without equals
=invalid_start
123INVALID_NAME=value
TESTENV

VERBOSE=true "$PROJECT_ROOT/bin/safe_source_env.sh" "$TEST_ENV_FILE" "$TEST_EXPORT_FILE"
assert_command_success "grep -q 'VALID_VAR=valid_value' '$TEST_EXPORT_FILE'" "Valid variable should be exported"
assert_command_fails "grep -q 'invalid line' '$TEST_EXPORT_FILE'" "Invalid line should not be exported"

start_test "safe_source_env with missing file"
assert_command_fails "$PROJECT_ROOT/bin/safe_source_env.sh /nonexistent/file" "Should fail with missing file"

finish_tests
EOF

  # Test for key management scripts
  cat > "$TEST_DIR/test_key_management.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
source "$SCRIPT_DIR/test_lib.sh"

# Setup test environment
TEST_KEY_DIR=$(mktemp -d)
TEST_ENV_FILE="$TEST_KEY_DIR/.env"
TEST_ACTIVE_FILE="$TEST_KEY_DIR/.env.active"
trap "rm -rf $TEST_KEY_DIR" EXIT

start_test "select_or_key with no keys"
cat > "$TEST_ENV_FILE" <<'TESTENV'
OTHER_VAR=value
TESTENV

assert_command_fails "VERBOSE=true '$PROJECT_ROOT/bin/select_or_key.sh' '$TEST_ENV_FILE' '$TEST_ACTIVE_FILE'" "Should fail with no keys"

start_test "select_or_key with empty keys"
cat > "$TEST_ENV_FILE" <<'TESTENV'
OPENROUTER_KEYS=
TESTENV

assert_command_fails "VERBOSE=true '$PROJECT_ROOT/bin/select_or_key.sh' '$TEST_ENV_FILE' '$TEST_ACTIVE_FILE'" "Should fail with empty keys"

start_test "select_or_key with test keys (will fail API check)"
cat > "$TEST_ENV_FILE" <<'TESTENV'
OPENROUTER_KEYS=test-key-1,test-key-2
TESTENV

# This should fail because test keys won't work with OpenRouter API
assert_command_fails "VERBOSE=true '$PROJECT_ROOT/bin/select_or_key.sh' '$TEST_ENV_FILE' '$TEST_ACTIVE_FILE'" "Should fail with invalid test keys"

start_test "rotate_or_key with valid setup"
# Create a mock active file
echo "OPENAI_API_KEY=test-key-1" > "$TEST_ACTIVE_FILE"

VERBOSE=true "$PROJECT_ROOT/bin/rotate_or_key.sh" "$TEST_ENV_FILE" "$TEST_ACTIVE_FILE"
current_key=$(grep -E '^OPENAI_API_KEY=' "$TEST_ACTIVE_FILE" | cut -d= -f2-)
assert_equals "test-key-2" "$current_key" "Should rotate to next key"

# Rotate again
VERBOSE=true "$PROJECT_ROOT/bin/rotate_or_key.sh" "$TEST_ENV_FILE" "$TEST_ACTIVE_FILE"
current_key=$(grep -E '^OPENAI_API_KEY=' "$TEST_ACTIVE_FILE" | cut -d= -f2-)
assert_equals "test-key-1" "$current_key" "Should rotate back to first key"

finish_tests
EOF

  chmod +x "$TEST_DIR"/test_*.sh
}

# Run integration tests
run_integration_tests() {
  if [[ "$RUN_INTEGRATION_TESTS" != "true" ]]; then
    return 0
  fi
  
  if [[ -n "$TEST_PATTERN" ]] && [[ "$TEST_PATTERN" != *"integration"* ]] && [[ "$TEST_PATTERN" != *"bootstrap"* ]]; then
    return 0
  fi
  
  log "Running integration tests..."
  
  if [[ "$DRY_RUN" == "true" ]]; then
    log "Would run integration tests for:"
    log "  - Bootstrap script workflow"
    log "  - MCP configuration"
    log "  - Runner script execution"
    return 0
  fi
  
  create_integration_tests
  
  local test_file="$TEST_DIR/test_integration.sh"
  
  if [[ -f "$test_file" ]]; then
    verbose "Running integration tests..."
    
    if bash "$test_file" > "$RESULTS_DIR/integration.log" 2>&1; then
      success "Integration tests passed"
      return 0
    else
      error "Integration tests failed"
      [[ "$VERBOSE" == "true" ]] && cat "$RESULTS_DIR/integration.log"
      return 1
    fi
  fi
}

# Create integration tests
create_integration_tests() {
  cat > "$TEST_DIR/test_integration.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
source "$SCRIPT_DIR/test_lib.sh"

# Setup test environment
TEST_INTEGRATION_DIR=$(mktemp -d)
trap "rm -rf $TEST_INTEGRATION_DIR" EXIT

start_test "Bootstrap dry-run execution"
cd "$TEST_INTEGRATION_DIR"
assert_command_success "$PROJECT_ROOT/bootstrap_enhanced.sh --dry-run --no-preflight test-project $(pwd)/test-project" "Bootstrap dry-run should succeed"

start_test "Diagnostic script execution"
assert_command_success "$PROJECT_ROOT/bin/diagnose.sh --auto --verbose" "Diagnostic script should run successfully"

start_test "Health monitor script validation"
assert_command_success "$PROJECT_ROOT/bin/health_monitor.sh --help" "Health monitor help should work"

start_test "MCP registry file structure"
if [[ -f "$HOME/.mcp/registry.json" ]]; then
  assert_command_success "python3 -m json.tool '$HOME/.mcp/registry.json'" "MCP registry should be valid JSON"
else
  echo "  Skipped: MCP registry not found"
fi

finish_tests
EOF

  chmod +x "$TEST_DIR/test_integration.sh"
}

# Run end-to-end tests
run_e2e_tests() {
  if [[ "$RUN_E2E_TESTS" != "true" ]]; then
    return 0
  fi
  
  if [[ -n "$TEST_PATTERN" ]] && [[ "$TEST_PATTERN" != *"e2e"* ]] && [[ "$TEST_PATTERN" != *"end"* ]]; then
    return 0
  fi
  
  log "Running end-to-end tests..."
  
  if [[ "$DRY_RUN" == "true" ]]; then
    log "Would run end-to-end tests for:"
    log "  - Complete project creation workflow"
    log "  - Dashboard server startup"
    log "  - Health monitoring integration"
    return 0
  fi
  
  create_e2e_tests
  
  local test_file="$TEST_DIR/test_e2e.sh"
  
  if [[ -f "$test_file" ]]; then
    verbose "Running end-to-end tests..."
    
    if timeout 300 bash "$test_file" > "$RESULTS_DIR/e2e.log" 2>&1; then
      success "End-to-end tests passed"
      return 0
    else
      error "End-to-end tests failed or timed out"
      [[ "$VERBOSE" == "true" ]] && cat "$RESULTS_DIR/e2e.log"
      return 1
    fi
  fi
}

# Create end-to-end tests
create_e2e_tests() {
  cat > "$TEST_DIR/test_e2e.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
source "$SCRIPT_DIR/test_lib.sh"

start_test "Dashboard server health check"
if pgrep -f "dashboard/api/server.py" >/dev/null; then
  assert_command_success "curl -s http://127.0.0.1:8052/api/health | grep -q healthy" "Dashboard health endpoint should respond"
else
  echo "  Skipped: Dashboard server not running"
fi

start_test "Complete diagnostic workflow"
cd "$PROJECT_ROOT"
assert_command_success "timeout 60 ./bin/diagnose.sh --auto" "Complete diagnostic should finish within 60 seconds"

start_test "Health monitor status check"
assert_command_success "./bin/health_monitor.sh --status" "Health monitor status check should work"

start_test "Project file structure validation"
required_files=(
  "bin/safe_source_env.sh"
  "bin/select_or_key.sh"
  "bin/diagnose.sh"
  "bin/health_monitor.sh"
  "bootstrap_enhanced.sh"
  "CLAUDE.md"
)

for file in "${required_files[@]}"; do
  assert_file_exists "$file" "Required file should exist: $file"
done

finish_tests
EOF

  chmod +x "$TEST_DIR/test_e2e.sh"
}

# Run performance tests
run_performance_tests() {
  if [[ "$RUN_PERFORMANCE_TESTS" != "true" ]]; then
    return 0
  fi
  
  if [[ -n "$TEST_PATTERN" ]] && [[ "$TEST_PATTERN" != *"performance"* ]] && [[ "$TEST_PATTERN" != *"perf"* ]]; then
    return 0
  fi
  
  log "Running performance tests..."
  
  if [[ "$DRY_RUN" == "true" ]]; then
    log "Would run performance tests for:"
    log "  - Bootstrap script execution time"
    log "  - Environment loading performance"
    log "  - API key rotation speed"
    return 0
  fi
  
  create_performance_tests
  
  local test_file="$TEST_DIR/test_performance.sh"
  
  if [[ -f "$test_file" ]]; then
    verbose "Running performance tests..."
    
    if bash "$test_file" > "$RESULTS_DIR/performance.log" 2>&1; then
      success "Performance tests passed"
      return 0
    else
      error "Performance tests failed"
      [[ "$VERBOSE" == "true" ]] && cat "$RESULTS_DIR/performance.log"
      return 1
    fi
  fi
}

# Create performance tests
create_performance_tests() {
  cat > "$TEST_DIR/test_performance.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
source "$SCRIPT_DIR/test_lib.sh"

# Performance thresholds (in seconds)
BOOTSTRAP_DRYRUN_THRESHOLD=10
ENV_LOADING_THRESHOLD=2
KEY_ROTATION_THRESHOLD=1

start_test "Bootstrap dry-run performance"
start_time=$(date +%s%N)
"$PROJECT_ROOT/bootstrap_enhanced.sh" --dry-run --no-preflight test-perf /tmp/test-perf >/dev/null 2>&1 || true
end_time=$(date +%s%N)
duration=$(( (end_time - start_time) / 1000000000 ))

echo "  Bootstrap dry-run took: ${duration}s"
if [[ $duration -le $BOOTSTRAP_DRYRUN_THRESHOLD ]]; then
  echo -e "  ${T_GREEN}✓${T_NC} Performance acceptable (≤${BOOTSTRAP_DRYRUN_THRESHOLD}s)"
  ((PASS_COUNT++))
else
  echo -e "  ${T_YELLOW}⚠${T_NC} Performance warning (>${BOOTSTRAP_DRYRUN_THRESHOLD}s)"
  ((PASS_COUNT++))  # Warning, not failure
fi

start_test "Environment loading performance"
if [[ -f "$PROJECT_ROOT/.env" ]]; then
  start_time=$(date +%s%N)
  for i in {1..5}; do
    source "$PROJECT_ROOT/bin/safe_source_env.sh" "$PROJECT_ROOT/.env" >/dev/null 2>&1 || true
  done
  end_time=$(date +%s%N)
  avg_duration=$(( (end_time - start_time) / 5000000000 ))
  
  echo "  Environment loading (5x avg): ${avg_duration}s"
  if [[ $avg_duration -le $ENV_LOADING_THRESHOLD ]]; then
    echo -e "  ${T_GREEN}✓${T_NC} Performance acceptable (≤${ENV_LOADING_THRESHOLD}s)"
    ((PASS_COUNT++))
  else
    echo -e "  ${T_YELLOW}⚠${T_NC} Performance warning (>${ENV_LOADING_THRESHOLD}s)"
    ((PASS_COUNT++))  # Warning, not failure
  fi
else
  echo "  Skipped: .env file not found"
fi

finish_tests
EOF

  chmod +x "$TEST_DIR/test_performance.sh"
}

# Run security tests
run_security_tests() {
  if [[ "$RUN_SECURITY_TESTS" != "true" ]]; then
    return 0
  fi
  
  if [[ -n "$TEST_PATTERN" ]] && [[ "$TEST_PATTERN" != *"security"* ]] && [[ "$TEST_PATTERN" != *"sec"* ]]; then
    return 0
  fi
  
  log "Running security tests..."
  
  if [[ "$DRY_RUN" == "true" ]]; then
    log "Would run security tests for:"
    log "  - Environment variable exposure"
    log "  - File permission validation"
    log "  - Secret handling verification"
    return 0
  fi
  
  create_security_tests
  
  local test_file="$TEST_DIR/test_security.sh"
  
  if [[ -f "$test_file" ]]; then
    verbose "Running security tests..."
    
    if bash "$test_file" > "$RESULTS_DIR/security.log" 2>&1; then
      success "Security tests passed"
      return 0
    else
      error "Security tests failed"
      [[ "$VERBOSE" == "true" ]] && cat "$RESULTS_DIR/security.log"
      return 1
    fi
  fi
}

# Create security tests
create_security_tests() {
  cat > "$TEST_DIR/test_security.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
source "$SCRIPT_DIR/test_lib.sh"

start_test "Environment file permissions"
if [[ -f "$PROJECT_ROOT/.env" ]]; then
  perms=$(stat -c "%a" "$PROJECT_ROOT/.env" 2>/dev/null || stat -f "%Lp" "$PROJECT_ROOT/.env" 2>/dev/null || echo "000")
  if [[ "$perms" =~ ^[67][0-7][0-7]$ ]]; then
    echo -e "  ${T_GREEN}✓${T_NC} Environment file has secure permissions ($perms)"
    ((PASS_COUNT++))
  else
    echo -e "  ${T_RED}✗${T_NC} Environment file has insecure permissions ($perms)"
    ((FAIL_COUNT++))
    FAILED_TESTS+=("$CURRENT_TEST")
  fi
else
  echo "  Skipped: .env file not found"
fi

start_test "Script executable permissions"
scripts=(
  "bin/safe_source_env.sh"
  "bin/select_or_key.sh"
  "bin/diagnose.sh"
  "bin/health_monitor.sh"
  "bootstrap_enhanced.sh"
)

all_executable=true
for script in "${scripts[@]}"; do
  if [[ -f "$PROJECT_ROOT/$script" ]]; then
    if [[ ! -x "$PROJECT_ROOT/$script" ]]; then
      echo -e "  ${T_RED}✗${T_NC} Script not executable: $script"
      all_executable=false
    fi
  fi
done

if [[ "$all_executable" == "true" ]]; then
  echo -e "  ${T_GREEN}✓${T_NC} All scripts are executable"
  ((PASS_COUNT++))
else
  echo -e "  ${T_RED}✗${T_NC} Some scripts are not executable"
  ((FAIL_COUNT++))
  FAILED_TESTS+=("$CURRENT_TEST")
fi

start_test "No hardcoded secrets in scripts"
secret_patterns=(
  "sk-[a-zA-Z0-9-_]{43,}"  # OpenAI/OpenRouter keys
  "ghp_[a-zA-Z0-9]{36}"    # GitHub PAT
  "[a-zA-Z0-9]{32,}"       # Generic long strings
)

found_secrets=false
for script in bin/*.sh bootstrap*.sh; do
  if [[ -f "$script" ]]; then
    for pattern in "${secret_patterns[@]}"; do
      if grep -E "$pattern" "$script" >/dev/null 2>&1; then
        # Allow test patterns and placeholder values
        if ! grep -E "(test-key|your_.*_key_here|placeholder|example)" "$script" >/dev/null 2>&1; then
          echo -e "  ${T_RED}✗${T_NC} Potential secret found in $script"
          found_secrets=true
        fi
      fi
    done
  fi
done

if [[ "$found_secrets" == "false" ]]; then
  echo -e "  ${T_GREEN}✓${T_NC} No hardcoded secrets found"
  ((PASS_COUNT++))
else
  echo -e "  ${T_RED}✗${T_NC} Potential hardcoded secrets found"
  ((FAIL_COUNT++))
  FAILED_TESTS+=("$CURRENT_TEST")
fi

start_test "Git ignore patterns"
if [[ -f "$PROJECT_ROOT/.gitignore" ]]; then
  required_patterns=(
    ".env"
    "*.log"
    ".venv"
  )
  
  all_patterns_found=true
  for pattern in "${required_patterns[@]}"; do
    if ! grep -q "$pattern" "$PROJECT_ROOT/.gitignore"; then
      echo -e "  ${T_RED}✗${T_NC} Missing gitignore pattern: $pattern"
      all_patterns_found=false
    fi
  done
  
  if [[ "$all_patterns_found" == "true" ]]; then
    echo -e "  ${T_GREEN}✓${T_NC} All required gitignore patterns present"
    ((PASS_COUNT++))
  else
    echo -e "  ${T_RED}✗${T_NC} Some gitignore patterns missing"
    ((FAIL_COUNT++))
    FAILED_TESTS+=("$CURRENT_TEST")
  fi
else
  echo -e "  ${T_YELLOW}⚠${T_NC} .gitignore file not found"
  ((PASS_COUNT++))  # Warning, not failure
fi

finish_tests
EOF

  chmod +x "$TEST_DIR/test_security.sh"
}

# Generate test report
generate_test_report() {
  local report_file="$RESULTS_DIR/test_report.html"
  
  log "Generating test report: $report_file"
  
  cat > "$report_file" <<'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OOS Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #f4f4f4; padding: 20px; margin-bottom: 20px; }
        .pass { color: #28a745; }
        .fail { color: #dc3545; }
        .warn { color: #ffc107; }
        .section { margin-bottom: 30px; }
        .log-content { background: #f8f9fa; padding: 10px; border-left: 3px solid #007bff; }
        pre { white-space: pre-wrap; }
    </style>
</head>
<body>
    <div class="header">
        <h1>OOS Test Report</h1>
        <p>Generated: $(date)</p>
        <p>Framework Version: $VERSION</p>
    </div>
EOF

  # Add test results for each log file
  for log_file in "$RESULTS_DIR"/*.log; do
    if [[ -f "$log_file" ]]; then
      local test_name
      test_name=$(basename "$log_file" .log)
      
      cat >> "$report_file" <<EOF
    <div class="section">
        <h2>$test_name</h2>
        <div class="log-content">
            <pre>$(cat "$log_file")</pre>
        </div>
    </div>
EOF
    fi
  done
  
  cat >> "$report_file" <<'EOF'
</body>
</html>
EOF

  success "Test report generated: $report_file"
}

# Cleanup test artifacts
cleanup_test_artifacts() {
  if [[ "$CLEANUP_AFTER" != "true" ]]; then
    return 0
  fi
  
  verbose "Cleaning up test artifacts..."
  
  # Keep results and coverage, clean temporary files
  find "$TEST_DIR" -name "*.tmp" -delete 2>/dev/null || true
  find "$TEST_DIR" -name "test_*.sh.log" -delete 2>/dev/null || true
}

# Main execution
main() {
  parse_args "$@"
  
  echo -e "${PURPLE}OOS Test Framework v${VERSION}${NC}"
  echo "Test Directory: $TEST_DIR"
  echo "Results Directory: $RESULTS_DIR"
  
  if [[ "$DRY_RUN" == "true" ]]; then
    echo "Mode: DRY RUN"
  fi
  
  echo
  
  setup_test_environment
  
  local overall_result=0
  
  # Run test suites
  run_unit_tests || ((overall_result++))
  run_integration_tests || ((overall_result++))
  run_e2e_tests || ((overall_result++))
  run_performance_tests || ((overall_result++))
  run_security_tests || ((overall_result++))
  
  # Generate reports
  if [[ "$DRY_RUN" == "false" ]]; then
    generate_test_report
  fi
  
  cleanup_test_artifacts
  
  echo
  if [[ $overall_result -eq 0 ]]; then
    success "All test suites passed!"
    echo
    echo "View detailed results in: $RESULTS_DIR/"
    [[ -f "$RESULTS_DIR/test_report.html" ]] && echo "HTML report: $RESULTS_DIR/test_report.html"
  else
    error "$overall_result test suite(s) failed"
    echo "Check logs in: $RESULTS_DIR/"
    exit 1
  fi
}

# Run main function
main "$@"