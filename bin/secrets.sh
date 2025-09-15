#!/usr/bin/env bash
set -euo pipefail

# Secrets Management for OOS
# Based on learnings from ZAI integration challenges

SECRETS_DIR="${HOME}/.config/oos/secrets.d"
ZAI_KEY_FILE="${SECRETS_DIR}/zai.key"

# Ensure secrets directory exists
setup_secrets_dir() {
    mkdir -p "${SECRETS_DIR}"
    chmod 700 "${SECRETS_DIR}"
}

# Store ZAI key securely
store_zai_key() {
    local key="$1"

    if [[ -z "${key}" ]]; then
        echo "Error: No key provided" >&2
        return 1
    fi

    setup_secrets_dir

    # Write key with secure permissions
    umask 077
    printf '%s\n' "${key}" > "${ZAI_KEY_FILE}"
    chmod 600 "${ZAI_KEY_FILE}"

    echo "ZAI key stored securely in ${ZAI_KEY_FILE}"
}

# Get stored ZAI key
get_zai_key() {
    if [[ ! -f "${ZAI_KEY_FILE}" ]]; then
        echo "" >&2
        return 1
    fi

    # Strip any whitespace/newlines
    tr -d ' \t\n\r' < "${ZAI_KEY_FILE}"
}

# Check if ZAI key exists
has_zai_key() {
    [[ -f "${ZAI_KEY_FILE}" ]] && [[ -s "${ZAI_KEY_FILE}" ]]
}

# Remove ZAI key
remove_zai_key() {
    if [[ -f "${ZAI_KEY_FILE}" ]]; then
        rm -f "${ZAI_KEY_FILE}"
        echo "ZAI key removed"
    fi
}

# List all stored secrets
list_secrets() {
    if [[ ! -d "${SECRETS_DIR}" ]]; then
        echo "No secrets directory found"
        return 0
    fi

    echo "Stored secrets:"
    find "${SECRETS_DIR}" -type f -name "*.key" -exec basename {} \; | sed 's/\.key$//'
}

# Validate ZAI key format
validate_zai_key() {
    local key="$1"

    if [[ -z "${key}" ]]; then
        echo "Error: Key is empty" >&2
        return 1
    fi

    # Basic validation - ZAI keys typically start with "zai-"
    if [[ ! "${key}" =~ ^zai- ]]; then
        echo "Warning: Key doesn't start with 'zai-'" >&2
    fi

    # Check key length (ZAI keys are typically 40+ characters)
    if [[ ${#key} -lt 30 ]]; then
        echo "Warning: Key seems too short" >&2
    fi

    echo "Key format appears valid"
}

# Show key info (without revealing the key)
show_zai_key_info() {
    if ! has_zai_key; then
        echo "No ZAI key stored"
        return 1
    fi

    local key_file="${ZAI_KEY_FILE}"
    local file_size=$(stat -f%z "${key_file}" 2>/dev/null || stat -c%s "${key_file}" 2>/dev/null || echo "unknown")
    local modified=$(stat -f%Sm -t"%Y-%m-%d %H:%M:%S" "${key_file}" 2>/dev/null || stat -c%y "${key_file}" 2>/dev/null || echo "unknown")

    echo "ZAI Key Information:"
    echo "  File: ${key_file}"
    echo "  Size: ${file_size} bytes"
    echo "  Modified: ${modified}"
    echo "  Permissions: $(ls -l "${key_file}" | cut -d' ' -f1)"
}

# Main command dispatcher
case "${1:-}" in
    store)
        if [[ $# -ne 2 ]]; then
            echo "Usage: $0 store <zai_key>" >&2
            exit 1
        fi
        store_zai_key "$2"
        ;;
    get)
        get_zai_key
        ;;
    has)
        if has_zai_key; then
            echo "ZAI key exists"
            exit 0
        else
            echo "No ZAI key found"
            exit 1
        fi
        ;;
    remove)
        remove_zai_key
        ;;
    list)
        list_secrets
        ;;
    validate)
        if [[ $# -ne 2 ]]; then
            echo "Usage: $0 validate <zai_key>" >&2
            exit 1
        fi
        validate_zai_key "$2"
        ;;
    info)
        show_zai_key_info
        ;;
    setup)
        setup_secrets_dir
        echo "Secrets directory created at ${SECRETS_DIR}"
        ;;
    *)
        echo "OOS Secrets Management"
        echo ""
        echo "Usage: $0 <command> [args]"
        echo ""
        echo "Commands:"
        echo "  store <key>     Store ZAI key securely"
        echo "  get            Get stored ZAI key"
        echo "  has            Check if ZAI key exists"
        echo "  remove         Remove stored ZAI key"
        echo "  list           List all stored secrets"
        echo "  validate <key> Validate key format"
        echo "  info           Show key information"
        echo "  setup          Create secrets directory"
        echo ""
        echo "Examples:"
        echo "  $0 store zai-1234567890abcdef"
        echo "  $0 get"
        echo "  $0 has"
        exit 1
        ;;
esac