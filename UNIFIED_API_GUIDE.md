# Unified API Endpoint Guide

## Overview

The API now provides a **single unified endpoint** `/api/v1/execute` that handles all operations. Instead of calling different endpoints for different tasks, you can use this one endpoint with different `action` parameters.

## Endpoint

```
POST /api/v1/execute
```

## Request Format

```json
{
  "action": "action_name",
  "user_text": "...",
  "user_query": "...",
  // ... other parameters based on action
}
```

## Supported Actions

### 1. `classify_intent`
Classify user intent (webpage_build, chat, greeting_only, illegal, other)

**Request:**
```json
{
  "action": "classify_intent",
  "user_text": "I want to build a CRM dashboard"
}
```

**Response:**
```json
{
  "action": "classify_intent",
  "success": true,
  "data": {
    "label": "webpage_build",
    "explanation": "User wants to build a webpage",
    "confidence": 0.95,
    "model": "gemini-2.0-flash-lite",
    "model_info": {
      "model_family": "Gemini",
      "model_name": "gemini-2.0-flash-lite"
    }
  }
}
```

### 2. `classify_page_type`
Classify the page type from user input

**Request:**
```json
{
  "action": "classify_page_type",
  "user_text": "Build a CRM dashboard for my marketing agency"
}
```

**Response:**
```json
{
  "action": "classify_page_type",
  "success": true,
  "data": {
    "page_type": "crm_dashboard",
    "explanation": "CRM dashboard for customer management",
    "confidence": 0.92,
    "model_info": {
      "model_family": "Gemini",
      "model_name": "gemini-2.0-flash-lite"
    }
  }
}
```

### 3. `analyze_query`
Analyze if a query needs follow-up questions

**Request:**
```json
{
  "action": "analyze_query",
  "user_text": "Build a landing page"
}
```

**Response:**
```json
{
  "action": "analyze_query",
  "success": true,
  "data": {
    "needs_followup": true,
    "explanation": "Query needs follow-up questions to gather more details",
    "confidence": 0.85,
    "model_info": {
      "model_family": "Gemini",
      "model_name": "gemini-2.0-flash-lite"
    }
  }
}
```

### 4. `chat`
Get a chat response for general Q/A

**Request:**
```json
{
  "action": "chat",
  "user_text": "What is a CRM?"
}
```

**Response:**
```json
{
  "action": "chat",
  "success": true,
  "data": {
    "response": "A CRM (Customer Relationship Management) system helps...",
    "model_info": {
      "model_family": "Gemini",
      "model_name": "gemini-2.0-flash-lite"
    }
  }
}
```

### 5. `generate_project`
Generate a complete webpage project

**Request:**
```json
{
  "action": "generate_project",
  "user_query": "Build a CRM dashboard for my marketing agency",
  "page_type_key": "crm_dashboard",
  "questionnaire_answers": {
    "business_type": "Marketing Agency",
    "team_size": "Small (2-10 people)"
  },
  "wizard_inputs": {
    "hero_text": "CRM Dashboard",
    "subtext": "Manage your leads efficiently",
    "cta": "Get Started",
    "theme": "Light"
  },
  "project_id": "proj_123",
  "conversation_id": "conv_456"
}
```

**Response:**
```json
{
  "action": "generate_project",
  "success": true,
  "data": {
    "project_id": "proj_123",
    "conversation_id": "conv_456",
    "project": { ... },
    "files_count": 25,
    "page_type": "crm_dashboard",
    "model_info": {
      "model_family": "Gemini",
      "model_name": "gemini-3-pro-preview"
    },
    "generation_time_seconds": 45.2
  }
}
```

### 6. `modify_project`
Modify an existing project

**Request:**
```json
{
  "action": "modify_project",
  "instruction": "Change the theme to dark mode",
  "project_id": "proj_123"
}
```

**Response:**
```json
{
  "action": "modify_project",
  "success": true,
  "data": {
    "project_id": "proj_123",
    "modified_project": { ... },
    "complexity": "small",
    "model_info": {
      "model_family": "Gemini",
      "model_name": "gemini-2.0-flash-lite"
    },
    "modification_time_seconds": 12.5
  }
}
```

### 7. `get_questionnaire`
Get questionnaire for a page type

**Request:**
```json
{
  "action": "get_questionnaire",
  "page_type_key": "crm_dashboard"
}
```

**Response:**
```json
{
  "action": "get_questionnaire",
  "success": true,
  "data": {
    "page_type": "crm_dashboard",
    "questions": [
      {
        "id": "business_type",
        "question": "What type of business is this CRM for?",
        "type": "radio",
        "options": [...]
      }
    ]
  }
}
```

### 8. `get_categories`
Get all page type categories

**Request:**
```json
{
  "action": "get_categories"
}
```

**Response:**
```json
{
  "action": "get_categories",
  "success": true,
  "data": {
    "categories": {
      "crm_dashboard": {
        "display_name": "CRM Dashboard",
        "description": "...",
        "icon": "📊",
        "examples": "..."
      },
      ...
    }
  }
}
```

### 9. `get_page_type`
Get page type reference information

**Request:**
```json
{
  "action": "get_page_type",
  "page_type_key": "crm_dashboard"
}
```

**Response:**
```json
{
  "action": "get_page_type",
  "success": true,
  "data": {
    "page_type": {
      "name": "Agency CRM",
      "category": "CRM Dashboard",
      "core_pages": [...],
      "components": [...]
    },
    "available_types": ["crm_dashboard", "hr_portal", ...]
  }
}
```

## Error Response

If an action fails:

```json
{
  "action": "classify_intent",
  "success": false,
  "data": {},
  "error": "user_text is required for classify_intent"
}
```

## Complete Workflow Example

### Step 1: Classify Intent
```bash
curl -X POST http://localhost:8000/api/v1/execute \
  -H "Content-Type: application/json" \
  -d '{
    "action": "classify_intent",
    "user_text": "I want to build a CRM"
  }'
```

### Step 2: Classify Page Type
```bash
curl -X POST http://localhost:8000/api/v1/execute \
  -H "Content-Type: application/json" \
  -d '{
    "action": "classify_page_type",
    "user_text": "Build a CRM dashboard"
  }'
```

### Step 3: Get Questionnaire
```bash
curl -X POST http://localhost:8000/api/v1/execute \
  -H "Content-Type: application/json" \
  -d '{
    "action": "get_questionnaire",
    "page_type_key": "crm_dashboard"
  }'
```

### Step 4: Generate Project
```bash
curl -X POST http://localhost:8000/api/v1/execute \
  -H "Content-Type: application/json" \
  -d '{
    "action": "generate_project",
    "user_query": "Build a CRM dashboard",
    "page_type_key": "crm_dashboard",
    "questionnaire_answers": {
      "business_type": "Marketing Agency",
      "team_size": "Small (2-10 people)"
    }
  }'
```

### Step 5: Stream Events
```bash
curl -N "http://localhost:8000/api/v1/stream?project_id=proj_123&conversation_id=conv_456"
```

## Benefits

1. **Single Endpoint**: One endpoint for all operations
2. **Consistent Format**: All responses follow the same structure
3. **Easy Integration**: Frontend only needs to know one endpoint
4. **Type Safety**: All actions validated with Pydantic models
5. **Backward Compatible**: Individual endpoints still available

## Notes

- The `/api/v1/stream` endpoint remains separate for event streaming (SSE)
- Individual endpoints (`/api/v1/intent/classify`, etc.) are still available for backward compatibility
- All actions return the same response structure with `action`, `success`, `data`, and optional `error` fields

