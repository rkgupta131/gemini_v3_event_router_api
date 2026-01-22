# Postman Collection Setup Guide

## Import Instructions

### Step 1: Import Collection

1. Open Postman
2. Click **Import** button (top left)
3. Select **File** tab
4. Choose `Postman_Collection.json`
5. Click **Import**

### Step 2: Import Environment (Optional but Recommended)

1. Click **Import** again
2. Select **File** tab
3. Choose `Postman_Environment.json`
4. Click **Import**
5. Select the "Gemini API Environment" from the environment dropdown (top right)

### Step 3: Configure Base URL

If you're not using the environment file:

1. Click on the collection name
2. Go to **Variables** tab
3. Update `base_url` to your API URL:
   - Local: `http://localhost:8000`
   - Production: `https://your-api-domain.com`

## Collection Structure

The collection is organized into folders:

### 1. Health & Info
- Root API info
- Health check endpoint

### 2. Intent Classification
- Classify intent (webpage_build, chat, etc.)

### 3. Page Type
- Classify page type
- Get page type reference
- List all page types

### 4. Query Analysis
- Analyze if query needs follow-up questions

### 5. Chat
- Get chat responses

### 6. Questionnaire
- Get questionnaire for page type
- Check if questionnaire exists

### 7. Categories
- Get all page type categories

### 8. Project Generation
- Generate simple project
- Generate with questionnaire
- Generate complex project (CRM)
- Get project by ID

### 9. Project Modification
- Simple modifications
- Add components

### 10. Events
- Get events (non-streaming)
- Stream events (SSE) - Note: SSE may not work perfectly in Postman

## Testing Workflow

### Basic Flow

1. **Health Check**: Start with `/api/v1/health` to verify API is running

2. **Classify Intent**: 
   ```
   POST /api/v1/intent/classify
   {
     "user_text": "I want to build a CRM"
   }
   ```

3. **Classify Page Type**:
   ```
   POST /api/v1/page-type/classify
   {
     "user_text": "Build a CRM dashboard"
   }
   ```

4. **Generate Project**:
   ```
   POST /api/v1/project/generate
   {
     "user_query": "Build a CRM dashboard",
     "page_type_key": "crm_dashboard"
   }
   ```
   - Copy the `project_id` and `conversation_id` from response
   - Update environment variables with these values

5. **Get Events**:
   ```
   GET /api/v1/events?project_id=proj_123&conversation_id=conv_456
   ```

6. **Modify Project**:
   ```
   POST /api/v1/project/modify
   {
     "instruction": "Change theme to dark mode",
     "project_id": "proj_123"
   }
   ```

## Environment Variables

The collection uses these variables:

- `base_url`: API base URL (default: `http://localhost:8000`)
- `project_id`: Project ID from generation response
- `conversation_id`: Conversation ID from generation response

## Tips

1. **Update Variables**: After generating a project, copy the `project_id` and `conversation_id` from the response and update the environment variables

2. **SSE Streaming**: The `/stream` endpoint uses Server-Sent Events which may not display properly in Postman. Use the `/events` endpoint for testing in Postman, or test SSE in a browser with JavaScript

3. **Long Requests**: Project generation can take 20-150 seconds. Increase Postman's timeout in Settings → General → Request timeout

4. **View Response**: Click on a request, then click "Send". The response will appear in the bottom panel

5. **Save Responses**: Right-click on a request → "Save Response" → "Save as example" to save successful responses

## Example Test Sequence

1. ✅ Health Check
2. ✅ Classify Intent: "Build a CRM"
3. ✅ Classify Page Type: "Build a CRM dashboard"
4. ✅ Get Questionnaire: `/api/v1/questionnaire/crm_dashboard`
5. ✅ Generate Project with questionnaire answers
6. ✅ Get Events for the project
7. ✅ Modify Project: "Add a contact form"
8. ✅ Get Updated Events

## Troubleshooting

### Connection Refused
- Make sure the API server is running: `uvicorn api.main:app --reload`
- Check the `base_url` is correct

### 500 Internal Server Error
- Check server logs for details
- Verify environment variables (GOOGLE_CLOUD_PROJECT, etc.) are set

### Timeout Errors
- Project generation can take time, increase Postman timeout
- For complex projects (CRM), expect 90-150 seconds

### SSE Not Working
- Postman has limited SSE support
- Use `/events` endpoint instead for testing
- For real SSE testing, use browser with JavaScript or curl

## Alternative: Using cURL

If you prefer command line:

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Classify intent
curl -X POST http://localhost:8000/api/v1/intent/classify \
  -H "Content-Type: application/json" \
  -d '{"user_text": "Build a CRM"}'

# Generate project
curl -X POST http://localhost:8000/api/v1/project/generate \
  -H "Content-Type: application/json" \
  -d '{
    "user_query": "Build a CRM dashboard",
    "page_type_key": "crm_dashboard"
  }'
```

