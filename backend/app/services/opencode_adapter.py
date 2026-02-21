import asyncio
import json
import logging
import httpx
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)


class OpenCodeEventType(Enum):
    SESSION_CREATED = "session.created"
    SESSION_DELETED = "session.deleted"
    SESSION_UPDATED = "session.updated"
    SESSION_STATUS = "session.status"
    MESSAGE_UPDATED = "message.updated"
    MESSAGE_PART_UPDATED = "message.part.updated"
    MESSAGE_REMOVED = "message.removed"
    TOOL_EXECUTE_BEFORE = "tool.execute.before"
    TOOL_EXECUTE_AFTER = "tool.execute.after"
    PERMISSION_ASKED = "permission.asked"
    PERMISSION_REPLIED = "permission.replied"
    SERVER_CONNECTED = "server.connected"


class ClaudeOfficeEventType(Enum):
    SESSION_START = "session_start"
    SESSION_END = "session_end"
    USER_PROMPT_SUBMIT = "user_prompt_submit"
    PRE_TOOL_USE = "pre_tool_use"
    POST_TOOL_USE = "post_tool_use"
    PERMISSION_REQUEST = "permission_request"
    SUBAGENT_START = "subagent_start"
    SUBAGENT_STOP = "subagent_stop"
    CONTEXT_COMPACTED = "context_compacted"
    STOP = "stop"


class OpenCodeAdapter:
    def __init__(
        self,
        server_url: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        enabled: bool = True,
        api_endpoint: str = "http://localhost:8000/api/v1/events"
    ):
        self.server_url = server_url.rstrip("/")
        self.username = username
        self.password = password
        self.enabled = enabled
        self.api_endpoint = api_endpoint
        self.session: Optional[httpx.AsyncClient] = None
        self.running = False
        self.reconnect_delay = 5
        self.session_cache: Dict[str, Dict[str, Any]] = {}
        self.message_cache: Dict[str, Dict[str, Any]] = {}

    async def start(self):
        if not self.enabled:
            logger.info("OpenCode adapter is disabled")
            return

        self.running = True
        self.session = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0, connect=10.0),
            auth=(self.username, self.password) if self.username and self.password else None
        )

        logger.info(f"OpenCode adapter connecting to {self.server_url}")
        await self._connect_event_stream()

    async def stop(self):
        self.running = False
        if self.session:
            await self.session.aclose()
        logger.info("OpenCode adapter stopped")

    async def _connect_event_stream(self):
        while self.running:
            try:
                await self._stream_events()
            except Exception as e:
                logger.error(f"Event stream error: {e}")
                if self.running:
                    logger.info(f"Reconnecting in {self.reconnect_delay} seconds...")
                    await asyncio.sleep(self.reconnect_delay)

    async def _stream_events(self):
        url = f"{self.server_url}/event"
        async with self.session.stream("GET", url) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not self.running:
                    break
                if line.startswith("data: "):
                    await self._process_event(line[6:])

    async def _process_event(self, event_data: str):
        try:
            event = json.loads(event_data)
            event_type = event.get("type")
            properties = event.get("properties", {})

            logger.debug(f"Received OpenCode event: {event_type}")

            opencode_event_type = OpenCodeEventType(event_type)
            claud_event = self._transform_event(opencode_event_type, properties)

            if claud_event:
                await self._send_to_backend(claud_event)

        except ValueError as e:
            logger.error(f"Failed to parse event JSON: {e}")
        except Exception as e:
            logger.error(f"Error processing event: {e}")

    def _transform_event(
        self,
        opencode_type: OpenCodeEventType,
        properties: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        session_id = properties.get("session_id") or properties.get("id")
        if not session_id:
            logger.warning(f"Event missing session_id: {opencode_type.value}")
            return None

        timestamp = datetime.now().isoformat()

        if opencode_type == OpenCodeEventType.SESSION_CREATED:
            self.session_cache[session_id] = properties
            return {
                "event_type": ClaudeOfficeEventType.SESSION_START.value,
                "session_id": session_id,
                "timestamp": timestamp,
                "data": self._extract_session_data(properties)
            }

        elif opencode_type == OpenCodeEventType.SESSION_DELETED:
            return {
                "event_type": ClaudeOfficeEventType.SESSION_END.value,
                "session_id": session_id,
                "timestamp": timestamp,
                "data": {}
            }

        elif opencode_type == OpenCodeEventType.SESSION_STATUS:
            status = properties.get("status")
            if status == "idle":
                return {
                    "event_type": ClaudeOfficeEventType.STOP.value,
                    "session_id": session_id,
                    "timestamp": timestamp,
                    "data": {}
                }
            elif status == "running":
                return {
                    "event_type": ClaudeOfficeEventType.USER_PROMPT_SUBMIT.value,
                    "session_id": session_id,
                    "timestamp": timestamp,
                    "data": {"prompt": "Task started"}
                }

        elif opencode_type == OpenCodeEventType.MESSAGE_UPDATED:
            message = properties.get("message", {})
            self.message_cache[message.get("id")] = message
            role = message.get("role")
            if role == "user":
                parts = message.get("parts", [])
                text_parts = [p.get("text") for p in parts if p.get("type") == "text"]
                prompt = " ".join(text_parts)
                return {
                    "event_type": ClaudeOfficeEventType.USER_PROMPT_SUBMIT.value,
                    "session_id": session_id,
                    "timestamp": timestamp,
                    "data": {"prompt": prompt}
                }

        elif opencode_type == OpenCodeEventType.TOOL_EXECUTE_BEFORE:
            tool_input = properties.get("input", {})
            tool_name = tool_input.get("tool", "unknown")
            tool_input_data = tool_input.get("args", {})
            parent_session = self.session_cache.get(properties.get("parent_id"))

            if parent_session or properties.get("parent_id"):
                tool_use_id = properties.get("id", "")
                return {
                    "event_type": ClaudeOfficeEventType.PRE_TOOL_USE.value,
                    "session_id": session_id,
                    "timestamp": timestamp,
                    "data": {
                        "tool_name": tool_name,
                        "tool_input": tool_input_data,
                        "tool_use_id": tool_use_id
                    }
                }

        elif opencode_type == OpenCodeEventType.TOOL_EXECUTE_AFTER:
            tool_input = properties.get("input", {})
            tool_name = tool_input.get("tool", "unknown")
            output = properties.get("output", {})

            return {
                "event_type": ClaudeOfficeEventType.POST_TOOL_USE.value,
                "session_id": session_id,
                "timestamp": timestamp,
                "data": {
                    "tool_name": tool_name,
                    "tool_input": tool_input.get("args", {}),
                    "success": output.get("success", True),
                    "error_type": output.get("error"),
                    "result_summary": str(output)[:200] if output else ""
                }
            }

        elif opencode_type == OpenCodeEventType.PERMISSION_ASKED:
            permission = properties.get("permission", {})
            return {
                "event_type": ClaudeOfficeEventType.PERMISSION_REQUEST.value,
                "session_id": session_id,
                "timestamp": timestamp,
                "data": {
                    "permission_type": permission.get("type"),
                    "message": permission.get("message")
                }
            }

        return None

    def _extract_session_data(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        project = properties.get("project", {})
        return {
            "project_name": project.get("name"),
            "project_root": project.get("root"),
            "session_title": properties.get("title", "Untitled"),
            "native_agent_id": properties.get("id"),
            "agent_name": properties.get("title", "Agent")
        }

    async def _send_to_backend(self, event: Dict[str, Any]):
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    self.api_endpoint,
                    json=event,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                logger.debug(f"Sent event to backend: {event.get('event_type')}")
        except Exception as e:
            logger.error(f"Failed to send event to backend: {e}")

    async def get_session_details(self, session_id: str) -> Optional[Dict[str, Any]]:
        try:
            url = f"{self.server_url}/session/{session_id}"
            response = await self.session.get(url)
            response.raise_for_status()
            data = response.json()
            self.session_cache[session_id] = data
            return data
        except Exception as e:
            logger.error(f"Failed to get session details: {e}")
            return None

    async def get_session_children(self, session_id: str) -> list:
        try:
            url = f"{self.server_url}/session/{session_id}/children"
            response = await self.session.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get session children: {e}")
            return []
