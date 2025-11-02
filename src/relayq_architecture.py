#!/usr/bin/env python3
"""
OOS RelayQ Architecture Integration
Distributed computing architecture with MacMini, RPi4, and ocivm nodes
"""

import asyncio
import json
import logging
import os
import socket
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NodeType(Enum):
    MAC_MINI = "macmini"      # Heavy compute, storage server
    RPI4 = "rpi4"             # Edge processing, IoT tasks
    OCIVM = "ocivm"           # Main development machine (current)


class NodeStatus(Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    ERROR = "error"


@dataclass
class Node:
    name: str
    node_type: NodeType
    host: str
    port: int
    capabilities: list[str]
    status: NodeStatus = NodeStatus.OFFLINE
    load: float = 0.0
    last_ping: float = 0.0
    ssh_config: dict[str, Any] | None = None


@dataclass
class DeploymentTask:
    task_id: str
    command: str
    target_nodes: list[str]
    priority: int = 1
    timeout: int = 300
    distributed: bool = False
    requirements: list[str] | None = None


class RelayQManager:
    """Manages the distributed RelayQ architecture"""

    def __init__(self, config_file: str = ".relayq_config.json"):
        self.config_file = Path(config_file)
        self.nodes: dict[str, Node] = {}
        self.current_node = None
        self.load_config()

    def load_config(self):
        """Load RelayQ configuration from file"""
        if self.config_file.exists():
            with open(self.config_file) as f:
                config = json.load(f)

            # Load nodes
            for node_data in config.get("nodes", []):
                # Convert string values back to enums
                node_data['node_type'] = NodeType(node_data['node_type'])
                node_data['status'] = NodeStatus(node_data['status'])
                node = Node(**node_data)
                self.nodes[node.name] = node

            logger.info(f"Loaded {len(self.nodes)} nodes from {self.config_file}")
        else:
            # Create default configuration
            self.create_default_config()

    def create_default_config(self):
        """Create default RelayQ configuration"""
        default_nodes = [
            Node(
                name="macmini-server",
                node_type=NodeType.MAC_MINI,
                host="192.168.1.100",  # Example IP
                port=22,
                capabilities=["compute", "storage", "database", "ai-training"],
                ssh_config={"user": "ubuntu", "key_path": "~/.ssh/macmini_key"}
            ),
            Node(
                name="rpi4-edge-1",
                node_type=NodeType.RPI4,
                host="192.168.1.101",  # Example IP
                port=22,
                capabilities=["edge-processing", "iot", "sensor-data", "light-compute"],
                ssh_config={"user": "pi", "key_path": "~/.ssh/rpi4_key"}
            ),
            Node(
                name="ocivm-dev",
                node_type=NodeType.OCIVM,
                host="localhost",
                port=22,
                capabilities=["development", "testing", "api", "orchestration"],
                status=NodeStatus.ONLINE
            )
        ]

        for node in default_nodes:
            self.nodes[node.name] = node

        # Save configuration
        self.save_config()
        logger.info("Created default RelayQ configuration")

    def save_config(self):
        """Save RelayQ configuration to file"""
        def node_to_dict(node):
            node_dict = asdict(node)
            node_dict['node_type'] = node.node_type.value
            node_dict['status'] = node.status.value
            return node_dict

        config = {
            "nodes": [node_to_dict(node) for node in self.nodes.values()],
            "current_node": self.current_node,
            "version": "1.0"
        }

        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)

    async def ping_node(self, node_name: str) -> bool:
        """Check if a node is reachable"""
        node = self.nodes.get(node_name)
        if not node:
            return False

        try:
            # Try to connect to SSH port
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((node.host, node.port))
            sock.close()

            is_online = result == 0
            node.status = NodeStatus.ONLINE if is_online else NodeStatus.OFFLINE
            return is_online

        except Exception as e:
            logger.warning(f"Failed to ping node {node_name}: {e}")
            node.status = NodeStatus.ERROR
            return False

    async def health_check_all(self) -> dict[str, bool]:
        """Check health of all nodes"""
        results = {}
        for node_name in self.nodes:
            results[node_name] = await self.ping_node(node_name)
        return results

    def get_nodes_by_type(self, node_type: NodeType) -> list[Node]:
        """Get all nodes of a specific type"""
        return [node for node in self.nodes.values() if node.node_type == node_type]

    def get_available_nodes(self) -> list[Node]:
        """Get all online and available nodes"""
        return [node for node in self.nodes.values() if node.status == NodeStatus.ONLINE]

    def select_best_node(self, task_requirements: list[str]) -> Node | None:
        """Select the best node for a task based on requirements"""
        available_nodes = self.get_available_nodes()

        # Score nodes based on capability match and load
        best_node = None
        best_score = -1

        for node in available_nodes:
            score = 0

            # Check capability match
            for req in task_requirements:
                if req in node.capabilities:
                    score += 10

            # Prefer less loaded nodes
            score += (1.0 - node.load) * 5

            # Prefer certain node types for specific tasks
            if "ai-training" in task_requirements and node.node_type == NodeType.MAC_MINI or "edge-processing" in task_requirements and node.node_type == NodeType.RPI4 or "development" in task_requirements and node.node_type == NodeType.OCIVM:
                score += 20

            if score > best_score:
                best_score = score
                best_node = node

        return best_node

    async def execute_on_node(self, node_name: str, command: str, timeout: int = 300) -> dict[str, Any]:
        """Execute a command on a remote node via SSH"""
        node = self.nodes.get(node_name)
        if not node:
            return {"success": False, "error": f"Node {node_name} not found"}

        if node.status != NodeStatus.ONLINE:
            return {"success": False, "error": f"Node {node_name} is not online"}

        try:
            # Build SSH command
            ssh_cmd = ["ssh"]

            if node.ssh_config:
                if "user" in node.ssh_config:
                    ssh_cmd.append(f"{node.ssh_config['user']}@{node.host}")
                if "key_path" in node.ssh_config:
                    ssh_cmd.extend(["-i", os.path.expanduser(node.ssh_config["key_path"])])
            else:
                ssh_cmd.append(f"ubuntu@{node.host}")

            ssh_cmd.extend(["-p", str(node.port)])
            ssh_cmd.append(command)

            # Execute command
            process = await asyncio.create_subprocess_exec(
                *ssh_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)

            return {
                "success": process.returncode == 0,
                "stdout": stdout.decode().strip(),
                "stderr": stderr.decode().strip(),
                "returncode": process.returncode
            }

        except TimeoutError:
            return {"success": False, "error": f"Command timed out after {timeout} seconds"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def deploy_task(self, task: DeploymentTask) -> dict[str, Any]:
        """Deploy a task to the best available node(s)"""
        results = {}

        if task.distributed and len(task.target_nodes) > 1:
            # Distributed deployment
            tasks = []
            for node_name in task.target_nodes:
                if node_name in self.nodes and self.nodes[node_name].status == NodeStatus.ONLINE:
                    tasks.append(self.execute_on_node(node_name, task.command, task.timeout))

            if tasks:
                distributed_results = await asyncio.gather(*tasks, return_exceptions=True)
                for i, result in enumerate(distributed_results):
                    node_name = task.target_nodes[i]
                    if isinstance(result, Exception):
                        results[node_name] = {"success": False, "error": str(result)}
                    else:
                        results[node_name] = result
            else:
                return {"success": False, "error": "No online nodes available for distributed deployment"}
        else:
            # Single node deployment
            if task.target_nodes:
                target_node = task.target_nodes[0]
                if target_node in self.nodes:
                    result = await self.execute_on_node(target_node, task.command, task.timeout)
                    results[target_node] = result
                else:
                    return {"success": False, "error": f"Target node {target_node} not found"}
            else:
                # Auto-select best node
                best_node = self.select_best_node(task.requirements or [])
                if best_node:
                    result = await self.execute_on_node(best_node.name, task.command, task.timeout)
                    results[best_node.name] = result
                else:
                    return {"success": False, "error": "No suitable node found"}

        return {
            "success": any(r.get("success", False) for r in results.values()),
            "results": results,
            "task_id": task.task_id
        }

    def get_topology_summary(self) -> dict[str, Any]:
        """Get a summary of the RelayQ topology"""
        summary = {
            "total_nodes": len(self.nodes),
            "nodes_by_type": {},
            "online_nodes": len(self.get_available_nodes()),
            "node_details": []
        }

        for node_type in NodeType:
            nodes = self.get_nodes_by_type(node_type)
            summary["nodes_by_type"][node_type.value] = {
                "count": len(nodes),
                "online": len([n for n in nodes if n.status == NodeStatus.ONLINE])
            }

        for node in self.nodes.values():
            summary["node_details"].append({
                "name": node.name,
                "type": node.node_type.value,
                "host": node.host,
                "status": node.status.value,
                "capabilities": node.capabilities
            })

        return summary


# Global RelayQ manager
_relayq_manager = None


def get_relayq_manager() -> RelayQManager:
    """Get or create global RelayQ manager"""
    global _relayq_manager
    if _relayq_manager is None:
        _relayq_manager = RelayQManager()
    return _relayq_manager


if __name__ == "__main__":
    # Test RelayQ functionality
    async def test_relayq():
        print("🏗️ Testing RelayQ Architecture...")

        manager = get_relayq_manager()

        # Show topology
        print("\n1. RelayQ Topology:")
        summary = manager.get_topology_summary()
        print(f"   Total nodes: {summary['total_nodes']}")
        print(f"   Online nodes: {summary['online_nodes']}")
        for node_type, info in summary["nodes_by_type"].items():
            print(f"   {node_type}: {info['online']}/{info['count']} online")

        # Health check
        print("\n2. Node Health Check:")
        health = await manager.health_check_all()
        for node_name, is_online in health.items():
            status = "✅" if is_online else "❌"
            print(f"   {node_name}: {status}")

        # Test task deployment
        print("\n3. Test Task Deployment:")
        test_task = DeploymentTask(
            task_id="test-001",
            command="echo 'Hello from RelayQ node!' && date",
            target_nodes=["ocivm-dev"],  # Use local node for testing
            requirements=["development"]
        )

        result = await manager.deploy_task(test_task)
        if result["success"]:
            print("   ✅ Task deployed successfully")
            for node, node_result in result["results"].items():
                if node_result["success"]:
                    print(f"   {node}: {node_result['stdout']}")
        else:
            print(f"   ❌ Task deployment failed: {result.get('error', 'Unknown error')}")

        print("\n✅ RelayQ architecture test completed!")

    asyncio.run(test_relayq())
