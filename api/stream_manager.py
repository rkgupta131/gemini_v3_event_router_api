"""
Stream Manager for Real-time Event Broadcasting
"""

import asyncio
from typing import Dict, Optional, Any, List
from collections import defaultdict
import json


class StreamManager:
    """
    Manages active SSE stream connections and broadcasts events to them.
    """
    
    def __init__(self):
        # Map of (project_id, conversation_id) -> list of queues
        self._streams: Dict[str, List[asyncio.Queue]] = defaultdict(list)
        self._all_events: List[Dict[str, Any]] = []  # Store all events for new connections
    
    def _get_stream_key(self, project_id: Optional[str], conversation_id: Optional[str]) -> str:
        """Generate a key for stream filtering"""
        return f"{project_id or '*'}:{conversation_id or '*'}"
    
    def register_stream(self, project_id: Optional[str], conversation_id: Optional[str]) -> asyncio.Queue:
        """Register a new stream connection and return its queue"""
        queue = asyncio.Queue()
        stream_key = self._get_stream_key(project_id, conversation_id)
        self._streams[stream_key].append(queue)
        return queue
    
    def unregister_stream(self, project_id: Optional[str], conversation_id: Optional[str], queue: asyncio.Queue):
        """Unregister a stream connection"""
        stream_key = self._get_stream_key(project_id, conversation_id)
        if stream_key in self._streams:
            try:
                self._streams[stream_key].remove(queue)
                if not self._streams[stream_key]:
                    del self._streams[stream_key]
            except ValueError:
                pass
    
    async def broadcast_event(self, event: Dict[str, Any]):
        """Broadcast an event to all matching stream connections"""
        # Store event for new connections
        self._all_events.append(event)
        # Keep only last 1000 events to avoid memory issues
        if len(self._all_events) > 1000:
            self._all_events = self._all_events[-1000:]
        
        event_project_id = event.get("project_id")
        event_conversation_id = event.get("conversation_id")
        
        # Broadcast to matching streams
        for stream_key, queues in list(self._streams.items()):
            project_id, conversation_id = stream_key.split(":", 1)
            
            # Check if event matches this stream's filters
            if project_id != "*" and event_project_id != project_id:
                continue
            if conversation_id != "*" and event_conversation_id != conversation_id:
                continue
            
            # Send to all queues for this stream key
            for queue in queues:
                try:
                    await queue.put(event)
                except Exception as e:
                    print(f"[STREAM_MANAGER] Error broadcasting to queue: {e}")
    
    def get_historical_events(
        self, 
        project_id: Optional[str] = None, 
        conversation_id: Optional[str] = None,
        model_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get historical events matching filters"""
        filtered = []
        for event in self._all_events:
            if project_id and event.get("project_id") != project_id:
                continue
            if conversation_id and event.get("conversation_id") != conversation_id:
                continue
            if model_name:
                # Check if event has model_name in payload or metadata
                event_model_name = event.get("model_name") or event.get("payload", {}).get("model_name")
                if event_model_name and event_model_name.lower() != model_name.lower():
                    continue
            filtered.append(event)
        return filtered


# Global stream manager instance
_stream_manager: Optional[StreamManager] = None


def get_stream_manager() -> StreamManager:
    """Get or create the global stream manager"""
    global _stream_manager
    if _stream_manager is None:
        _stream_manager = StreamManager()
    return _stream_manager

