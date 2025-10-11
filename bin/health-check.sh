#!/bin/bash
# OOS Comprehensive Health Check System
# Monitors system health, performance, and service status

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
HEALTH_LOG="$PROJECT_ROOT/logs/health.log"
METRICS_DIR="$PROJECT_ROOT/logs/metrics"
ALERT_THRESHOLD=80
MAX_RESPONSE_TIME=5.0

# Create directories
mkdir -p "$(dirname "$HEALTH_LOG")" "$METRICS_DIR"

# Health check results
OVERALL_HEALTH="healthy"
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
WARNINGS=0

# Timestamp
TIMESTAMP=$(date -Iseconds)

# Help text
usage() {
    cat << EOF
OOS Health Check System

USAGE:
    $0 [OPTIONS]

DESCRIPTION:
    Comprehensive health monitoring for OOS system components including
    services, resources, performance, and external dependencies.

OPTIONS:
    --verbose           Show detailed output during checks
    --json              Output results in JSON format
    --continuous        Run checks continuously (every 60 seconds)
    --once              Run checks once and exit (default)
    --alert-threshold N Set alert threshold percentage (default: 80)
    --quiet             Suppress output, only return exit code
    --help              Show this help message

EXIT CODES:
    0   All checks passed (healthy)
    1   Some checks failed (unhealthy)
    2   Critical failures detected
    3   Invalid arguments

EXAMPLES:
    $0                          # Run health check once
    $0 --verbose                # Show detailed output
    $0 --json                   # JSON output for monitoring systems
    $0 --continuous             # Run continuously

COMPONENTS CHECKED:
    • System resources (CPU, memory, disk)
    • Service health (OOS services, databases)
    • Network connectivity
    • External dependencies
    • Performance metrics
    • Security status
    • Backup status

EOF
}

# Logging functions
log_health() {
    local level="$1"
    local message="$2"
    echo "[$TIMESTAMP] [$level] $message" >> "$HEALTH_LOG"
}

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
    log_health "INFO" "$1"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
    log_health "SUCCESS" "$1"
    ((PASSED_CHECKS++))
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    log_health "WARNING" "$1"
    ((WARNINGS++))
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
    log_health "ERROR" "$1"
    ((FAILED_CHECKS++))
    OVERALL_HEALTH="unhealthy"
}

log_verbose() {
    if [[ "$VERBOSE" == "true" ]]; then
        echo -e "${PURPLE}🔍 $1${NC}"
    fi
}

# Default values
VERBOSE=false
JSON_OUTPUT=false
CONTINUOUS=false
QUIET=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --verbose)
            VERBOSE=true
            shift
            ;;
        --json)
            JSON_OUTPUT=true
            shift
            ;;
        --continuous)
            CONTINUOUS=true
            shift
            ;;
        --once)
            CONTINUOUS=false
            shift
            ;;
        --alert-threshold)
            ALERT_THRESHOLD="$2"
            shift 2
            ;;
        --quiet)
            QUIET=true
            shift
            ;;
        --help)
            usage
            exit 0
            ;;
        -*)
            log_error "Unknown option: $1"
            usage
            exit 3
            ;;
        *)
            log_error "Invalid argument: $1"
            usage
            exit 3
            ;;
    esac
done

# JSON output structure
json_start() {
    echo "{"
    echo "  \"timestamp\": \"$TIMESTAMP\","
    echo "  \"overall_health\": \"$OVERALL_HEALTH\","
    echo "  \"checks\": {"
}

json_end() {
    local health_percentage=$(( (PASSED_CHECKS * 100) / TOTAL_CHECKS ))
    echo "  },"
    echo "  \"summary\": {"
    echo "    \"total_checks\": $TOTAL_CHECKS,"
    echo "    \"passed_checks\": $PASSED_CHECKS,"
    echo "    \"failed_checks\": $FAILED_CHECKS,"
    echo "    \"warnings\": $WARNINGS,"
    echo "    \"health_percentage\": $health_percentage"
    echo "  }"
    echo "}"
}

# Check functions
check_system_resources() {
    ((TOTAL_CHECKS++))
    log_verbose "Checking system resources..."

    # CPU usage
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//')
    local cpu_check=true

    # Memory usage
    local mem_info=$(free -m | grep Mem)
    local total_mem=$(echo $mem_info | awk '{print $2}')
    local used_mem=$(echo $mem_info | awk '{print $3}')
    local mem_usage=$(( (used_mem * 100) / total_mem ))
    local mem_check=true

    # Disk usage
    local disk_usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    local disk_check=true

    # Evaluate resource usage
    if (( cpu_usage > 80 )); then
        log_error "High CPU usage: ${cpu_usage}%"
        cpu_check=false
    fi

    if (( mem_usage > 85 )); then
        log_error "High memory usage: ${mem_usage}%"
        mem_check=false
    elif (( mem_usage > 70 )); then
        log_warning "Moderate memory usage: ${mem_usage}%"
    fi

    if (( disk_usage > 90 )); then
        log_error "High disk usage: ${disk_usage}%"
        disk_check=false
    elif (( disk_usage > 80 )); then
        log_warning "Moderate disk usage: ${disk_usage}%"
    fi

    if $cpu_check && $mem_check && $disk_check; then
        log_success "System resources: CPU ${cpu_usage}%, Memory ${mem_usage}%, Disk ${disk_usage}%"
    fi

    # Save metrics
    echo "$TIMESTAMP,$cpu_usage,$mem_usage,$disk_usage" >> "$METRICS_DIR/resources.csv"
}

check_service_health() {
    ((TOTAL_CHECKS++))
    log_verbose "Checking service health..."

    local services_healthy=true

    # Check OOS-specific services
    if systemctl list-unit-files | grep -q "oos"; then
        local oos_services=$(systemctl list-units --type=service --state=running | grep oos | awk '{print $1}')

        if [[ -n "$oos_services" ]]; then
            while IFS= read -r service; do
                if systemctl is-active --quiet "$service"; then
                    log_verbose "Service $service is running"
                else
                    log_error "Service $service is not running"
                    services_healthy=false
                fi
            done <<< "$oos_services"
        else
            log_warning "No OOS services found"
        fi
    else
        log_info "No systemd OOS services configured"
    fi

    # Check critical processes
    local critical_processes=("claude" "python" "uv" "git")
    for process in "${critical_processes[@]}"; do
        if pgrep -x "$process" > /dev/null; then
            log_verbose "Process $process is running"
        else
            log_verbose "Process $process not running (may be normal)"
        fi
    done

    if $services_healthy; then
        log_success "Service health check passed"
    fi
}

check_network_connectivity() {
    ((TOTAL_CHECKS++))
    log_verbose "Checking network connectivity..."

    local network_healthy=true

    # Check internet connectivity
    if ping -c 1 -W 5 8.8.8.8 > /dev/null 2>&1; then
        log_verbose "Internet connectivity OK"
    else
        log_error "No internet connectivity"
        network_healthy=false
    fi

    # Check DNS resolution
    if nslookup github.com > /dev/null 2>&1; then
        log_verbose "DNS resolution OK"
    else
        log_warning "DNS resolution issues detected"
    fi

    # Check if we can reach GitHub
    if curl -s --connect-timeout 5 https://github.com > /dev/null; then
        log_verbose "GitHub connectivity OK"
    else
        log_warning "GitHub connectivity issues"
    fi

    if $network_healthy; then
        log_success "Network connectivity check passed"
    fi
}

check_external_dependencies() {
    ((TOTAL_CHECKS++))
    log_verbose "Checking external dependencies..."

    local deps_healthy=true

    # Check for required tools
    local required_tools=("git" "python3" "uv" "curl" "jq")
    for tool in "${required_tools[@]}"; do
        if command -v "$tool" > /dev/null 2>&1; then
            log_verbose "Tool $tool is available"
        else
            log_error "Required tool $tool is missing"
            deps_healthy=false
        fi
    done

    # Check Python packages
    if command -v python3 > /dev/null; then
        local critical_packages=("click" "requests" "pyyaml")
        for package in "${critical_packages[@]}"; do
            if python3 -c "import $package" 2>/dev/null; then
                log_verbose "Python package $package is available"
            else
                log_warning "Python package $package is missing"
            fi
        done
    fi

    if $deps_healthy; then
        log_success "External dependencies check passed"
    fi
}

check_performance_metrics() {
    ((TOTAL_CHECKS++))
    log_verbose "Checking performance metrics..."

    # Measure response time for critical operations
    local start_time=$(date +%s.%N)

    # Test Git operation
    if git status > /dev/null 2>&1; then
        local end_time=$(date +%s.%N)
        local git_time=$(echo "$end_time - $start_time" | bc)

        if (( $(echo "$git_time > $MAX_RESPONSE_TIME" | bc -l) )); then
            log_warning "Slow git response: ${git_time}s"
        else
            log_verbose "Git response time: ${git_time}s"
        fi
    fi

    # Check system load
    local load_avg=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//')
    local cpu_cores=$(nproc)
    local load_percentage=$(echo "scale=1; $load_avg / $cpu_cores * 100" | bc)

    if (( $(echo "$load_percentage > 200" | bc -l) )); then
        log_error "High system load: $load_avg ($load_percentage% of CPU capacity)"
    elif (( $(echo "$load_percentage > 100" | bc -l) )); then
        log_warning "Moderate system load: $load_avg ($load_percentage% of CPU capacity)"
    else
        log_verbose "System load: $load_avg ($load_percentage% of CPU capacity)"
    fi

    log_success "Performance metrics check completed"
}

check_security_status() {
    ((TOTAL_CHECKS++))
    log_verbose "Checking security status..."

    # Check for exposed API keys (basic check)
    local exposed_keys=false
    if grep -r "sk-[a-zA-Z0-9]" "$PROJECT_ROOT" --include="*.sh" --include="*.py" --include="*.env*" 2>/dev/null | head -1 | grep -q .; then
        log_warning "Potential exposed API keys detected"
        exposed_keys=true
    fi

    # Check file permissions
    local config_perms=$(stat -c "%a" "$PROJECT_ROOT/.git/config" 2>/dev/null || echo "000")
    if [[ "$config_perms" != "600" && "$config_perms" != "644" ]]; then
        log_warning "Unusual file permissions on .git/config: $config_perms"
    fi

    # Check for suspicious processes
    if pgrep -f "strace\|gdb\|lldb" > /dev/null; then
        log_warning "Debugging tools detected running"
    fi

    if ! $exposed_keys; then
        log_success "Security status check passed"
    fi
}

check_backup_status() {
    ((TOTAL_CHECKS++))
    log_verbose "Checking backup status..."

    local backup_found=false

    # Check for recent backups (look for common backup patterns)
    local backup_patterns=("*.backup" "*.bak" "backup-*" "*.sql.gz")
    for pattern in "${backup_patterns[@]}"; do
        if find "$PROJECT_ROOT" -name "$pattern" -mtime -7 | head -1 | grep -q .; then
            backup_found=true
            break
        fi
    done

    # Check git status as a form of backup
    if git status > /dev/null 2>&1; then
        local uncommitted=$(git status --porcelain | wc -l)
        if (( uncommitted > 50 )); then
            log_warning "High number of uncommitted changes: $uncommitted"
        fi
    fi

    if $backup_found; then
        log_success "Recent backups found"
    else
        log_info "No recent backups detected (may be normal)"
    fi
}

# Main health check function
run_health_checks() {
    if [[ "$JSON_OUTPUT" == "true" ]]; then
        json_start
    elif [[ "$QUIET" != "true" ]]; then
        echo "🏥 OOS Health Check - $TIMESTAMP"
        echo "=================================="
        echo ""
    fi

    # Run all checks
    check_system_resources
    check_service_health
    check_network_connectivity
    check_external_dependencies
    check_performance_metrics
    check_security_status
    check_backup_status

    # Calculate final health percentage
    local health_percentage=$(( (PASSED_CHECKS * 100) / TOTAL_CHECKS ))

    if [[ "$JSON_OUTPUT" == "true" ]]; then
        json_end
    elif [[ "$QUIET" != "true" ]]; then
        echo ""
        echo "📊 Health Check Summary:"
        echo "  Total checks: $TOTAL_CHECKS"
        echo "  Passed: $PASSED_CHECKS"
        echo "  Failed: $FAILED_CHECKS"
        echo "  Warnings: $WARNINGS"
        echo "  Health Score: $health_percentage%"
        echo ""

        if (( health_percentage >= ALERT_THRESHOLD )); then
            echo -e "${GREEN}🎉 System Status: HEALTHY${NC}"
        elif (( health_percentage >= 60 )); then
            echo -e "${YELLOW}⚠️  System Status: WARNING${NC}"
        else
            echo -e "${RED}🚨 System Status: UNHEALTHY${NC}"
        fi
    fi

    # Set exit code based on health
    if (( health_percentage >= ALERT_THRESHOLD )); then
        return 0
    elif (( health_percentage >= 60 )); then
        return 1
    else
        return 2
    fi
}

# Continuous monitoring mode
run_continuous() {
    log_info "Starting continuous health monitoring (interval: 60s)"
    log_info "Press Ctrl+C to stop"

    while true; do
        run_health_checks
        sleep 60
    done
}

# Main execution
main() {
    # Check for required tools
    command -v bc > /dev/null || {
        log_error "bc calculator is required for health checks"
        exit 2
    }

    if [[ "$CONTINUOUS" == "true" ]]; then
        run_continuous
    else
        run_health_checks
    fi
}

# Run main function
main "$@"