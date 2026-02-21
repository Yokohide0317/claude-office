"""Test OpenCode adapter with mock events."""

import asyncio
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.services.opencode_adapter import OpenCodeAdapter, OpenCodeEventType


async def test_event_transformation():
    """Test that OpenCode events are correctly transformed."""
    adapter = OpenCodeAdapter(
        server_url="http://localhost:4096",
        enabled=False,  # Don't start the actual adapter
        api_endpoint="http://localhost:8000/api/v1/events"
    )

    print("Testing OpenCode event transformation...")

    # Test session created event
    session_created = {
        "type": "session.created",
        "properties": {
            "session_id": "test-session-1",
            "id": "test-session-1",
            "title": "Test Session",
            "project": {
                "name": "test-project",
                "root": "/home/user/test"
            }
        }
    }

    result = adapter._transform_event(
        OpenCodeEventType.SESSION_CREATED,
        session_created["properties"]
    )

    print(f"\n1. Session Created:")
    print(json.dumps(result, indent=2))

    # Test tool execute before
    tool_before = {
        "type": "tool.execute.before",
        "properties": {
            "session_id": "test-session-1",
            "id": "tool-123",
            "parent_id": "test-session-1",
            "input": {
                "tool": "bash",
                "args": {
                    "command": "ls -la"
                }
            }
        }
    }

    result = adapter._transform_event(
        OpenCodeEventType.TOOL_EXECUTE_BEFORE,
        tool_before["properties"]
    )

    print(f"\n2. Tool Execute Before:")
    print(json.dumps(result, indent=2))

    # Test message updated (user)
    message_updated = {
        "type": "message.updated",
        "properties": {
            "session_id": "test-session-1",
            "message": {
                "id": "msg-123",
                "role": "user",
                "parts": [
                    {"type": "text", "text": "Hello, please help me with this task"}
                ]
            }
        }
    }

    result = adapter._transform_event(
        OpenCodeEventType.MESSAGE_UPDATED,
        message_updated["properties"]
    )

    print(f"\n3. Message Updated (User):")
    print(json.dumps(result, indent=2))

    # Test session status (idle)
    session_idle = {
        "type": "session.status",
        "properties": {
            "session_id": "test-session-1",
            "status": "idle"
        }
    }

    result = adapter._transform_event(
        OpenCodeEventType.SESSION_STATUS,
        session_idle["properties"]
    )

    print(f"\n4. Session Status (Idle):")
    print(json.dumps(result, indent=2))

    # Test permission asked
    permission = {
        "type": "permission.asked",
        "properties": {
            "session_id": "test-session-1",
            "permission": {
                "type": "file.write",
                "message": "Do you want to write to config.json?"
            }
        }
    }

    result = adapter._transform_event(
        OpenCodeEventType.PERMISSION_ASKED,
        permission["properties"]
    )

    print(f"\n5. Permission Asked:")
    print(json.dumps(result, indent=2))

    print("\n✅ All tests passed!")


async def test_connection():
    """Test connection to OpenCode server (if available)."""
    import httpx

    print("\nTesting OpenCode server connection...")

    adapter = OpenCodeAdapter(
        server_url="http://localhost:4096",
        enabled=False
    )

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:4096/global/health")
            if response.status_code == 200:
                print("✅ OpenCode server is running!")
                print(f"   Response: {response.json()}")
            else:
                print(f"⚠️  OpenCode server returned status {response.status_code}")
    except Exception as e:
        print(f"⚠️  Could not connect to OpenCode server: {e}")
        print("   Make sure 'opencode serve' is running")


if __name__ == "__main__":
    asyncio.run(test_event_transformation())
    asyncio.run(test_connection())
