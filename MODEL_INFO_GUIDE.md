# Model Information Guide

## Overview

The API now returns standardized model information in all responses to help the frontend track which models are being used for different operations.

## Model Information Structure

All API responses now include a `model_info` object with the following structure:

```json
{
  "model_family": "Gemini",
  "model_name": "gemini-2.0-flash-lite"
}
```

### Fields

- **`model_family`**: Always `"Gemini"` for this API (previously was `"Anthropic"` for Claude models)
- **`model_name`**: The specific model identifier used (e.g., `"gemini-2.0-flash-lite"`, `"gemini-2.0-flash"`, `"gemini-3-pro-preview"`)

## Model Selection Strategy

Different models are used for different operations based on complexity:

### 1. Intent Classification
- **Model**: `gemini-2.0-flash-lite` (fast, cost-effective)
- **Use Case**: Quick classification of user intent

### 2. Page Type Classification
- **Model**: `gemini-2.0-flash-lite` (fast, cost-effective)
- **Use Case**: Determining what type of page to build

### 3. Query Analysis
- **Model**: `gemini-2.0-flash-lite` (fast, cost-effective)
- **Use Case**: Analyzing if query needs follow-up questions

### 4. Chat Responses
- **Model**: `gemini-2.0-flash-lite` (fast, cost-effective)
- **Use Case**: General Q/A conversations

### 5. Project Generation
- **Simple pages** (landing_page, student_portfolio): `gemini-2.0-flash`
- **Medium complexity** (ecommerce, marketplace): `gemini-2.0-flash`
- **Complex pages** (CRM, HR portal, inventory): `gemini-3-pro-preview`

### 6. Project Modification
- **Small changes**: `gemini-2.0-flash-lite`
- **Medium changes**: `gemini-2.0-flash-lite`
- **Complex changes**: `gemini-3-pro-preview`

## API Response Examples

### Intent Classification Response

```json
{
  "label": "webpage_build",
  "explanation": "User wants to build a webpage",
  "confidence": 0.95,
  "model": "gemini-2.0-flash-lite",
  "model_info": {
    "model_family": "Gemini",
    "model_name": "gemini-2.0-flash-lite"
  },
  "metadata": {}
}
```

### Project Generation Response

```json
{
  "project_id": "proj_123",
  "conversation_id": "conv_456",
  "project": { ... },
  "files_count": 25,
  "page_type": "crm_dashboard",
  "model_used": "gemini-3-pro-preview",
  "model_info": {
    "model_family": "Gemini",
    "model_name": "gemini-3-pro-preview"
  },
  "models_used": [
    {
      "model_family": "Gemini",
      "model_name": "gemini-2.0-flash-lite"
    },
    {
      "model_family": "Gemini",
      "model_name": "gemini-2.0-flash-lite"
    },
    {
      "model_family": "Gemini",
      "model_name": "gemini-3-pro-preview"
    }
  ],
  "generation_time_seconds": 45.2
}
```

## Frontend Integration

### Handling Model Information

The frontend can now track which models are used throughout the pipeline:

```javascript
// Example: Intent classification
const intentResponse = await fetch('/api/v1/intent/classify', {
  method: 'POST',
  body: JSON.stringify({ user_text: 'Build a CRM' })
});

const intentData = await intentResponse.json();
console.log(`Intent classified using: ${intentData.model_info.model_family} - ${intentData.model_info.model_name}`);

// Example: Project generation
const projectResponse = await fetch('/api/v1/project/generate', {
  method: 'POST',
  body: JSON.stringify({ user_query: 'Build a CRM dashboard' })
});

const projectData = await projectResponse.json();
console.log(`Main model: ${projectData.model_info.model_name}`);
console.log(`All models used:`, projectData.models_used);
```

### Backward Compatibility

The `model` field is still included in all responses for backward compatibility, but the frontend should migrate to using `model_info` for better structure.

## Migration from Claude

If you were previously using Claude models, the response structure is similar:

**Before (Claude):**
```json
{
  "model_family": "Anthropic",
  "model_name": "claude-opus-4-5-20251101"
}
```

**Now (Gemini):**
```json
{
  "model_family": "Gemini",
  "model_name": "gemini-3-pro-preview"
}
```

The frontend can handle both formats by checking `model_family`:

```javascript
if (response.model_info.model_family === "Gemini") {
  // Handle Gemini model
} else if (response.model_info.model_family === "Anthropic") {
  // Handle Claude model (if still supported)
}
```

## Model Name Reference

| Model Name | Use Case | Speed | Cost |
|------------|----------|-------|------|
| `gemini-2.0-flash-lite` | Classification, simple tasks | Fast | Low |
| `gemini-2.0-flash` | Medium complexity generation | Fast | Medium |
| `gemini-3-pro-preview` | Complex generation, large projects | Slower | Higher |

