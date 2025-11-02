#!/usr/bin/env python3
"""
Auto-configure RelayQ SSH settings from .env
Makes SSH setup repeatable and automated
"""

import os
import json
import subprocess
from pathlib import Path

def load_env():
    """Load environment variables from .env"""
    env_path = Path(__file__).parent / ".env"
    env_vars = {}

    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value.strip('"')

    return env_vars

def generate_relayq_config():
    """Generate RelayQ configuration from .env variables"""
    env = load_env()

    # Default configuration
    config = {
        "version": "1.0",
        "nodes": [
            {
                "name": "ocivm-dev",
                "node_type": "ocivm",
                "host": "localhost",
                "port": 22,
                "capabilities": ["development", "testing", "api", "orchestration"],
                "status": "online"
            }
        ]
    }

    # Add MacMini if configured
    if env.get("MACMINI_IP"):
        config["nodes"].append({
            "name": "macmini-server",
            "node_type": "macmini",
            "host": env["MACMINI_IP"],
            "port": 22,
            "capabilities": ["compute", "storage", "database", "ai-training"],
            "status": "offline",
            "ssh_config": {
                "user": env.get("MACMINI_USER", "ubuntu"),
                "key_path": env.get("MACMINI_KEY_PATH", "~/.ssh/macmini_key")
            }
        })
        print(f"✅ MacMini configured: {env['MACMINI_IP']}")
    else:
        print("⚠️  MacMini not configured (add MACMINI_IP to .env)")

    # Add RPi4 if configured
    if env.get("RPI4_IP"):
        config["nodes"].append({
            "name": "rpi4-edge-1",
            "node_type": "rpi4",
            "host": env["RPI4_IP"],
            "port": 22,
            "capabilities": ["edge-processing", "iot", "sensor-data", "light-compute"],
            "status": "offline",
            "ssh_config": {
                "user": env.get("RPI4_USER", "pi"),
                "key_path": env.get("RPI4_KEY_PATH", "~/.ssh/rpi4_key")
            }
        })
        print(f"✅ RPi4 configured: {env['RPI4_IP']}")
    else:
        print("⚠️  RPi4 not configured (add RPI4_IP to .env)")

    return config

def save_relayq_config(config):
    """Save RelayQ configuration to file"""
    config_file = Path(__file__).parent / ".relayq_config.json"

    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)

    print(f"📁 Configuration saved to: {config_file}")
    return config_file

def setup_ssh_keys():
    """Generate SSH keys if they don't exist"""
    ssh_dir = Path.home() / ".ssh"
    ssh_dir.mkdir(exist_ok=True, mode=0o700)

    keys_created = []

    # MacMini key
    macmini_key = ssh_dir / "macmini_key"
    if not macmini_key.exists():
        print("🔑 Generating MacMini SSH key...")
        try:
            subprocess.run([
                "ssh-keygen", "-t", "ed25519", "-f", str(macmini_key), "-N", ""
            ], check=True, capture_output=True)
            keys_created.append(str(macmini_key))
            print(f"   ✅ Created: {macmini_key}")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to create MacMini key: {e}")
    else:
        print(f"   ✅ MacMini key exists: {macmini_key}")

    # RPi4 key
    rpi4_key = ssh_dir / "rpi4_key"
    if not rpi4_key.exists():
        print("🔑 Generating RPi4 SSH key...")
        try:
            subprocess.run([
                "ssh-keygen", "-t", "ed25519", "-f", str(rpi4_key), "-N", ""
            ], check=True, capture_output=True)
            keys_created.append(str(rpi4_key))
            print(f"   ✅ Created: {rpi4_key}")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to create RPi4 key: {e}")
    else:
        print(f"   ✅ RPi4 key exists: {rpi4_key}")

    return keys_created

def show_next_steps():
    """Show what to do next"""
    env = load_env()

    print("\n📋 SSH Setup Instructions:")
    print("=" * 50)

    macmini_pub = Path.home() / ".ssh" / "macmini_key.pub"
    rpi4_pub = Path.home() / ".ssh" / "rpi4_key.pub"

    if env.get("MACMINI_IP") and macmini_pub.exists():
        print(f"\n🖥️  MacMini Setup ({env['MACMINI_IP']}):")
        print(f"   User: {env.get('MACMINI_USER', 'ubuntu')}")
        print(f"   Public key to copy:")
        print(f"   {macmini_pub.read_text().strip()}")
        print(f"\n   On MacMini, run:")
        print(f"   mkdir -p ~/.ssh")
        print(f"   echo '{macmini_pub.read_text().strip()}' >> ~/.ssh/authorized_keys")
        print(f"   chmod 600 ~/.ssh/authorized_keys")
        print(f"   chmod 700 ~/.ssh")

    if env.get("RPI4_IP") and rpi4_pub.exists():
        print(f"\n🍓 RPi4 Setup ({env['RPI4_IP']}):")
        print(f"   User: {env.get('RPI4_USER', 'pi')}")
        print(f"   Public key to copy:")
        print(f"   {rpi4_pub.read_text().strip()}")
        print(f"\n   On RPi4, run:")
        print(f"   mkdir -p ~/.ssh")
        print(f"   echo '{rpi4_pub.read_text().strip()}' >> ~/.ssh/authorized_keys")
        print(f"   chmod 600 ~/.ssh/authorized_keys")
        print(f"   chmod 700 ~/.ssh")

    print(f"\n🧪 Test Everything:")
    print(f"   python3 src/ssh_manager.py")
    print(f"   ./bin/oos-full-stack --test")

    print(f"\n💡 Pro Tip:")
    print(f"   This configuration is now repeatable!")
    print(f"   Just update .env and run: python3 configure_ssh.py")

def update_env_template():
    """Add SSH configuration to .env if not present"""
    env_path = Path(__file__).parent / ".env"

    # Check if SSH config already exists
    with open(env_path, 'r') as f:
        env_content = f.read()

    ssh_vars = ["MACMINI_IP", "RPI4_IP", "MACMINI_USER", "RPI4_USER"]
    needs_update = any(var not in env_content for var in ssh_vars)

    if needs_update:
        print(f"\n📝 Adding SSH configuration to .env...")

        with open(env_path, 'a') as f:
            f.write("\n# RelayQ SSH Configuration\n")
            f.write("# Uncomment and configure these for distributed computing\n")
            f.write("# MACMINI_IP=192.168.1.100\n")
            f.write("# RPI4_IP=192.168.1.101\n")
            f.write("# MACMINI_USER=ubuntu\n")
            f.write("# RPI4_USER=pi\n")
            f.write("# MACMINI_KEY_PATH=~/.ssh/macmini_key\n")
            f.write("# RPI4_KEY_PATH=~/.ssh/rpi4_key\n")

        print(f"   ✅ Added SSH variables to .env")
        print(f"   📝 Edit .env to add your actual IP addresses")
    else:
        print(f"   ✅ SSH configuration already in .env")

if __name__ == "__main__":
    print("🔧 OOS RelayQ SSH Configuration")
    print("=" * 50)
    print("This script makes SSH setup repeatable using .env variables")
    print()

    # Update .env with SSH variables
    update_env_template()

    # Setup SSH keys
    setup_ssh_keys()

    # Generate configuration
    config = generate_relayq_config()
    save_relayq_config(config)

    # Show next steps
    show_next_steps()