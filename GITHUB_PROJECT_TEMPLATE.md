# 📋 GitHub Project Template for Secure Development

## 🎯 Quick Start

This template provides a complete, secure development environment with:
- ✅ **Simple secrets management** (no complex interfaces)
- ✅ **Automatic security protection** (pre-commit hooks)
- ✅ **AI agent ready** (non-interactive secret access)
- ✅ **Zero API key exposure risk** (git protection)

## 🚀 Setup Instructions

### Step 1: Clone this Template
```bash
git clone https://github.com/YOUR_USERNAME/template-name.git your-project-name
cd your-project-name
rm -rf .git  # Remove the template's git history
git init       # Start fresh git history
```

### Step 2: Install Security System
```bash
./bin/setup-simple-security.sh
```

### Step 3: Add Your API Keys
```bash
nano .env
# Add your actual API keys here
```

### Step 4: Test Everything Works
```bash
python3 bin/get-secrets.py list
python3 bin/get-secrets.py get OPENROUTER_API_KEY
```

### Step 5: Push Your New Project
```bash
git add .
git commit -m "Initial commit - secure project setup"
git remote add origin https://github.com/YOUR_USERNAME/your-project-name.git
git push -u origin main
```

## 📁 Project Structure

```
your-project/
├── .env                 # Your API keys (gitignored)
├── .gitignore          # Prevents secret exposure
├── bin/
│   ├── setup-simple-security.sh  # Install security system
│   ├── setup-new-project.sh      # Copy secrets from master
│   └── get-secrets.py            # AI secrets client
├── src/                # Your source code
├── tests/              # Your tests
└── docs/               # Your documentation
```

## 🔐 Security Features

### ✅ **Protection Against Exposure**
- `.env` file is in `.gitignore` - never committed
- Pre-commit hooks block secret commits
- Secrets are masked in logs and displays
- No hardcoded secrets in code

### ✅ **Secure Secret Access**
```python
# Your application code
import os
from dotenv import load_dotenv

load_dotenv()  # Load from .env file
api_key = os.getenv('OPENROUTER_API_KEY')
```

### ✅ **AI Agent Integration**
```python
# AI agent can access secrets non-interactively
import sys
sys.path.append('bin')
from get_secrets import SimpleSecrets

secrets = SimpleSecrets()
api_key = secrets.get('OPENROUTER_API_KEY')
```

## 🔧 For AI Agents

### Simple Usage
```python
#!/usr/bin/env python3
import sys
sys.path.append('bin')
from get_secrets import SimpleSecrets

class MyAIAgent:
    def __init__(self):
        self.secrets = SimpleSecrets()
        self.api_key = self.secrets.get('OPENROUTER_API_KEY')

    def make_request(self, prompt):
        if self.api_key:
            # Make API request using self.api_key
            return f"Response using API key: {self.api_key[:8]}..."
        else:
            return "No API key available"

agent = MyAIAgent()
print(agent.make_request("Hello world!"))
```

### Non-Interactive Usage
```bash
# AI agents can access secrets without any interaction
python3 my_ai_agent.py

# Or get specific secrets
python3 bin/get-secrets.py get OPENROUTER_API_KEY
```

## 📋 Available Commands

### Security Setup
```bash
./bin/setup-simple-security.sh    # Install security system
```

### Secrets Management
```bash
python3 bin/get-secrets.py list           # List all secrets
python3 bin/get-secrets.py get KEY_NAME   # Get specific secret
```

### Project Setup
```bash
./bin/setup-new-project.sh /path/to/new/project  # Copy secrets to new project
```

### Git Hooks
```bash
git commit -m "Your commit message"  # Automatically checks for secrets
```

## 🛡️ Security Rules

### ✅ **DO**
- Store secrets in `.env` file only
- Use environment variables in code
- Test with `python3 bin/get-secrets.py list`
- Commit `.gitignore` to your repository

### ❌ **DO NOT**
- Hardcode API keys in source code
- Commit `.env` file to git
- Copy-paste API keys between projects
- Use complex secrets managers unless necessary

## 🎯 Use Cases

### Web Applications
```python
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['API_KEY'] = os.getenv('OPENROUTER_API_KEY')
```

### CLI Tools
```python
import click
import os
from dotenv import load_dotenv

load_dotenv()

@click.command()
def api_call():
    api_key = os.getenv('OPENROUTER_API_KEY')
    click.echo(f"Using API key: {api_key[:8]}...")
```

### AI Agents
```python
from get_secrets import SimpleSecrets

class Agent:
    def __init__(self):
        self.secrets = SimpleSecrets()

    def authenticate(self):
        return self.secrets.get('OPENROUTER_API_KEY')
```

## 🔄 For Multiple Projects

### Master Secrets Repository
Keep your main `.env` file in one location, then copy to projects:

```bash
# In each new project
~/master/bin/setup-new-project.sh ~/projects/awesome-app
```

### Team Usage
Each team member can:
1. Clone this template
2. Add their own API keys to `.env`
3. Never commit `.env` file
4. Share project code safely

## 📚 Documentation Templates

### README Template
```markdown
# Project Name

## Setup

1. Clone this repository
2. Run setup script:
   ```bash
   ./bin/setup-simple-security.sh
   ```
3. Add your API keys to `.env` file
4. Test access:
   ```bash
   python3 bin/get-secrets.py list
   ```

## Usage

Your application usage instructions here.
```

### Environment Variables Template
```markdown
# Environment Variables

This project uses environment variables for configuration. Copy `.env.example` to `.env` and fill in your values.

Required Variables:
- `OPENROUTER_API_KEY`: Your OpenRouter API key
- `OPENAI_API_KEY`: Your OpenAI API key (optional)

Development Variables:
- `DEBUG`: Enable debug mode
- `LOG_LEVEL`: Set logging level
```

## 🎯 Why This Template?

### ✅ **Simple**
- No complex secret managers
- Standard file operations
- Clear documentation
- Quick setup time

### ✅ **Secure**
- Git protection against exposure
- No hardcoded secrets
- Masked logging
- Pre-commit validation

### ✅ **Universal**
- Works with any programming language
- Compatible with any framework
- AI agent ready
- Project agnostic

### ✅ **Maintainable**
- Clear file structure
- Automated setup
- Standard patterns
- Comprehensive documentation

## 🚀 Getting Started

1. **Use this template** for all new projects
2. **Customize** as needed for your specific requirements
3. **Keep security** by never committing `.env` files
4. **Share safely** with your team members

That's it! You now have a complete, secure development environment that actually works when complex secret managers fail. 🎉

---

**Note**: This template is designed to be simple and reliable. It avoids the complexity of tools like 1Password while maintaining strong security practices through git protection and environment variable management.