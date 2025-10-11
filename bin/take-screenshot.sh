#!/bin/bash

# OOS Screenshot Analysis Tool
# Takes screenshot and sends to Claude for analysis

echo "📸 OOS Screenshot Analysis"
echo "=========================="

# Create screenshots directory if it doesn't exist
mkdir -p "$HOME/Screenshots/oos"

# Generate timestamp filename
timestamp=$(date +"%Y%m%d_%H%M%S")
screenshot_path="$HOME/Screenshots/oos/screenshot_${timestamp}.png"

# Detect platform and take screenshot
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo "📱 Taking screenshot on macOS..."
    screencapture -i "$screenshot_path"
    screenshot_status=$?
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    echo "🖥️  Taking screenshot on Linux..."
    if command -v gnome-screenshot &> /dev/null; then
        gnome-screenshot -f "$screenshot_path"
        screenshot_status=$?
    elif command -v scrot &> /dev/null; then
        scrot "$screenshot_path"
        screenshot_status=$?
    elif command -v import &> /dev/null; then
        # ImageMagick
        import "$screenshot_path"
        screenshot_status=$?
    else
        echo "❌ No screenshot tool found. Install gnome-screenshot, scrot, or imagemagick"
        echo "   Ubuntu: sudo apt install gnome-screenshot"
        echo "   Other: sudo apt install scrot"
        exit 1
    fi
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    # Windows
    echo "🪟 Taking screenshot on Windows..."
    powershell -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Screen]::PrimaryScreen.Bounds | ForEach-Object { \$bmp = New-Object System.Drawing.Bitmap(\$_.Width, \$_.Height); \$graphics = [System.Drawing.Graphics]::FromImage(\$bmp); \$graphics.CopyFromScreen(\$_.X, \$_.Y, 0, 0, \$_.Size); \$bmp.Save('$screenshot_path', [System.Drawing.Imaging.ImageFormat]::Png); }"
    screenshot_status=$?
else
    echo "❌ Unsupported operating system: $OSTYPE"
    exit 1
fi

# Check if screenshot was taken successfully
if [ $screenshot_status -ne 0 ] || [ ! -f "$screenshot_path" ]; then
    echo "❌ Screenshot failed"
    exit 1
fi

echo "✅ Screenshot saved: $screenshot_path"

# Get analysis prompt
analysis_prompt="${1:-Analyze this screenshot and tell me what you see. Focus on UI/UX issues, improvements, or anything notable.}"

echo "🤖 Analyzing with Claude..."
echo "Prompt: $analysis_prompt"
echo ""

# Send to Claude Code for analysis
if command -v claude &> /dev/null; then
    # Use Claude Code to analyze the screenshot
    echo "Please analyze this screenshot: $analysis_prompt" | claude --print --output-format=text

    # Also copy path to clipboard for manual use
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "$screenshot_path" | pbcopy
        echo "📋 Screenshot path copied to clipboard"
    elif command -v xclip &> /dev/null; then
        echo "$screenshot_path" | xclip -selection clipboard
        echo "📋 Screenshot path copied to clipboard"
    fi

else
    echo "❌ Claude Code not found. Please install Claude Code first."
    echo "💡 Screenshot saved at: $screenshot_path"
    echo "📋 You can manually drag this file into Claude Code for analysis"
fi

echo ""
echo "🎯 Use cases:"
echo "  ./bin/take-screenshot.sh"
echo "  ./bin/take-screenshot.sh 'Review this design for accessibility issues'"
echo "  ./bin/take-screenshot.sh 'What improvements would you suggest for this interface?'"