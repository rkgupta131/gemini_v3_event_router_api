"""
Event logger for Streamlit - captures and displays events in the UI.
"""

import json
from typing import List, Dict, Any, Optional
try:
    import streamlit as st
except ImportError:
    st = None
from events.event_types import EventEnvelope


class StreamlitEventLogger:
    """
    Event logger that captures events and displays them in Streamlit UI.
    Also optionally saves events to a file.
    """
    
    def __init__(self, save_to_file: bool = True, output_file: str = "output/events.jsonl"):
        self.events: List[Dict[str, Any]] = []
        self.save_to_file = save_to_file
        self.output_file = output_file
    
    def log_event(self, event: EventEnvelope):
        """Log an event and optionally save to file."""
        event_dict = event.to_dict()
        
        # Extract model_name from payload if present and add as top-level field
        model_name = event_dict.get("payload", {}).get("model_name")
        if model_name:
            event_dict["model_name"] = model_name
        
        self.events.append(event_dict)
        
        # Broadcast to stream manager if available (for API context)
        # Use a synchronous queue that will be processed by async background task
        try:
            from api.stream_manager import get_stream_manager
            stream_manager = get_stream_manager()
            
            # Add event to queue (thread-safe, synchronous)
            # The background processor will pick it up and broadcast it
            stream_manager._sync_event_queue.put_nowait(event_dict)
            
        except (ImportError, Exception) as e:
            # Stream manager not available or error - continue normally
            print(f"[EVENT_LOGGER] Error queuing event for broadcast: {e}")
            import traceback
            traceback.print_exc()
            pass
        
        if self.save_to_file:
            try:
                import os
                os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
                with open(self.output_file, "a", encoding="utf-8") as f:
                    f.write(json.dumps(event_dict) + "\n")
            except Exception as e:
                print(f"[EVENT_LOGGER] Error saving event to file: {e}")
    
    def display_events(self, container=None):
        """Display events in Streamlit UI."""
        if container is None:
            container = st
        
        if not self.events:
            return
        
        with container.expander("📡 Events Stream (for Frontend/Backend Teams)", expanded=True):
            st.success(f"✅ **{len(self.events)} events** generated during this session")
            st.caption(f"These events follow the Phase 1 LLM Streaming Contract")
            
            # Show event type summary
            event_types = {}
            for event in self.events:
                event_type = event.get("event_type", "unknown")
                event_types[event_type] = event_types.get(event_type, 0) + 1
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Event Types:**")
                for event_type, count in sorted(event_types.items()):
                    st.text(f"  {event_type}: {count}")
            
            # Show recent events
            st.markdown("**Recent Events (last 10):**")
            for event in self.events[-10:]:
                event_type = event.get("event_type", "unknown")
                event_id = event.get("event_id", "unknown")
                timestamp = event.get("timestamp", "unknown")
                
                with st.expander(f"{event_type} ({event_id})", expanded=False):
                    st.json(event)
            
            # Download button for all events
            events_json = json.dumps(self.events, indent=2)
            st.download_button(
                label="📥 Download All Events (JSON)",
                data=events_json,
                file_name="events.json",
                mime="application/json"
            )
            
            # Download button for JSONL (one event per line, for SSE simulation)
            events_jsonl = "\n".join(json.dumps(event) for event in self.events)
            st.download_button(
                label="📥 Download Events (JSONL - for SSE)",
                data=events_jsonl,
                file_name="events.jsonl",
                mime="application/x-ndjson"
            )
    
    def get_events(self) -> List[Dict[str, Any]]:
        """Get all logged events."""
        return self.events
    
    def clear(self):
        """Clear all events."""
        self.events = []


# Global logger for API context
_api_event_logger: Optional[StreamlitEventLogger] = None


def get_event_logger() -> StreamlitEventLogger:
    """Get or create the event logger (works in both Streamlit and API contexts)."""
    try:
        # Try Streamlit context first
        if "event_logger" not in st.session_state:
            st.session_state.event_logger = StreamlitEventLogger()
        return st.session_state.event_logger
    except (ImportError, RuntimeError, AttributeError):
        # API context - use global logger
        global _api_event_logger
        if _api_event_logger is None:
            _api_event_logger = StreamlitEventLogger()
        return _api_event_logger

