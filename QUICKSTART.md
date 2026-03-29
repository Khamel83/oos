# Start Using OOS (5 Minutes)

## Install OOS

```bash
# Install in existing project
cd ~/your-project
curl -fsSL https://raw.githubusercontent.com/Khamel83/oos/master/install.sh | bash

# OR clone OOS repository
git clone https://github.com/Khamel83/oos
cd oos
./install.sh
```

## Setup Environment

```bash
oos dev setup
```

This installs dependencies and creates necessary directories.

## Create Your First Task

```bash
oos task create "Build authentication system"
oos task list
```

## Start Working

```bash
# Get your task ID from the list above
oos task start abc123

# Do your work...

# Mark it done
oos task done abc123
```

## Check What You Have

```bash
oos status
```

Shows which features are available (Core/Enhanced/Advanced).

## Done. You're Using OOS.

**Next steps:**
- Run `oos help` to see all commands
- Run `oos help setup` to enable AI features (optional)
- Check [USAGE.md](USAGE.md) for common tasks

---

**That's it. 5 minutes. You're productive.**
