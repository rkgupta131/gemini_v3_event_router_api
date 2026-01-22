"""
Stream Manager for Real-time Event Broadcasting
"""

import asyncio
import queue
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
        # Synchronous queue for events from sync callbacks (thread-safe)
        self._sync_event_queue = queue.Queue()
        self._processor_started = False
        self._processor_task: Optional[asyncio.Task] = None
    
    def _get_stream_key(self, project_id: Optional[str], conversation_id: Optional[str], model_name: Optional[str] = None) -> str:
        """Generate a key for stream filtering"""
        return f"{project_id or '*'}:{conversation_id or '*'}:{model_name or '*'}"
    
    def register_stream(self, project_id: Optional[str], conversation_id: Optional[str], model_name: Optional[str] = None) -> asyncio.Queue:
        """Register a new stream connection and return its queue"""
        queue = asyncio.Queue()
        stream_key = self._get_stream_key(project_id, conversation_id, model_name)
        self._streams[stream_key].append(queue)
        return queue
    
    def unregister_stream(self, project_id: Optional[str], conversation_id: Optional[str], queue: asyncio.Queue, model_name: Optional[str] = None):
        """Unregister a stream connection"""
        stream_key = self._get_stream_key(project_id, conversation_id, model_name)
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
        # Get model_name from event (can be top-level or in payload)
        event_model_name = event.get("model_name") or event.get("payload", {}).get("model_name")
        
        # Broadcast to matching streams
        for stream_key, queues in list(self._streams.items()):
            parts = stream_key.split(":", 2)
            project_id = parts[0] if len(parts) > 0 else "*"
            conversation_id = parts[1] if len(parts) > 1 else "*"
            model_filter = parts[2] if len(parts) > 2 else "*"
            
            # Check if event matches this stream's filters
            if project_id != "*" and event_project_id != project_id:
                continue
            if conversation_id != "*" and event_conversation_id != conversation_id:
                continue
            if model_filter != "*" and event_model_name and event_model_name.lower() != model_filter.lower():
                continue
            
            # Send to all queues for this stream key
            for queue in queues:
                try:
                    await queue.put(event)
                except Exception as e:
                    print(f"[STREAM_MANAGER] Error broadcasting to queue: {e}")
    
    async def _process_sync_event_queue(self):
        """Background task to process events from synchronous queue"""
        print("[STREAM_MANAGER] Background event processor running...")
        while True:
            try:
                # Get event from queue (with timeout to allow checking for shutdown)
                try:
                    event = self._sync_event_queue.get(timeout=1.0)
                    # Broadcast the event
                    await self.broadcast_event(event)
                    print(f"[STREAM_MANAGER] Broadcasted event: {event.get('event_type', 'unknown')}")
                except queue.Empty:
                    # No events, continue waiting
                    await asyncio.sleep(0.1)
                    continue
            except asyncio.CancelledError:
                print("[STREAM_MANAGER] Background processor cancelled")
                break
            except Exception as e:
                print(f"[STREAM_MANAGER] Error processing sync event queue: {e}")
                import traceback
                traceback.print_exc()
                await asyncio.sleep(0.1)
    
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

