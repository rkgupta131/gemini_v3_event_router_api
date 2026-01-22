# Unified Stream Endpoint Guide

## Overview

The API provides a **single unified `/api/v1/stream` endpoint** that handles all event streaming. This endpoint uses Server-Sent Events (SSE) to stream events in real-time as they are generated during project operations.

## Endpoint

```
GET /api/v1/stream
```

## Query Parameters

- `project_id` (optional): Filter events by project ID
- `conversation_id` (optional): Filter events by conversation ID

## Event Types

The stream handles **all event types** from the Event Contract:

### Chat & Cognition Events
- `chat.message` - Chat messages
- `thinking.start` - Thinking indicator start
- `thinking.end` - Thinking indicator end
- `chat.question` - Questions requiring user input
- `chat.suggestion` - Suggestions for user

### Progress Events
- `progress.init` - Initialize progress steps
- `progress.update` - Update progress step status
- `progress.transition` - Transition progress mode

### Filesystem Events
- `fs.create` - File/folder creation
- `fs.write` - File write operations
- `fs.delete` - File deletion

### Edit Events
- `edit.read` - File read operation
- `edit.start` - Edit operation start
- `edit.end` - Edit operation end
- `edit.security_check` - Security check result

### Build Events (Backend-owned)
- `build.start` - Build process started
- `build.log` - Build log message
- `build.error` - Build error
- `preview.ready` - Preview ready with URL

### Version Events (Backend-owned)
- `version.created` - Version created
- `version.deployed` - Version deployed

### Error Events
- `error` - Error occurred

### Stream Lifecycle Events
- `stream.complete` - Stream completed successfully
- `stream.await_input` - Stream waiting for user input
- `stream.failed` - Stream failed

## Frontend Integration

### JavaScript/TypeScript Example

```javascript
// Connect to stream
const projectId = 'proj_123';
const conversationId = 'conv_456';
const eventSource = new EventSource(
  `/api/v1/stream?project_id=${projectId}&conversation_id=${conversationId}`
);

// Handle incoming events
eventSource.onmessage = (event) => {
  // Check for stream end
  if (event.data === '[DONE]') {
    eventSource.close();
    console.log('Stream completed');
    return;
  }
  
  // Parse event data
  const eventData = JSON.parse(event.data);
  
  // Handle different event types
  switch (eventData.event_type) {
    case 'chat.message':
      console.log('Chat:', eventData.payload.content);
      break;
      
    case 'progress.update':
      console.log('Progress:', eventData.payload);
      updateProgressUI(eventData.payload);
      break;
      
    case 'fs.write':
      console.log('File written:', eventData.payload.path);
      updateFileTree(eventData.payload);
      break;
      
    case 'stream.complete':
      console.log('Stream completed');
      eventSource.close();
      break;
      
    case 'error':
      console.error('Error:', eventData.payload);
      break;
      
    default:
      console.log('Event:', eventData);
  }
};

// Handle errors
eventSource.onerror = (error) => {
  console.error('Stream error:', error);
  eventSource.close();
};

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
  eventSource.close();
});
```

### React Example

```jsx
import { useEffect, useState } from 'react';

function useEventStream(projectId, conversationId) {
  const [events, setEvents] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  
  useEffect(() => {
    const eventSource = new EventSource(
      `/api/v1/stream?project_id=${projectId}&conversation_id=${conversationId}`
    );
    
    eventSource.onopen = () => {
      setIsConnected(true);
    };
    
    eventSource.onmessage = (event) => {
      if (event.data === '[DONE]') {
        eventSource.close();
        setIsConnected(false);
        return;
      }
      
      const eventData = JSON.parse(event.data);
      setEvents(prev => [...prev, eventData]);
    };
    
    eventSource.onerror = () => {
      setIsConnected(false);
      eventSource.close();
    };
    
    return () => {
      eventSource.close();
    };
  }, [projectId, conversationId]);
  
  return { events, isConnected };
}

// Usage in component
function ProjectView({ projectId, conversationId }) {
  const { events, isConnected } = useEventStream(projectId, conversationId);
  
  return (
    <div>
      <div>Status: {isConnected ? 'Connected' : 'Disconnected'}</div>
      <div>Events: {events.length}</div>
      {/* Render events */}
    </div>
  );
}
```

## Event Format

Each event follows this structure:

```json
{
  "event_id": "evt_0001",
  "event_type": "chat.message",
  "timestamp": "2025-01-04T10:15:30Z",
  "project_id": "proj_123",
  "conversation_id": "conv_456",
  "payload": {
    "content": "Starting project generation..."
  }
}
```

## Stream Behavior

1. **Historical Events**: When a client connects, it first receives all historical events matching the filters
2. **Real-time Events**: After historical events, new events are streamed in real-time as they're generated
3. **Keepalive**: The stream sends keepalive messages every 30 seconds to prevent connection timeout
4. **Stream End**: The stream ends when a `stream.complete` or `stream.failed` event is received, followed by `[DONE]`

## Filtering

### Filter by Project ID Only
```
GET /api/v1/stream?project_id=proj_123
```

### Filter by Conversation ID Only
```
GET /api/v1/stream?conversation_id=conv_456
```

### Filter by Both
```
GET /api/v1/stream?project_id=proj_123&conversation_id=conv_456
```

### No Filters (All Events)
```
GET /api/v1/stream
```

## Error Handling

The stream may send error events:

```json
{
  "event_type": "error",
  "message": "Stream error: ..."
}
```

Always handle `onerror` to detect connection issues:

```javascript
eventSource.onerror = (error) => {
  console.error('Stream connection error:', error);
  // Attempt to reconnect or show error to user
};
```

## Backward Compatibility

The `/api/v1/events` endpoint is still available for non-streaming event retrieval, but `/api/v1/stream` is the recommended approach for real-time updates.

## Example: Complete Project Generation Flow

```javascript
// 1. Start project generation
const response = await fetch('/api/v1/project/generate', {
  method: 'POST',
  body: JSON.stringify({
    user_query: 'Build a CRM dashboard',
    project_id: 'proj_123',
    conversation_id: 'conv_456'
  })
});

const { project_id, conversation_id } = await response.json();

// 2. Connect to stream
const eventSource = new EventSource(
  `/api/v1/stream?project_id=${project_id}&conversation_id=${conversation_id}`
);

// 3. Handle events
eventSource.onmessage = (event) => {
  if (event.data === '[DONE]') {
    eventSource.close();
    return;
  }
  
  const eventData = JSON.parse(event.data);
  
  // Update UI based on event type
  if (eventData.event_type === 'progress.update') {
    updateProgressBar(eventData.payload);
  } else if (eventData.event_type === 'fs.write') {
    addFileToTree(eventData.payload);
  } else if (eventData.event_type === 'chat.message') {
    addMessageToChat(eventData.payload.content);
  }
};
```

## Notes

- The stream maintains a buffer of the last 1000 events for new connections
- Multiple clients can connect to the same stream simultaneously
- Events are automatically filtered based on query parameters
- The connection is automatically cleaned up when the client disconnects

