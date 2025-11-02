#!/usr/bin/env python3
"""
Working SSH Manager for RelayQ Architecture
Uses the proven SSH connection setup
"""

import os
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, Any, List

def load_ssh_config():
    """Load SSH configuration from .ssh_config"""
    config_path = Path(__file__).parent.parent / ".ssh_config"
    config = {}

    if config_path.exists():
        with open(config_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key] = value.strip('"')

    return config

async def test_ssh_connection(host: str, user: str, key_path: str = None) -> Dict[str, Any]:
    """Test SSH connection with working parameters"""
    try:
        # Build SSH command with working options
        ssh_cmd = ["ssh"]

        # Add key if specified
        if key_path:
            key_path = Path(key_path).expanduser()
            if key_path.exists():
                ssh_cmd.extend(["-i", str(key_path)])

        # Add target and simple test command
        ssh_cmd.extend([f"{user}@{host}", "echo 'SSH connection successful'"])

        # Execute command with longer timeout for first connection
        process = await asyncio.create_subprocess_exec(
            *ssh_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=30  # Longer timeout for first connection
            )

            return {
                "success": process.returncode == 0,
                "stdout": stdout.decode().strip(),
                "stderr": stderr.decode().strip(),
                "returncode": process.returncode
            }
        except asyncio.TimeoutError:
            # Kill the process if it times out
            process.kill()
            return {
                "success": False,
                "error": "SSH connection timeout after 30 seconds"
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

async def test_relayq_nodes():
    """Test all RelayQ node connections"""
    config = load_ssh_config()
    results = {}

    print("🔧 Testing RelayQ SSH Connections")
    print("=" * 50)

    # Test MacMini
    if config.get("MACMINI_IP") and config.get("MACMINI_USER"):
        print(f"\n1. Testing MacMini ({config['MACMINI_IP']}):")

        macmini_result = await test_ssh_connection(
            config["MACMINI_IP"],
            config["MACMINI_USER"],
            config.get("MACMINI_KEY_PATH")
        )

        if macmini_result["success"]:
            print(f"   ✅ MacMini: {macmini_result['stdout']}")
        else:
            print(f"   ❌ MacMini: {macmini_result.get('error', 'Unknown error')}")

        results["macmini"] = macmini_result

    # Test RPi4 (if configured)
    if config.get("RPI4_IP") and config.get("RPI4_USER"):
        print(f"\n2. Testing RPi4 ({config['RPI4_IP']}):")

        rpi4_result = await test_ssh_connection(
            config["RPI4_IP"],
            config["RPI4_USER"],
            config.get("RPI4_KEY_PATH")
        )

        if rpi4_result["success"]:
            print(f"   ✅ RPi4: {rpi4_result['stdout']}")
        else:
            print(f"   ❌ RPi4: {rpi4_result.get('error', 'Unknown error')}")

        results["rpi4"] = rpi4_result
    else:
        print(f"\n2. RPi4: ⚠️  Not configured")

    return results

async def execute_on_node(host: str, user: str, command: str, key_path: str = None) -> Dict[str, Any]:
    """Execute command on remote node"""
    try:
        ssh_cmd = ["ssh"]

        if key_path:
            key_path = Path(key_path).expanduser()
            if key_path.exists():
                ssh_cmd.extend(["-i", str(key_path)])

        ssh_cmd.extend([f"{user}@{host}", command])

        process = await asyncio.create_subprocess_exec(
            *ssh_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=60
        )

        return {
            "success": process.returncode == 0,
            "stdout": stdout.decode().strip(),
            "stderr": stderr.decode().strip(),
            "returncode": process.returncode,
            "command": command,
            "host": host
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "command": command,
            "host": host
        }

if __name__ == "__main__":
    async def main():
        print("🚀 OOS Working SSH Manager")
        print("=" * 50)

        # Load and show configuration
        config = load_ssh_config()
        print(f"Configuration loaded from .ssh_config")
        print(f"MacMini: {config.get('MACMINI_IP', 'Not configured')}")
        print(f"RPi4: {config.get('RPI4_IP', 'Not configured')}")

        # Test connections
        results = await test_relayq_nodes()

        # Summary
        print(f"\n📊 Connection Summary:")
        working_nodes = sum(1 for r in results.values() if r.get("success"))
        total_nodes = len(results)
        print(f"   Working: {working_nodes}/{total_nodes} nodes")

        if working_nodes > 0:
            print(f"\n✅ SSH setup working! Ready for distributed computing")
            print(f"   Run full demo: ./bin/oos-full-stack --test")
        else:
            print(f"\n⚠️  SSH needs configuration")
            print(f"   Check .ssh_config and ensure keys are properly set up")

    asyncio.run(main())