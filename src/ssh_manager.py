#!/usr/bin/env python3
"""
SSH Manager for RelayQ Architecture
Handles SSH connections, key management, and testing
"""

import os
import subprocess
import asyncio
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SSHConnection:
    host: str
    user: str
    port: int = 22
    key_path: Optional[str] = None
    password: Optional[str] = None
    timeout: int = 10


class SSHManager:
    """Manages SSH connections and key operations"""

    def __init__(self):
        self.known_hosts_file = Path.home() / ".ssh" / "known_hosts"
        self.ssh_dir = Path.home() / ".ssh"
        self.ensure_ssh_directory()

    def ensure_ssh_directory(self):
        """Ensure SSH directory exists with proper permissions"""
        self.ssh_dir.mkdir(exist_ok=True, mode=0o700)

    async def test_connection(self, connection: SSHConnection) -> Dict[str, Any]:
        """Test SSH connection and return detailed status"""
        try:
            cmd = self._build_ssh_command(connection, "echo 'SSH Connection Test Successful'")

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=connection.timeout
            )

            return {
                "success": process.returncode == 0,
                "stdout": stdout.decode().strip(),
                "stderr": stderr.decode().strip(),
                "returncode": process.returncode
            }

        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": f"Connection timeout after {connection.timeout} seconds"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _build_ssh_command(self, connection: SSHConnection, command: str) -> List[str]:
        """Build SSH command with proper options"""
        ssh_cmd = ["ssh"]

        # Connection options
        ssh_cmd.extend([
            "-p", str(connection.port),
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            "-o", "ConnectTimeout=" + str(connection.timeout),
            "-o", "BatchMode=yes"  # Never ask for passwords
        ])

        # Key-based authentication
        if connection.key_path:
            key_path = Path(connection.key_path).expanduser()
            if key_path.exists():
                ssh_cmd.extend(["-i", str(key_path)])
            else:
                logger.warning(f"SSH key not found: {key_path}")

        # Build user@host
        target = f"{connection.user}@{connection.host}"
        ssh_cmd.extend([target, command])

        return ssh_cmd

    async def execute_command(self, connection: SSHConnection, command: str, timeout: int = 30) -> Dict[str, Any]:
        """Execute command on remote host via SSH"""
        try:
            ssh_cmd = self._build_ssh_command(connection, command)

            # Set timeout for this specific execution
            connection.timeout = timeout

            process = await asyncio.create_subprocess_exec(
                *ssh_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )

            return {
                "success": process.returncode == 0,
                "stdout": stdout.decode().strip(),
                "stderr": stderr.decode().strip(),
                "returncode": process.returncode,
                "command": command,
                "host": connection.host
            }

        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": f"Command timeout after {timeout} seconds",
                "command": command,
                "host": connection.host
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "command": command,
                "host": connection.host
            }

    def generate_ssh_key(self, key_name: str, key_type: str = "ed25519") -> str:
        """Generate SSH key pair"""
        key_path = self.ssh_dir / key_name

        if key_path.exists():
            logger.info(f"SSH key already exists: {key_path}")
            return str(key_path)

        try:
            # Generate new key
            subprocess.run([
                "ssh-keygen",
                "-t", key_type,
                "-f", str(key_path),
                "-N", ""  # No passphrase
            ], check=True, capture_output=True)

            # Set proper permissions
            key_path.chmod(0o600)
            key_path.with_suffix(f"{key_path.suffix}.pub").chmod(0o644)

            logger.info(f"Generated SSH key: {key_path}")
            return str(key_path)

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to generate SSH key: {e}")
            raise

    def get_public_key(self, key_path: str) -> str:
        """Get public key content"""
        key_path = Path(key_path).expanduser()
        pub_key_path = key_path.with_suffix(f"{key_path.suffix}.pub")

        if pub_key_path.exists():
            return pub_key_path.read_text().strip()
        else:
            raise FileNotFoundError(f"Public key not found: {pub_key_path}")

    async def setup_ssh_key_copy(self, connection: SSHConnection, key_name: str) -> Dict[str, Any]:
        """Setup and copy SSH key to remote host"""
        try:
            # Generate key if doesn't exist
            key_path = self.generate_ssh_key(key_name)
            connection.key_path = key_path

            # Get public key
            public_key = self.get_public_key(key_path)

            # Test connection first
            test_result = await self.test_connection(connection)

            if test_result["success"]:
                return {
                    "success": True,
                    "message": "SSH connection already working",
                    "key_path": key_path,
                    "public_key": public_key
                }

            # Try to copy public key using ssh-copy-id if available
            try:
                copy_cmd = [
                    "ssh-copy-id",
                    "-i", f"{key_path}.pub",
                    "-p", str(connection.port),
                    "-o", "StrictHostKeyChecking=no",
                    f"{connection.user}@{connection.host}"
                ]

                process = await asyncio.create_subprocess_exec(
                    *copy_cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )

                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=30
                )

                if process.returncode == 0:
                    # Test connection after key copy
                    test_result = await self.test_connection(connection)

                    return {
                        "success": test_result["success"],
                        "message": "SSH key copied successfully" if test_result["success"] else "Key copied but connection still failed",
                        "key_path": key_path,
                        "public_key": public_key,
                        "test_result": test_result
                    }
                else:
                    return {
                        "success": False,
                        "error": f"ssh-copy-id failed: {stderr.decode()}",
                        "key_path": key_path,
                        "public_key": public_key,
                        "manual_copy_required": True,
                        "manual_copy_command": f'echo "{public_key}" | ssh -p {connection.port} {connection.user}@{connection.host} "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"'
                    }

            except FileNotFoundError:
                return {
                    "success": False,
                    "error": "ssh-copy-id not available",
                    "key_path": key_path,
                    "public_key": public_key,
                    "manual_copy_required": True,
                    "manual_copy_command": f'echo "{public_key}" | ssh -p {connection.port} {connection.user}@{connection.host} "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"'
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def discover_local_nodes(self) -> List[str]:
        """Discover potential local network nodes"""
        potential_ips = []

        # Get local network range (simplified)
        try:
            # Get hostname and try to infer local network
            result = subprocess.run(
                ["hostname", "-I"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                local_ips = result.stdout.strip().split()
                for ip in local_ips:
                    if "." in ip and not ip.startswith("127."):
                        # Simple network inference (e.g., 192.168.1.x)
                        parts = ip.split(".")
                        if len(parts) == 4:
                            network = ".".join(parts[:3])
                            for i in range(1, 255):
                                potential_ips.append(f"{network}.{i}")

        except Exception as e:
            logger.warning(f"Could not discover local network: {e}")

        return potential_ips[:20]  # Limit to first 20 potential IPs


# Global SSH manager
_ssh_manager = None


def get_ssh_manager() -> SSHManager:
    """Get or create global SSH manager"""
    global _ssh_manager
    if _ssh_manager is None:
        _ssh_manager = SSHManager()
    return _ssh_manager


async def test_relayq_ssh_connections() -> Dict[str, Any]:
    """Test SSH connections for all configured RelayQ nodes"""
    from relayq_architecture import get_relayq_manager

    relayq_manager = get_relayq_manager()
    ssh_manager = get_ssh_manager()

    results = {}

    for node_name, node in relayq_manager.nodes.items():
        if node.node_type.value == "ocivm":
            # Skip local node
            results[node_name] = {
                "success": True,
                "message": "Local ocivm node (no SSH needed)"
            }
            continue

        if not node.ssh_config:
            results[node_name] = {
                "success": False,
                "error": "No SSH configuration found"
            }
            continue

        # Create SSH connection
        connection = SSHConnection(
            host=node.host,
            user=node.ssh_config.get("user", "ubuntu"),
            port=node.port,
            key_path=node.ssh_config.get("key_path"),
            timeout=5
        )

        # Test connection
        test_result = await ssh_manager.test_connection(connection)
        results[node_name] = test_result

        if test_result["success"]:
            node.status = "online"
        else:
            node.status = "offline"

    return results


if __name__ == "__main__":
    async def test_ssh_setup():
        print("🔑 SSH Manager Test")
        print("=" * 40)

        ssh_manager = get_ssh_manager()

        # Test 1: Generate test key
        print("\n1. Testing SSH key generation...")
        try:
            key_path = ssh_manager.generate_ssh_key("test_key")
            print(f"   ✅ Generated: {key_path}")

            public_key = ssh_manager.get_public_key(key_path)
            print(f"   📄 Public key: {public_key[:50]}...")

        except Exception as e:
            print(f"   ❌ Key generation failed: {e}")

        # Test 2: Test RelayQ connections
        print("\n2. Testing RelayQ SSH connections...")
        results = await test_relayq_ssh_connections()

        for node_name, result in results.items():
            status = "✅" if result.get("success") else "❌"
            message = result.get("message", result.get("error", "No message"))
            print(f"   {node_name}: {status} {message}")

        print("\n🔧 SSH Setup Tips:")
        print("   1. Generate keys: ssh-keygen -t ed25519 -f ~/.ssh/node_key")
        print("   2. Copy to remote: ssh-copy-id -i ~/.ssh/node_key.pub user@host")
        print("   3. Update .relayq_config.json with correct IPs and key paths")
        print("   4. Test with: python3 src/ssh_manager.py")

    asyncio.run(test_ssh_setup())