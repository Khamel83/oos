#!/bin/bash
# OOS One-Line Installer
set -e

echo "🚀 Installing OOS (Organized Operational Setup)..."

# Detect OS
OS="$(uname -s)"
case "${OS}" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=Mac;;
    *)          MACHINE="UNKNOWN:${OS}"
esac

echo "📍 Detected: $MACHINE"

# Check requirements
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found"
    echo "Install with: sudo apt install python3 (Ubuntu) or brew install python3 (Mac)"
    exit 1
fi

if ! command -v git &> /dev/null; then
    echo "❌ Git is required but not found"
    echo "Install with: sudo apt install git (Ubuntu) or brew install git (Mac)"
    exit 1
fi

echo "✅ Python 3 and Git found"

# Install directory
INSTALL_DIR="$HOME/oos"

# Remove existing installation
if [ -d "$INSTALL_DIR" ]; then
    echo "🔄 Updating existing OOS installation..."
    cd "$INSTALL_DIR"
    git pull
else
    echo "📥 Cloning OOS repository..."
    git clone https://github.com/Khamel83/oos.git "$INSTALL_DIR"
fi

# Make executable
chmod +x "$INSTALL_DIR/run.py"

# Try to create global command
if command -v sudo &> /dev/null; then
    echo "🔗 Creating global 'oos' command..."
    if sudo ln -sf "$INSTALL_DIR/run.py" /usr/local/bin/oos 2>/dev/null; then
        echo "✅ Global 'oos' command created"
        GLOBAL_INSTALL=true
    else
        echo "⚠️  Could not create global command (sudo failed)"
        GLOBAL_INSTALL=false
    fi
else
    echo "⚠️  No sudo available, skipping global installation"
    GLOBAL_INSTALL=false
fi

# Create personal alias if global install failed
if [ "$GLOBAL_INSTALL" = false ]; then
    echo "🔗 Adding personal alias..."
    
    # Detect shell
    SHELL_RC=""
    if [ -n "$BASH_VERSION" ]; then
        SHELL_RC="$HOME/.bashrc"
    elif [ -n "$ZSH_VERSION" ]; then
        SHELL_RC="$HOME/.zshrc"
    else
        SHELL_RC="$HOME/.profile"
    fi
    
    # Add alias if not already present
    ALIAS_LINE='alias oos="$HOME/oos/run.py"'
    if ! grep -q "alias oos=" "$SHELL_RC" 2>/dev/null; then
        echo "$ALIAS_LINE" >> "$SHELL_RC"
        echo "✅ Added 'oos' alias to $SHELL_RC"
        echo "   Run: source $SHELL_RC (or restart terminal)"
    else
        echo "✅ Alias already exists in $SHELL_RC"
    fi
fi

# Check optional dependencies
echo ""
echo "🔍 Checking optional dependencies..."

if command -v op &> /dev/null; then
    echo "✅ 1Password CLI found"
else
    echo "⚠️  1Password CLI not found (optional for secure environments)"
    echo "   Install: https://developer.1password.com/docs/cli/get-started/"
fi

if command -v gh &> /dev/null; then
    echo "✅ GitHub CLI found"
else
    echo "⚠️  GitHub CLI not found (optional for GitHub integration)"
    echo "   Install: https://cli.github.com/"
fi

echo ""
echo "🎉 OOS installation complete!"
echo ""
echo "📖 Usage:"
if [ "$GLOBAL_INSTALL" = true ]; then
    echo "  oos              # Interactive setup from any directory"
    echo "  oos --help       # Show help"
else
    echo "  $HOME/oos/run.py # Interactive setup"
    echo "  oos              # If you restart your terminal/source shell config"
fi
echo ""
echo "🚀 Try it now:"
echo "  mkdir /tmp/test-project && cd /tmp/test-project"
if [ "$GLOBAL_INSTALL" = true ]; then
    echo "  oos"
else
    echo "  $HOME/oos/run.py"
fi
echo ""
echo "📚 Full documentation: $INSTALL_DIR/README_NEW_INTERFACE.md"