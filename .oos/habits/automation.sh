#!/bin/bash
# Auto-generated agentic workflow automation

# Terminal integration - add to your shell config
agentic_auto_start() {
    if [ -f "/home/ubuntu/dev/oos/.oos/habits/active" ]; then
        echo "🤖 Agentic mode active - use /do, /solve, /learn, /complete"
    else
        echo "💡 Start your agentic session: /morning"
    fi
}

# Aliases for daily use
alias morning='/home/ubuntu/dev/oos/bin/agentic-daily.sh morning'
alias evening='/home/ubuntu/dev/oos/bin/agentic-daily.sh evening'
alias do='/home/ubuntu/dev/oos/bin/agentic-daily.sh do'
alias solve='/home/ubuntu/dev/oos/bin/agentic-daily.sh solve'
alias learn='/home/ubuntu/dev/oos/bin/agentic-daily.sh learn'
alias complete='/home/ubuntu/dev/oos/bin/agentic-daily.sh complete'

# Smart prompt integration
if [ "$PS1" ]; then
    agentic_auto_start
fi
