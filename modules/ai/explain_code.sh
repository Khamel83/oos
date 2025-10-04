#!/usr/bin/env bash
# Module: ai/explain_code
# Purpose: Generate explanation for code file or function
# Input: file path [function_name]
# Output: code explanation
# Exit codes: 0=success, 1=file not found, 2=invalid input

set -euo pipefail

FILE_PATH="$1"
FUNCTION_NAME="${2:-}"

if [[ ! -f "$FILE_PATH" ]]; then
    echo "File not found: $FILE_PATH"
    exit 1
fi

echo "Analyzing code in: $FILE_PATH"

# Get file extension to determine language
EXT="${FILE_PATH##*.}"

case "$EXT" in
    "py")
        LANGUAGE="Python"
        ;;
    "js"|"ts")
        LANGUAGE="JavaScript/TypeScript"
        ;;
    "sh")
        LANGUAGE="Shell/Bash"
        ;;
    "go")
        LANGUAGE="Go"
        ;;
    "rs")
        LANGUAGE="Rust"
        ;;
    *)
        LANGUAGE="Unknown"
        ;;
esac

echo "Language: $LANGUAGE"

# Show file stats
LINES=$(wc -l < "$FILE_PATH")
CHARS=$(wc -c < "$FILE_PATH")

echo "Lines: $LINES"
echo "Characters: $CHARS"

# Extract function if specified
if [[ -n "$FUNCTION_NAME" ]]; then
    echo ""
    echo "Looking for function: $FUNCTION_NAME"

    case "$LANGUAGE" in
        "Python")
            grep -A 20 "def $FUNCTION_NAME(" "$FILE_PATH" || echo "Function not found"
            ;;
        "JavaScript/TypeScript")
            grep -A 20 "function $FUNCTION_NAME\|const $FUNCTION_NAME\|$FUNCTION_NAME.*=" "$FILE_PATH" || echo "Function not found"
            ;;
        "Shell/Bash")
            grep -A 20 "$FUNCTION_NAME()" "$FILE_PATH" || echo "Function not found"
            ;;
        *)
            echo "Function extraction not supported for $LANGUAGE"
            ;;
    esac
else
    echo ""
    echo "File structure:"

    # Show imports/includes
    case "$LANGUAGE" in
        "Python")
            echo "Imports:"
            grep "^import\|^from.*import" "$FILE_PATH" | head -5 || echo "No imports found"
            echo ""
            echo "Functions:"
            grep "^def " "$FILE_PATH" | head -10 || echo "No functions found"
            ;;
        "JavaScript/TypeScript")
            echo "Imports:"
            grep "^import\|^const.*require" "$FILE_PATH" | head -5 || echo "No imports found"
            echo ""
            echo "Functions:"
            grep "function\|const.*=.*=>" "$FILE_PATH" | head -10 || echo "No functions found"
            ;;
        "Shell/Bash")
            echo "Functions:"
            grep "^[a-zA-Z_][a-zA-Z0-9_]*() {" "$FILE_PATH" | head -10 || echo "No functions found"
            ;;
    esac
fi

echo ""
echo "Summary: $LANGUAGE file with $LINES lines of code"

exit 0