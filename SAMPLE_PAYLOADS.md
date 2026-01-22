# Sample API Payloads

## Action Auto-Detection

**The API automatically detects the action from user input using LLM intent classification.**
- `action` field is **optional** - if not provided, it will be auto-detected
- The detected action is **always returned in the response**
- Action detection uses intent classification to determine if user wants to:
  - Build a webpage → `generate_project`
  - Modify a project → `modify_project` (if modification keywords + project_id/project_json)
  - General chat/Q&A → `chat`

## Project Generation with model_family

### Using model_family (Recommended) - Action Auto-Detected

```json
{
  "user_query": "Generate a multi-page fitness tracking web application with workout logging, progress charts, and user profiles",
  "model_family": "Anthropic",
  "project_id": "proj_12345",
  "conversation_id": "conv_12345"
}
```

**Response will include:**
```json
{
  "action": "generate_project",
  "success": true,
  "data": {
    "project_id": "proj_12345",
    "project": {...},
    "model_info": {
      "model_family": "Anthropic",
      "model_name": "claude-opus-4-5-20251101"
    }
  }
}
```

### Using model_name (model_family will be inferred)

```json
{
  "user_query": "Generate a multi-page fitness tracking web application with workout logging, progress charts, and user profiles",
  "model_name": "claude-opus-4-5-20251101",
  "project_id": "proj_12345",
  "conversation_id": "conv_12345"
}
```

### Full payload with all optional fields

```json
{
  "action": "generate_project",
  "user_query": "Generate a multi-page fitness tracking web application with workout logging, progress charts, and user profiles",
  "model_family": "Anthropic",
  "page_type_key": "fitness_app",
  "questionnaire_answers": {
    "target_audience": ["fitness enthusiasts", "athletes"],
    "features": ["workout logging", "progress tracking", "social sharing"]
  },
  "wizard_inputs": {
    "hero_text": "Track Your Fitness Journey",
    "subtext": "Log workouts, monitor progress, and achieve your goals",
    "cta": "Get Started",
    "theme": "modern"
  },
  "project_id": "proj_12345",
  "conversation_id": "conv_12345"
}
```

## Supported model_family values

- `"Gemini"` - Uses Gemini models (default)
- `"Anthropic"` - Uses Claude models
- `"OpenAI"` - Uses GPT models

## Auto-Detected Actions

The following actions are automatically detected from user input:

- `"generate_project"` - User wants to build/create a webpage/project
- `"modify_project"` - User wants to modify/change/update an existing project (requires project_id or project_json)
- `"chat"` - General Q/A, greetings, or other conversations

## Example: Project Generation (Auto-Detected)

```json
{
  "user_query": "I want to build a CRM system",
  "model_family": "Anthropic"
}
```

**Response:**
```json
{
  "action": "generate_project",
  "success": true,
  "data": {...}
}
```

## Example: Project Modification (Auto-Detected)

```json
{
  "user_text": "Add a dark mode toggle to the navigation bar",
  "project_id": "proj_12345",
  "model_family": "Anthropic"
}
```

**Response:**
```json
{
  "action": "modify_project",
  "success": true,
  "data": {...}
}
```

## Example: Chat (Auto-Detected)

```json
{
  "user_text": "What is a landing page?",
  "model_family": "Anthropic"
}
```

**Response:**
```json
{
  "action": "chat",
  "success": true,
  "data": {
    "response": "A landing page is...",
    "model_info": {
      "model_family": "Anthropic",
      "model_name": "claude-haiku-4-5-20251001"
    }
  }
}
```

## Optional: Manual Action Override

You can still manually specify the action if needed:

```json
{
  "action": "generate_project",
  "user_query": "Build a fitness app",
  "model_family": "Anthropic"
}
```

