# Testing Event Streaming

## Issue Fixed
- ✅ API no longer hangs when `needs_followup=True`
- ✅ Questions are now emitted as `chat.question` events
- ✅ API continues with generation (non-blocking)
- ✅ Events are properly broadcast to SSE streams

## Why Postman Doesn't Work Well for SSE

Postman has limited support for Server-Sent Events (SSE). The events may not display properly or may timeout.

## Recommended Testing Methods

### Method 1: Using curl (Terminal)

**Terminal 1 - Start Event Stream:**
```bash
curl -N "http://localhost:8000/api/v1/stream?project_id=proj_test_123&conversation_id=conv_test_456&model_name=Gemini"
```

**Terminal 2 - Generate Project:**
```bash
curl -X POST "http://localhost:8000/api/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "user_query": "Build a simple landing page for a SaaS product",
    "model_family": "Gemini",
    "project_id": "proj_test_123",
    "conversation_id": "conv_test_456"
  }'
```

You'll see events streaming in Terminal 1 in real-time.

### Method 2: Using Browser EventSource API

Create an HTML file (`test_events.html`):

```html
<!DOCTYPE html>
<html>
<head>
    <title>Event Stream Test</title>
</head>
<body>
    <h1>Event Stream</h1>
    <div id="events"></div>
    
    <script>
        const projectId = 'proj_test_123';
        const conversationId = 'conv_test_456';
        const modelName = 'Gemini';
        
        const eventSource = new EventSource(
            `http://localhost:8000/api/v1/stream?project_id=${projectId}&conversation_id=${conversationId}&model_name=${modelName}`
        );
        
        const eventsDiv = document.getElementById('events');
        
        eventSource.onmessage = (event) => {
            if (event.data === '[DONE]') {
                eventSource.close();
                eventsDiv.innerHTML += '<p><strong>Stream ended</strong></p>';
                return;
            }
            
            try {
                const data = JSON.parse(event.data);
                const eventDiv = document.createElement('div');
                eventDiv.style.border = '1px solid #ccc';
                eventDiv.style.margin = '10px';
                eventDiv.style.padding = '10px';
                eventDiv.innerHTML = `
                    <strong>Event Type:</strong> ${data.event_type}<br>
                    <strong>Timestamp:</strong> ${data.timestamp}<br>
                    <pre>${JSON.stringify(data.payload, null, 2)}</pre>
                `;
                eventsDiv.appendChild(eventDiv);
            } catch (e) {
                console.error('Error parsing event:', e);
            }
        };
        
        eventSource.onerror = (error) => {
            console.error('EventSource error:', error);
            eventsDiv.innerHTML += '<p style="color: red;"><strong>Error occurred</strong></p>';
        };
    </script>
</body>
</html>
```

Open this file in a browser, then make the POST request from another terminal/Postman.

### Method 3: Using Python Script

Create `test_stream.py`:

```python
import requests
import json
import time

# Start streaming in background
project_id = "proj_test_123"
conversation_id = "conv_test_456"
model_name = "Gemini"

# Make POST request to generate project
response = requests.post(
    "http://localhost:8000/api/stream",
    json={
        "user_query": "Build a simple landing page for a SaaS product",
        "model_family": "Gemini",
        "project_id": project_id,
        "conversation_id": conversation_id
    },
    stream=False
)

print("POST Response:", response.json())

# Now stream events
stream_url = f"http://localhost:8000/api/v1/stream?project_id={project_id}&conversation_id={conversation_id}&model_name={model_name}"
stream_response = requests.get(stream_url, stream=True)

print("\n=== Streaming Events ===\n")
for line in stream_response.iter_lines():
    if line:
        line_str = line.decode('utf-8')
        if line_str.startswith('data: '):
            data = line_str[6:]  # Remove 'data: ' prefix
            if data == '[DONE]':
                print("Stream ended")
                break
            try:
                event = json.loads(data)
                print(f"Event: {event.get('event_type')}")
                print(f"Payload: {json.dumps(event.get('payload'), indent=2)}")
                print("-" * 50)
            except json.JSONDecodeError:
                print(f"Raw data: {data}")
```

Run: `python test_stream.py`

## Understanding the Flow

1. **POST to `/api/stream`** - Generates project and emits events
2. **GET to `/api/v1/stream`** - Receives events in real-time via SSE

### Event Types You'll See:

- `chat.message` - Status messages
- `chat.question` - Questions when `needs_followup=True` (if questionnaire exists)
- `progress.init` - Progress tracking initialized
- `progress.update` - Progress updates
- `thinking.start` - LLM thinking started
- `thinking.end` - LLM thinking completed
- `stream.complete` - Stream completed successfully

## Providing Questionnaire Answers

If questions were emitted, you can provide answers in a follow-up request:

```bash
curl -X POST "http://localhost:8000/api/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "user_query": "Build a simple landing page for a SaaS product",
    "model_family": "Gemini",
    "project_id": "proj_test_123",
    "conversation_id": "conv_test_456",
    "questionnaire_answers": {
      "industry": "SaaS / Software Product",
      "primary_goal": "Lead Generation (Capture emails/contacts)",
      "target_audience": "B2B (Businesses)"
    }
  }'
```

## Troubleshooting

### Events not showing up?
1. Make sure `project_id` and `conversation_id` match in both requests
2. Make sure `model_name` in stream matches `model_family` in POST (or use no filter)
3. Check server logs for `[STREAM_MANAGER] Broadcasted event` messages
4. Ensure the background event processor is running (check startup logs)

### API hanging?
- The fix ensures the API never hangs - it always proceeds with generation
- Questions are emitted as events but don't block the API response
- If you see hanging, check server logs for errors

### Postman not working?
- Postman has limited SSE support
- Use curl, browser EventSource, or Python script instead
- For Postman, you can still test the POST endpoint (it will return JSON), but events won't stream

