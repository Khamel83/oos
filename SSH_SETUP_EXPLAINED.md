#!/usr/bin/env python3
"""
Auto-configure RelayQ SSH settings from .env
Makes SSH setup repeatable and automated
"""

import os
import json
from pathlib import Path

def load_env():
    """Load environment variables from .env"""
    env_path = Path(__file__).parent.parent / ".env"
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
            "status": "offline",  # Will be updated by health checks
            "ssh_config": {
                "user": env.get("MACMINI_USER", "ubuntu"),
                "key_path": env.get("MACMINI_KEY_PATH", "~/.ssh/macmini_key")
            }
        })
        print(f"✅ MacMini configured: {env['MACMINI_IP']}")
    else:
        print("⚠️  MacMini not configured (no MACMINI_IP in .env)")

    # Add RPi4 if configured
    if env.get("RPI4_IP"):
        config["nodes"].append({
            "name": "rpi4-edge-1",
            "node_type": "rpi4",
            "host": env["RPI4_IP"],
            "port": 22,
            "capabilities": ["edge-processing", "iot", "sensor-data", "light-compute"],
            "status": "offline",  # Will be updated by health checks
            "ssh_config": {
                "user": env.get("RPI4_USER", "pi"),
                "key_path": env.get("RPI4_KEY_PATH", "~/.ssh/rpi4_key")
            }
        })
        print(f"✅ RPi4 configured: {env['RPI4_IP']}")
    else:
        print("⚠️  RPi4 not configured (no RPI4_IP in .env)")

    return config

def save_relayq_config(config):
    """Save RelayQ configuration to file"""
    config_file = Path(__file__).parent.parent / ".relayq_config.json"

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
        import subprocess
        subprocess.run([
            "ssh-keygen", "-t", "ed25519", "-f", str(macmini_key), "-N", ""
        ], check=True, capture_output=True)
        keys_created.append(str(macmini_key))
        print(f"   ✅ Created: {macmini_key}")
    else:
        print(f"   ✅ MacMini key exists: {macmini_key}")

    # RPi4 key
    rpi4_key = ssh_dir / "rpi4_key"
    if not rpi4_key.exists():
        print("🔑 Generating RPi4 SSH key...")
        import subprocess
        subprocess.run([
            "ssh-keygen", "-t", "ed25519", "-f", str(rpi4_key), "-N", ""
        ], check=True, capture_output=True)
        keys_created.append(str(rpi4_key))
        print(f"   ✅ Created: {rpi4_key}")
    else:
        print(f"   ✅ RPi4 key exists: {rpi4_key}")

    return keys_created

def show_next_steps():
    """Show what to do next"""
    env = load_env()

    print("\n📋 Next Steps:")
    print("=" * 50)

    if env.get("MACMINI_IP"):
        print(f"\n1️⃣  MacMini Setup ({env['MACMINI_IP']}):")
        print("   # Copy this public key to MacMini:")

        macmini_pub = Path.home() / ".ssh" / "macmini_key.pub"
        if macmini_pub.exists():
            print(f"   {macmini_pub.read_text().strip()}")

        print(f"\n   # On MacMini, run:")
        print(f"   echo 'ssh-ed25519 ...' >> ~/.ssh/authorized_keys")
        print(f"   chmod 600 ~/.ssh/authorized_keys")

    if env.get("RPI4_IP"):
        print(f"\n2️⃣  RPi4 Setup ({env['RPI4_IP']}):")
        print("   # Copy this public key to RPi4:")

        rpi4_pub = Path.home() / ".ssh" / "rpi4_key.pub"
        if rpi4_pub.exists():
            print(f"   {rpi4_pub.read_text().strip()}")

        print(f"\n   # On RPi4, run:")
        print(f"   echo 'ssh-ed25519 ...' >> ~/.ssh/authorized_keys")
        print(f"   chmod 600 ~/.ssh/authorized_keys")

    print(f"\n3️⃣  Test Connections:")
    print("   python3 src/ssh_manager.py")
    print("   ./bin/oos-full-stack --test")

    print(f"\n💡 Tip: Your configuration is now repeatable!")
    print("   Just run this script again after changing .env")

if __name__ == "__main__":
    print("🔧 OOS RelayQ SSH Configuration")
    print("=" * 50)
    print("This script configures SSH for distributed computing")
    print("using settings from your .env file\n")

    # Setup SSH keys
    setup_ssh_keys()

    # Generate configuration
    config = generate_relayq_config()
    save_relayq_config(config)

    # Show next steps
    show_next_steps()