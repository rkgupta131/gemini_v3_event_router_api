"""
Event Streaming Routes
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from api.models import EventStreamRequest
from utils.event_logger import get_event_logger
import json

router = APIRouter()


@router.get("/events/stream")
async def stream_events(project_id: str = None, conversation_id: str = None):
    """
    Stream events via Server-Sent Events (SSE).
    
    This endpoint provides real-time event streaming for frontend integration.
    Events are streamed in SSE format as they are generated.
    """
    event_logger = get_event_logger()
    
    def event_generator():
        """Generator function for SSE streaming"""
        # Get events from logger
        events = event_logger.get_events()
        
        # Filter by project_id/conversation_id if provided
        for event in events:
            if project_id and event.get("project_id") != project_id:
                continue
            if conversation_id and event.get("conversation_id") != conversation_id:
                continue
            
            # Format as SSE
            yield f"data: {json.dumps(event)}\n\n"
        
        # Send end marker
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/events")
async def get_events(project_id: str = None, conversation_id: str = None):
    """
    Get all events (non-streaming).
    
    Returns a list of all events, optionally filtered by project_id or conversation_id.
    """
    try:
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

