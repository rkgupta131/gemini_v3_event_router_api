"""
Event Streaming Routes - Unified Stream Endpoint
"""

import asyncio
import json
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from api.stream_manager import get_stream_manager
from utils.event_logger import get_event_logger

router = APIRouter()


@router.get("/stream")
async def stream_events(
    project_id: Optional[str] = Query(None, description="Filter events by project ID"),
    conversation_id: Optional[str] = Query(None, description="Filter events by conversation ID"),
    model_name: Optional[str] = Query(None, description="Filter events by model family: Gemini, Claude, or GPT")
):
    """
    Unified event streaming endpoint via Server-Sent Events (SSE).
    
    This is the SINGLE endpoint for all event streaming. It handles:
    - Real-time event streaming as events are generated
    - Filtering by project_id and/or conversation_id
    - All event types (chat, progress, filesystem, build, errors, etc.)
    - Historical events for new connections
    
    **Usage:**
    ```javascript
    const eventSource = new EventSource('/api/v1/stream?project_id=proj_123&conversation_id=conv_456');
    
    eventSource.onmessage = (event) => {
        if (event.data === '[DONE]') {
            eventSource.close();
            return;
        }
        const eventData = JSON.parse(event.data);
        console.log('Event:', eventData);
    };
    ```
    
    **Event Format:**
    Each event is sent as:
    ```
    data: {"event_id": "...", "event_type": "...", "payload": {...}}
    ```
    
    **Stream End:**
    The stream ends with:
    ```
    data: [DONE]
    ```
    """
    stream_manager = get_stream_manager()
    event_queue = stream_manager.register_stream(project_id, conversation_id)
    
    async def event_generator():
        """Generator function for SSE streaming"""
        try:
            # First, send historical events matching the filters
            historical_events = stream_manager.get_historical_events(project_id, conversation_id, model_name)
            for event in historical_events:
                yield f"data: {json.dumps(event)}\n\n"
            
            # Then stream new events in real-time
            while True:
                try:
                    # Wait for new event with timeout for keepalive
                    event = await asyncio.wait_for(event_queue.get(), timeout=30.0)
                    
                    # Check if stream should end
                    if event.get("event_type") in ["stream.complete", "stream.failed"]:
                        yield f"data: {json.dumps(event)}\n\n"
                        yield "data: [DONE]\n\n"
                        break
                    
                    # Send the event
                    yield f"data: {json.dumps(event)}\n\n"
                    
                except asyncio.TimeoutError:
                    # Send keepalive to prevent connection timeout
                    yield ": keepalive\n\n"
                    continue
                    
        except asyncio.CancelledError:
            # Client disconnected
            pass
        except Exception as e:
            # Send error event
            error_event = {
                "event_type": "error",
                "message": f"Stream error: {str(e)}"
            }
            yield f"event: error\ndata: {json.dumps(error_event)}\n\n"
        finally:
            # Cleanup: unregister stream
            stream_manager.unregister_stream(project_id, conversation_id, event_queue)
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )


@router.get("/events")
async def get_events(
    project_id: Optional[str] = Query(None, description="Filter events by project ID"),
    conversation_id: Optional[str] = Query(None, description="Filter events by conversation ID")
):
    """
    Get all events (non-streaming) - for backward compatibility.
    
    **Note:** Prefer using `/stream` for real-time updates.
    
    Returns a list of all events, optionally filtered by project_id or conversation_id.
    """
    try:
        # Try to get from stream manager first (has all events)
        try:
            stream_manager = get_stream_manager()
            events = stream_manager.get_historical_events(project_id, conversation_id)
            return {"events": events, "count": len(events)}
        except Exception:
            # Fallback to event logger
            event_logger = get_event_logger()
            events = event_logger.get_events()
            
            # Filter if needed
            if project_id or conversation_id:
                filtered = []
                for event in events:
                    if project_id and event.get("project_id") != project_id:
                        continue
                    if conversation_id and event.get("conversation_id") != conversation_id:
                        continue
                    filtered.append(event)
                return {"events": filtered, "count": len(filtered)}
            
            return {"events": events, "count": len(events)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get events: {str(e)}")
