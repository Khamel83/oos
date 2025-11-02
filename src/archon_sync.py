#!/usr/bin/env python3
"""
OOS Archon Synchronization System
Syncs OOS state, tasks, and data to Archon Supabase backend
"""

import os
import json
import asyncio
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
import logging
import httpx

# Load environment variables
def load_env():
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value.strip('"')

load_env()

# Try to import supabase, but provide fallback
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("Warning: Supabase library not available. Using HTTP API fallback.")

import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SyncStatus:
    last_sync: Optional[datetime] = None
    sync_count: int = 0
    error_count: int = 0
    last_error: Optional[str] = None
    enabled: bool = True


@dataclass
class ArchonProjectState:
    project_id: str
    oos_version: str
    node_count: int
    tasks_active: int
    tasks_completed: int
    ai_requests_today: int
    last_activity: datetime
    system_health: Dict[str, Any]


class ArchonSyncManager:
    """Manages synchronization with Archon Supabase backend"""

    def __init__(self):
        self.archon_url = os.getenv('ARCHON_URL', 'https://archon.khamel.com')
        self.project_id = os.getenv('ARCHON_PROJECT_ID')
        self.api_url = os.getenv('ARCHON_API_URL', 'https://archon.khamel.com/api')
        self.vault_password = os.getenv('ARCHON_VAULT_PASSWORD')

        self.sync_status = SyncStatus()
        self.client: Optional[Client] = None

        if not self.project_id:
            logger.warning("No ARCHON_PROJECT_ID configured. Sync will be disabled.")
            self.sync_status.enabled = False
        else:
            self._initialize_client()

    def _initialize_client(self):
        """Initialize Supabase client"""
        if SUPABASE_AVAILABLE:
            try:
                # For now, we'll use direct HTTP API since Supabase requires specific credentials
                self.client = None
                logger.info("Initialized Archon API sync manager")
            except Exception as e:
                logger.warning(f"Failed to initialize Supabase client: {e}")
        else:
            logger.info("Using HTTP API for Archon sync")

    async def sync_task_state(self, tasks: List[Dict[str, Any]]) -> bool:
        """Sync local task state to Archon"""
        if not self.sync_status.enabled:
            logger.debug("Sync disabled, skipping task sync")
            return True

        try:
            # Get existing tasks from Archon
            existing_tasks = await self._get_archon_tasks()
            existing_task_map = {task.get('title'): task for task in existing_tasks}

            # Sync each task
            for task in tasks:
                task_title = task.get('title', 'Untitled Task')
                existing_task = existing_task_map.get(task_title)

                if existing_task:
                    # Update existing task
                    await self._update_archon_task(existing_task['id'], task)
                else:
                    # Create new task
                    await self._create_archon_task(task)

            logger.info(f"Synced {len(tasks)} tasks to Archon")
            return True

        except Exception as e:
            logger.error(f"Failed to sync tasks to Archon: {e}")
            self.sync_status.error_count += 1
            self.sync_status.last_error = str(e)
            return False

    async def sync_system_state(self, state: ArchonProjectState) -> bool:
        """Sync system state to Archon knowledge base"""
        if not self.sync_status.enabled:
            logger.debug("Sync disabled, skipping state sync")
            return True

        try:
            # Create knowledge base entry with system state
            knowledge_entry = {
                "title": f"OOS System State - {datetime.now().isoformat()}",
                "content": json.dumps(asdict(state), indent=2, default=str),
                "document_type": "system_state",
                "metadata": {
                    "source": "oos_sync",
                    "project_id": self.project_id,
                    "timestamp": datetime.now().isoformat()
                }
            }

            await self._upload_to_knowledge_base(knowledge_entry)
            logger.info("Synced system state to Archon knowledge base")
            return True

        except Exception as e:
            logger.error(f"Failed to sync system state to Archon: {e}")
            self.sync_status.error_count += 1
            self.sync_status.last_error = str(e)
            return False

    async def sync_heartbeat(self) -> bool:
        """Send heartbeat to keep Archon project active"""
        if not self.sync_status.enabled:
            return True

        try:
            heartbeat_data = {
                "project_id": self.project_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "active",
                "service": "oos"
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/heartbeat",
                    json=heartbeat_data,
                    timeout=10.0
                )
                response.raise_for_status()

            logger.debug("Sent heartbeat to Archon")
            return True

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.debug("Heartbeat endpoint not available (404) - skipping")
                return True  # Heartbeat is optional
            else:
                logger.warning(f"Heartbeat HTTP error: {e}")
                return False
        except Exception as e:
            logger.warning(f"Heartbeat failed: {e}")
            return False

    async def _get_archon_tasks(self) -> List[Dict[str, Any]]:
        """Get tasks from Archon project"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_url}/tasks",
                    params={"project_id": self.project_id},
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()
                return data.get('tasks', [])

        except Exception as e:
            logger.error(f"Failed to get Archon tasks: {e}")
            return []

    async def _create_archon_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new task in Archon"""
        task_data = {
            "project_id": self.project_id,
            "title": task.get('title', 'Untitled Task'),
            "description": task.get('description', ''),
            "status": task.get('status', 'todo'),
            "priority": task.get('priority', 'medium'),
            "metadata": {
                "source": "oos_sync",
                "oos_task_id": task.get('id'),
                "tags": task.get('tags', [])
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/tasks",
                json=task_data,
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()

    async def _update_archon_task(self, task_id: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing task in Archon"""
        update_data = {
            "status": task.get('status'),
            "description": task.get('description'),
            "metadata": {
                "source": "oos_sync",
                "oos_task_id": task.get('id'),
                "tags": task.get('tags', []),
                "last_updated": datetime.now().isoformat()
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{self.api_url}/tasks/{task_id}",
                json=update_data,
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()

    async def _upload_to_knowledge_base(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """Upload document to Archon knowledge base"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/knowledge/upload",
                    json=entry,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.debug("Knowledge upload endpoint not available (404) - skipping")
                return {"success": True, "message": "Knowledge upload skipped (endpoint not available)"}
            else:
                raise
        except Exception as e:
            logger.error(f"Failed to upload to knowledge base: {e}")
            raise

    async def full_sync(self, oos_state: Dict[str, Any]) -> Dict[str, Any]:
        """Perform full synchronization with Archon"""
        start_time = time.time()
        sync_results = {
            "success": True,
            "synced_tasks": 0,
            "synced_state": False,
            "heartbeat_sent": False,
            "duration": 0,
            "errors": []
        }

        try:
            # Sync tasks
            if 'tasks' in oos_state:
                if await self.sync_task_state(oos_state['tasks']):
                    sync_results["synced_tasks"] = len(oos_state['tasks'])
                else:
                    sync_results["success"] = False
                    sync_results["errors"].append("Task sync failed")

            # Sync system state
            if 'system_state' in oos_state:
                state_data = oos_state['system_state']
                archon_state = ArchonProjectState(
                    project_id=self.project_id,
                    oos_version=state_data.get('version', 'unknown'),
                    node_count=state_data.get('node_count', 1),
                    tasks_active=state_data.get('tasks_active', 0),
                    tasks_completed=state_data.get('tasks_completed', 0),
                    ai_requests_today=state_data.get('ai_requests_today', 0),
                    last_activity=datetime.fromisoformat(state_data.get('last_activity', datetime.now().isoformat())),
                    system_health=state_data.get('system_health', {})
                )

                if await self.sync_system_state(archon_state):
                    sync_results["synced_state"] = True
                else:
                    sync_results["success"] = False
                    sync_results["errors"].append("System state sync failed")

            # Send heartbeat
            if await self.sync_heartbeat():
                sync_results["heartbeat_sent"] = True

            # Update sync status
            self.sync_status.last_sync = datetime.now()
            self.sync_status.sync_count += 1

            sync_results["duration"] = time.time() - start_time

            logger.info(f"Full sync completed in {sync_results['duration']:.2f}s")
            return sync_results

        except Exception as e:
            logger.error(f"Full sync failed: {e}")
            self.sync_status.error_count += 1
            self.sync_status.last_error = str(e)
            sync_results["success"] = False
            sync_results["errors"].append(str(e))
            return sync_results

    def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync status"""
        return {
            "enabled": self.sync_status.enabled,
            "last_sync": self.sync_status.last_sync.isoformat() if self.sync_status.last_sync else None,
            "sync_count": self.sync_status.sync_count,
            "error_count": self.sync_status.error_count,
            "last_error": self.sync_status.last_error,
            "project_id": self.project_id,
            "archon_url": self.archon_url
        }


# Global sync manager
_sync_manager = None


def get_sync_manager() -> ArchonSyncManager:
    """Get or create global sync manager"""
    global _sync_manager
    if _sync_manager is None:
        _sync_manager = ArchonSyncManager()
    return _sync_manager


async def start_background_sync(oos_state: Dict[str, Any], interval: int = 300):
    """Start background sync process"""
    sync_manager = get_sync_manager()

    while True:
        try:
            logger.info("Starting background sync...")
            result = await sync_manager.full_sync(oos_state)

            if result["success"]:
                logger.info(f"Background sync successful: {result}")
            else:
                logger.warning(f"Background sync issues: {result['errors']}")

            # Wait for next sync
            await asyncio.sleep(interval)

        except Exception as e:
            logger.error(f"Background sync error: {e}")
            await asyncio.sleep(min(interval, 60))  # Retry sooner on error


if __name__ == "__main__":
    # Test Archon sync functionality
    async def test_archon_sync():
        print("🔄 Testing Archon Synchronization...")

        sync_manager = get_sync_manager()

        # Show sync status
        print("\n1. Sync Status:")
        status = sync_manager.get_sync_status()
        print(f"   Enabled: {status['enabled']}")
        print(f"   Project ID: {status['project_id']}")
        print(f"   Archon URL: {status['archon_url']}")

        if not status['enabled']:
            print("   ⚠️  Sync is disabled - no project ID configured")
            return

        # Test heartbeat
        print("\n2. Testing Heartbeat:")
        heartbeat_success = await sync_manager.sync_heartbeat()
        print(f"   Heartbeat: {'✅' if heartbeat_success else '❌'}")

        # Test task sync (create a test task)
        print("\n3. Testing Task Sync:")
        test_tasks = [
            {
                "id": "sync-test-001",
                "title": "Archon Sync Test Task",
                "description": "Test task created during sync verification",
                "status": "todo",
                "priority": "medium",
                "tags": ["test", "sync"]
            }
        ]

        task_sync_success = await sync_manager.sync_task_state(test_tasks)
        print(f"   Task Sync: {'✅' if task_sync_success else '❌'}")

        # Test system state sync
        print("\n4. Testing System State Sync:")
        oos_state = {
            "tasks": test_tasks,
            "system_state": {
                "version": "2.0",
                "node_count": 3,
                "tasks_active": 1,
                "tasks_completed": 5,
                "ai_requests_today": 12,
                "last_activity": datetime.now().isoformat(),
                "system_health": {
                    "ai_provider": "online",
                    "relayq_nodes": 1,
                    "sync_status": "active"
                }
            }
        }

        sync_result = await sync_manager.full_sync(oos_state)
        print(f"   Full Sync: {'✅' if sync_result['success'] else '❌'}")
        print(f"   Duration: {sync_result['duration']:.2f}s")
        print(f"   Tasks Synced: {sync_result['synced_tasks']}")
        print(f"   State Synced: {'Yes' if sync_result['synced_state'] else 'No'}")
        print(f"   Heartbeat: {'Yes' if sync_result['heartbeat_sent'] else 'No'}")

        print("\n✅ Archon synchronization test completed!")

    asyncio.run(test_archon_sync())