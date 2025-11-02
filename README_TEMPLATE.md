# 🚀 [Your Project Name]

> **Simple, Secure Development - No Complex Interfaces**

## 🎯 Quick Start

This project uses a simple, secure secrets management system that works when complex tools like 1Password fail.

### 1. **Clone & Setup**
```bash
git clone https://github.com/YOUR_USERNAME/your-repo.git
cd your-repo
./bin/setup-simple-security.sh
```

### 2. **Add Your Secrets**
```bash
nano .env
# Add your API keys here
```

### 3. **Test & Run**
```bash
python3 bin/get-secrets.py list
# Now run your application
```

## 🔐 Security Features

- ✅ **No API key exposure** - `.env` never committed
- ✅ **Git protection** - Pre-commit hooks block secrets
- ✅ **AI agent ready** - Simple Python secrets client
- ✅ **Zero complexity** - Just edit a text file

## 📋 What You Get

### 🔑 **Simple Secrets Management**
- Edit `.env` file to add API keys
- Use environment variables in code
- Automatic loading with `python-dotenv`

### 🛡️ **Automatic Security**
- Pre-commit hooks prevent secret commits
- Git protection with `.gitignore`
- Masked secret display in logs

### 🤖 **AI Agent Integration**
```python
from get_secrets import SimpleSecrets

secrets = SimpleSecrets()
api_key = secrets.get('OPENROUTER_API_KEY')
```

## 🚀 Usage Examples

### Web Applications
```python
from flask import Flask
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.config['API_KEY'] = os.getenv('OPENROUTER_API_KEY')
```

### CLI Tools
```bash
python3 bin/get-secrets.py get OPENROUTER_API_KEY
```

### AI Agents
```python
import sys
sys.path.append('bin')
from get_secrets import SimpleSecrets

agent = SimpleSecrets()
```

## 📁 Project Structure

```
your-repo/
├── .env                 # Your secrets (gitignored)
├── .gitignore          # Security protection
├── bin/
│   ├── setup-simple-security.sh  # Install security system
│   ├── setup-new-project.sh      # Copy secrets to new projects
│   └── get-secrets.py            # AI secrets client
├── src/                # Your source code
└── tests/              # Your tests
```

## 🔧 Available Commands

```bash
# Security setup
./bin/setup-simple-security.sh

# Secrets access
python3 bin/get-secrets.py list
python3 bin/get-secrets.py get KEY_NAME

# Project setup
./bin/setup-new-project.sh /path/to/new/project
```

## ⚙️ Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
# Required
OPENROUTER_API_KEY=""
OPENAI_API_KEY=""

# Optional
DEBUG=false
LOG_LEVEL="info"
```

## 🛡️ Security Rules

- **Never** commit `.env` files
- **Never** hardcode API keys in code
- **Always** use environment variables
- **Test** with `python3 bin/get-secrets.py list`

## 🎯 Why This Approach?

- **Simple** - Edit text files, no complex interfaces
- **Secure** - Git protection, pre-commit hooks
- **Reliable** - Works when complex tools fail
- **Fast** - 5-minute setup time

That's it! Simple, secure development that actually works. 🎉

## 📚 Documentation

- [Detailed Setup Guide](docs/setup.md)
- [API Reference](docs/api.md)
- [Security Guide](docs/security.md)