# SSH Setup - Step by Step Instructions

## 🎯 The Goal
Set up SSH so your **ocivm** (current machine) can communicate with **MacMini** and **RPi4** for distributed computing.

## 🏗️ Architecture Overview
```
Your Network:
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   MacMini    │    │     RPi4    │    │   ocivm     │
│ 192.168.1.x │    │ 192.168.1.x │    │  (current)  │
│ Heavy compute│    │ Edge tasks   │    │ Development │
└─────────────┘    └─────────────┘    └─────────────┘
```

## 📋 Step-by-Step Instructions

### Step 1: Find Your Machine IPs
**On each machine, run:**
```bash
# Find the IP address
hostname -I
# OR
ip addr show | grep 'inet 192.168'
```

### Step 2: Configure .env (on ocivm)
**Edit your `.env` file:**
```bash
nano .env
```

**Add the actual IPs:**
```bash
# RelayQ SSH Configuration
MACMINI_IP=192.168.1.100        # Replace with actual MacMini IP
RPI4_IP=192.168.1.101          # Replace with actual RPi4 IP
MACMINI_USER=ubuntu             # Username on MacMini
RPI4_USER=pi                    # Username on RPi4
MACMINI_KEY_PATH=~/.ssh/macmini_key
RPI4_KEY_PATH=~/.ssh/rpi4_key
```

### Step 3: Generate Configuration (on ocivm)
```bash
python3 configure_ssh.py
```

This will:
- ✅ Generate SSH keys automatically
- ✅ Create `.relayq_config.json` with your settings
- ✅ Show you the public keys to copy

### Step 4: Copy SSH Keys to Remote Machines

**For MacMini:**
1. **On ocivm (current machine)** - get the public key:
```bash
cat ~/.ssh/macmini_key.pub
```

2. **On MacMini** - add the key:
```bash
# Create SSH directory if it doesn't exist
mkdir -p ~/.ssh

# Add the public key (paste the key from ocivm)
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAA..." >> ~/.ssh/authorized_keys

# Set correct permissions
chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh
```

**For RPi4:**
1. **On ocivm (current machine)** - get the public key:
```bash
cat ~/.ssh/rpi4_key.pub
```

2. **On RPi4** - add the key:
```bash
# Create SSH directory if it doesn't exist
mkdir -p ~/.ssh

# Add the public key (paste the key from ocivm)
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAA..." >> ~/.ssh/authorized_keys

# Set correct permissions
chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh
```

### Step 5: Test Everything
```bash
# Test SSH connections
python3 src/ssh_manager.py

# Test full stack
./bin/oos-full-stack --test
```

## 🔧 What Each Machine Does

### **ocivm (Current Machine - Oracle VM)**
- **Role**: Development, orchestration, API
- **Setup**: Already configured, no SSH needed
- **Commands**: Run all OOS commands here

### **MacMini (Heavy Compute)**
- **Role**: AI training, storage, database operations
- **Requirements**:
  - SSH server enabled (`sudo systemctl enable ssh`)
  - Ubuntu user with sudo access
  - IP accessible from ocivm

### **RPi4 (Edge Computing)**
- **Role**: IoT tasks, sensor processing, light compute
- **Requirements**:
  - SSH server enabled (`sudo systemctl enable ssh`)
  - Pi user with sudo access
  - IP accessible from ocivm

## 🚀 Quick Test Commands

**Test connection to MacMini:**
```bash
ssh -i ~/.ssh/macmini_key ubuntu@MACMINI_IP "echo 'MacMini SSH works!'"
```

**Test connection to RPi4:**
```bash
ssh -i ~/.ssh/rpi4_key pi@RPI4_IP "echo 'RPi4 SSH works!'"
```

## 🔄 Making It Repeatable

**The beauty of this setup:**

1. **All configuration in .env** - No manual file editing
2. **Automatic key generation** - No manual ssh-keygen
3. **One-command setup** - `python3 configure_ssh.py`
4. **Persistent configuration** - Settings saved in `.relayq_config.json`

**If you need to change IPs:**
```bash
# 1. Edit .env with new IPs
nano .env

# 2. Regenerate configuration
python3 configure_ssh.py

# 3. Copy new keys to machines (if needed)
```

## ⚠️ Common Issues & Solutions

### **SSH Permission Denied**
```bash
# On remote machine, check permissions:
ls -la ~/.ssh/
# Should be:
# -rw-------  authorized_keys
# drwx------  .ssh/

# Fix permissions:
chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh/
```

### **SSH Connection Refused**
```bash
# On remote machine, enable SSH:
sudo systemctl enable ssh
sudo systemctl start ssh
sudo systemctl status ssh
```

### **Firewall Issues**
```bash
# On remote machines, allow SSH:
sudo ufw allow ssh
# OR
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
```

## 🎯 What You Get When Complete

- **Distributed task execution** across 3 machines
- **Intelligent load balancing** based on node capabilities
- **Automatic failover** if nodes go offline
- **Full stack AI + RelayQ + Archon** integration

## 📞 Need Help?

1. **Check the output** of `python3 configure_ssh.py` - it tells you exactly what to do
2. **Test SSH manually** before running full OOS commands
3. **Start with one machine** (MacMini) before adding RPi4

**Remember**: The core OOS functionality works perfectly without SSH. SSH is only for distributed computing across multiple machines.