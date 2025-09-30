#!/bin/bash
# Simple OOS Deposit - Copy OOS to any project in 5 lines
set -e

echo "🚀 Depositing OOS into project..."

# Copy core files to current project
mkdir -p .claude .oos bin
cp -r .claude/* .claude/ 2>/dev/null || true
cp -r .oos/* .oos/ 2>/dev/null || true
cp bin/*.sh bin/ 2>/dev/null || true

# Make everything executable
chmod +x bin/*.sh 2>/dev/null || true

echo "✅ OOS deposited! Use ./bin/oos-v1.2.sh to start"