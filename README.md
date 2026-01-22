# Gemini V3 Event Router API

AI-powered webpage builder API using Google Gemini models. This project provides a REST API for generating React/Vite/TypeScript webpages based on natural language descriptions.

## 🚀 Features

- **Intent Classification** - Classify user intent (webpage_build, chat, etc.)
- **Page Type Detection** - Automatically detect page type (CRM, E-commerce, Portfolio, etc.)
- **Project Generation** - Generate complete React projects with TypeScript
- **Project Modification** - Modify existing projects based on instructions
- **Event Streaming** - Real-time event streaming via Server-Sent Events (SSE)
- **Questionnaire System** - Gather requirements through interactive questionnaires
- **Multiple Page Types** - Support for 12+ page types with automatic feature detection

## 📋 Quick Start

### Prerequisites

- Python 3.8+
- Google Cloud Project with Vertex AI enabled
- Google Cloud credentials configured

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd gemini_v3_event_router_api

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_LOCATION="global"  # or your preferred location
```

### Running the API

```bash
# Development server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Production server
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

Visit `http://localhost:8000/api/docs` for interactive API documentation.

## 📚 Documentation

- **[API Documentation](./API_README.md)** - Complete API endpoint reference
- **[Event Contract](./events/EVENT_CONTRACT.md)** - Event streaming contract
- **[Page Types](./PAGE_TYPE_FEATURE.md)** - Supported page types and features
- **[Prompts Reference](./PROMPTS_QUICK_REFERENCE.md)** - System prompts quick reference

## 🏗️ Project Structure

```
.
├── api/                    # FastAPI application
│   ├── main.py            # Main FastAPI app
│   ├── models.py          # Pydantic models
│   └── routes/            # API route handlers
├── data/                  # Configuration data
│   ├── page_types_reference.py
│   ├── questionnaire_config.py
│   └── page_categories.py
├── events/                # Event system
│   ├── event_emitter.py
│   ├── event_types.py
│   └── EVENT_CONTRACT.md
├── models/                # Core models
│   ├── gemini_client.py
│   └── json_parser.py
├── router/                # Model routing logic
├── utils/                 # Utility functions
└── app.py                 # Original Streamlit app (legacy)
```

## 🔌 API Endpoints

### Core Endpoints

- `POST /api/v1/intent/classify` - Classify user intent
- `POST /api/v1/page-type/classify` - Classify page type
- `POST /api/v1/query/analyze` - Analyze query detail
- `POST /api/v1/chat` - Chat response
- `POST /api/v1/project/generate` - Generate project
- `POST /api/v1/project/modify` - Modify project
- `GET /api/v1/events/stream` - Stream events (SSE)

See [API_README.md](./API_README.md) for complete documentation.

## 🎯 Supported Page Types

- Landing Page
- CRM Dashboard
- HR Portal
- Inventory Management
- E-commerce Fashion
- Digital Product Store
- Service Marketplace
- Student Portfolio
- Hyperlocal Delivery
- Real Estate Listing
- AI Tutor LMS
- Generic (fallback)

## 🔐 Environment Variables

```bash
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=global
```

## 📦 Dependencies

- FastAPI - Web framework
- Uvicorn - ASGI server
- Pydantic - Data validation
- google-genai - Google Gemini API client
- python-dotenv - Environment variable management

## 🤝 For Frontend/Backend Teams

This API is designed to be consumed by frontend and backend teams:

- **Frontend**: Use REST endpoints for all operations, SSE for real-time updates
- **Backend**: Integrate with your backend services, handle project storage
- **Event Streaming**: Real-time updates via Server-Sent Events

See [API_README.md](./API_README.md) for integration examples.

## 📝 License

[Add your license here]

## 🙏 Contributing

[Add contribution guidelines here]

