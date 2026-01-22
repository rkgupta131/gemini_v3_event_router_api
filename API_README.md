# Webpage Builder API

REST API for AI-powered webpage generation using Gemini models. This API provides endpoints for intent classification, page type detection, project generation, and event streaming.

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION
```

### Running the API

```bash
# Development server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Production server
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API Base URL**: `http://localhost:8000`
- **Interactive Docs**: `http://localhost:8000/api/docs`
- **ReDoc**: `http://localhost:8000/api/redoc`

## 📚 API Endpoints

### Intent Classification

**POST** `/api/v1/intent/classify`

Classify user intent from input text.

**Request:**
```json
{
  "user_text": "I want to build a CRM dashboard",
  "model": "gemini-2.0-flash-lite"  // optional
}
```

**Response:**
```json
{
  "label": "webpage_build",
  "explanation": "User wants to build a webpage",
  "confidence": 0.95,
  "model": "gemini-2.0-flash-lite",
  "metadata": {}
}
```

### Page Type Classification

**POST** `/api/v1/page-type/classify`

Classify the page type from user input.

**Request:**
```json
{
  "user_text": "Build a CRM for my marketing agency"
}
```

**Response:**
```json
{
  "page_type": "crm_dashboard",
  "explanation": "CRM dashboard for customer management",
  "confidence": 0.92,
  "model": "gemini-2.0-flash-lite",
  "metadata": {}
}
```

**GET** `/api/v1/page-type/{page_type_key}`

Get page type reference information.

**GET** `/api/v1/page-types`

List all available page types.

### Query Analysis

**POST** `/api/v1/query/analyze`

Analyze if a query needs follow-up questions.

**Request:**
```json
{
  "user_text": "Build a landing page"
}
```

**Response:**
```json
{
  "needs_followup": true,
  "explanation": "Query needs follow-up questions to gather more details",
  "confidence": 0.85,
  "model": "gemini-2.0-flash-lite"
}
```

### Chat

**POST** `/api/v1/chat`

Generate a chat response for general Q/A.

**Request:**
```json
{
  "user_text": "What is a CRM?"
}
```

**Response:**
```json
{
  "response": "A CRM (Customer Relationship Management) system helps businesses manage...",
  "model": "gemini-2.0-flash-lite"
}
```

### Project Generation

**POST** `/api/v1/project/generate`

Generate a complete webpage project.

**Request:**
```json
{
  "user_query": "Build a CRM dashboard for my marketing agency",
  "page_type_key": "crm_dashboard",  // optional
  "questionnaire_answers": {  // optional
    "business_type": "Marketing Agency",
    "team_size": "Small (2-10 people)"
  },
  "wizard_inputs": {  // optional
    "hero_text": "Welcome to Our CRM",
    "subtext": "Manage your leads efficiently",
    "cta": "Get Started",
    "theme": "Light"
  },
  "project_id": "proj_123",  // optional
  "conversation_id": "conv_456"  // optional
}
```

**Response:**
```json
{
  "project_id": "proj_123",
  "conversation_id": "conv_456",
  "project": {
    "name": "CRM Dashboard",
    "description": "...",
    "files": {
      "src/App.tsx": "...",
      "package.json": "..."
    }
  },
  "files_count": 25,
  "page_type": "crm_dashboard",
  "model_used": "gemini-3-pro-preview",
  "generation_time_seconds": 45.2
}
```

### Project Modification

**POST** `/api/v1/project/modify`

Modify an existing project.

**Request:**
```json
{
  "instruction": "Change the theme to dark mode",
  "project_json": {  // either project_json or project_id
    "project": { ... }
  },
  "project_id": "proj_123"  // optional if project_json provided
}
```

**Response:**
```json
{
  "project_id": "proj_123",
  "modified_project": { ... },
  "complexity": "small",
  "model_used": "gemini-2.0-flash-lite",
  "modification_time_seconds": 12.5
}
```

### Get Project

**GET** `/api/v1/project/{project_id}`

Retrieve a project by ID.

### Questionnaire

**GET** `/api/v1/questionnaire/{page_type_key}`

Get questionnaire for a page type.

**GET** `/api/v1/questionnaire/{page_type_key}/exists`

Check if questionnaire exists.

### Categories

**GET** `/api/v1/categories`

Get all page type categories.

### Events

**GET** `/api/v1/events/stream?project_id=proj_123&conversation_id=conv_456`

Stream events via Server-Sent Events (SSE).

**GET** `/api/v1/events?project_id=proj_123&conversation_id=conv_456`

Get all events (non-streaming).

## 🔄 Typical Workflow

### 1. Classify Intent
```bash
POST /api/v1/intent/classify
{
  "user_text": "I want to build a CRM"
}
```

### 2. Classify Page Type
```bash
POST /api/v1/page-type/classify
{
  "user_text": "I want to build a CRM for my marketing agency"
}
```

### 3. Analyze Query (if needed)
```bash
POST /api/v1/query/analyze
{
  "user_text": "Build a CRM"
}
```

### 4. Get Questionnaire (if needed)
```bash
GET /api/v1/questionnaire/crm_dashboard
```

### 5. Generate Project
```bash
POST /api/v1/project/generate
{
  "user_query": "Build a CRM for my marketing agency",
  "questionnaire_answers": { ... },
  "wizard_inputs": { ... }
}
```

### 6. Stream Events (optional)
```bash
GET /api/v1/events/stream?project_id=proj_123
```

## 📋 Page Types

Supported page types:
- `landing_page` - Marketing/promotional page
- `crm_dashboard` - CRM/Customer management
- `hr_portal` - HR/Employee management
- `inventory_management` - Stock/warehouse management
- `ecommerce_fashion` - Online fashion store
- `digital_product_store` - Digital downloads store
- `service_marketplace` - Two-sided marketplace
- `student_portfolio` - Personal portfolio
- `hyperlocal_delivery` - Food/grocery delivery
- `real_estate_listing` - Property listings
- `ai_tutor_lms` - Learning management system
- `generic` - Generic webpage (fallback)

## 🔐 Environment Variables

Required:
- `GOOGLE_CLOUD_PROJECT` - Your Google Cloud project ID
- `GOOGLE_CLOUD_LOCATION` - Location (default: "global")

Optional:
- `LOG_LEVEL` - Logging level (default: "INFO")

## 🧪 Testing

```bash
# Test health endpoint
curl http://localhost:8000/api/v1/health

# Test intent classification
curl -X POST http://localhost:8000/api/v1/intent/classify \
  -H "Content-Type: application/json" \
  -d '{"user_text": "I want to build a website"}'
```

## 📖 Frontend Integration

### Using Fetch API

```javascript
// Classify intent
const response = await fetch('http://localhost:8000/api/v1/intent/classify', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ user_text: 'Build a CRM' })
});
const data = await response.json();
```

### Using EventSource (SSE)

```javascript
const eventSource = new EventSource(
  'http://localhost:8000/api/v1/events/stream?project_id=proj_123'
);

eventSource.onmessage = (event) => {
  const eventData = JSON.parse(event.data);
  console.log('Event:', eventData);
  
  if (eventData === '[DONE]') {
    eventSource.close();
  }
};
```

## 🏗️ Backend Integration

### Python Example

```python
import requests

# Generate project
response = requests.post(
    'http://localhost:8000/api/v1/project/generate',
    json={
        'user_query': 'Build a CRM dashboard',
        'wizard_inputs': {
            'hero_text': 'Welcome',
            'theme': 'Light'
        }
    }
)

project = response.json()
print(f"Generated project with {project['files_count']} files")
```

## 📝 Notes for Frontend/Backend Teams

### Frontend Team
- Use `/api/v1/events/stream` for real-time updates during project generation
- All endpoints return JSON responses
- Use the interactive docs at `/api/docs` for testing
- Event streaming uses Server-Sent Events (SSE) format

### Backend Team
- Project files are saved to `output/` and `modified_output/` directories
- Events are logged to `events.jsonl` file
- All models support fallback to more capable models if needed
- Project generation can take 20-150 seconds depending on complexity

## 🐛 Error Handling

All endpoints return standard HTTP status codes:
- `200` - Success
- `400` - Bad Request
- `404` - Not Found
- `500` - Internal Server Error

Error response format:
```json
{
  "error": "Error message",
  "detail": "Detailed error information",
  "code": "ERROR_CODE"
}
```

## 📄 License

[Add your license here]

