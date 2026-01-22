"""
Project Generation and Modification Routes
"""

import os
import json
import time
from fastapi import APIRouter, HTTPException, BackgroundTasks
from api.models import (
    ProjectGenerationRequest,
    ProjectGenerationResponse,
    ProjectModificationRequest,
    ProjectModificationResponse,
    ProjectResponse,
    ModelInfo
)
from api.utils import get_model_info
from models.gemini_client import (
    generate_text,
    parse_project_json,
    save_project_files,
    classify_page_type,
    analyze_query_detail,
    classify_modification_complexity,
    get_model_for_complexity,
    get_smaller_model
)
from data.page_types_reference import get_page_type_by_key
from data.questionnaire_config import has_questionnaire
from events import EventEmitter
from utils.event_logger import get_event_logger

router = APIRouter()

OUTPUT_DIR = "output"
MODIFIED_DIR = "modified_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(MODIFIED_DIR, exist_ok=True)


def get_latest_project():
    """Get the latest project from output directories"""
    if os.path.exists(MODIFIED_DIR):
        versions = sorted(
            d for d in os.listdir(MODIFIED_DIR) if d.startswith("project_")
        )
        if versions:
            path = os.path.join(MODIFIED_DIR, versions[-1], "project.json")
            if os.path.exists(path):
                with open(path) as f:
                    return path, json.load(f)["project"]

    base = os.path.join(OUTPUT_DIR, "project.json")
    if os.path.exists(base):
        with open(base) as f:
            return base, json.load(f)["project"]

    return None, None


@router.post("/project/generate", response_model=ProjectGenerationResponse)
async def generate_project(request: ProjectGenerationRequest):
    """
    Generate a complete webpage project based on user requirements.
    
    This is the main endpoint for project generation. It:
    1. Classifies page type if not provided
    2. Analyzes query detail
    3. Generates the project JSON using appropriate model
    4. Saves project files
    5. Returns the complete project structure
    """
    try:
        start_time = time.time()
        
        # Initialize event system
        event_logger = get_event_logger()
        project_id = request.project_id or f"proj_{int(time.time())}"
        conversation_id = request.conversation_id or f"conv_{int(time.time())}"
        
        emitter = EventEmitter(
            project_id=project_id,
            conversation_id=conversation_id,
            callback=lambda event: event_logger.log_event(event)
        )
        
        # Emit initial events
        emitter.emit_chat_message("Starting project generation...")
        
        # Track all models used in the pipeline
        models_used_list = []
        
        # Classify page type if not provided
        page_type_key = request.page_type_key
        page_type_model = None
        if not page_type_key:
            page_type_key, page_type_meta = classify_page_type(request.user_query)
            page_type_model = page_type_meta.get("model", get_smaller_model())
            models_used_list.append(ModelInfo(**get_model_info(page_type_model)))
        
        page_type_config = get_page_type_by_key(page_type_key)
        
        # Analyze query detail
        query_model = get_smaller_model()
        needs_followup, _ = analyze_query_detail(request.user_query, model=query_model)
        models_used_list.append(ModelInfo(**get_model_info(query_model)))
        
        # Build generation prompt
        base_prompt = (
            "Return exactly one JSON object describing a React+Vite+TypeScript project. "
            "Schema must be: {\"project\": {\"name\": string, \"description\": string, \"files\": {...}, \"dirents\": {...}, \"meta\": {...}}}. "
            "Files should be strings (escaped) or objects with a 'content' key. "
            "Return only the JSON object and nothing else.\n\n"
        )
        
        # Add page type specific requirements
        if page_type_config:
            base_prompt += f"\n=== PAGE TYPE: {page_type_config['name']} ({page_type_config['category']}) ===\n"
            base_prompt += f"Target User: {page_type_config['end_user']}\n\n"
            
            base_prompt += "REQUIRED CORE PAGES:\n"
            for i, page in enumerate(page_type_config['core_pages'], 1):
                base_prompt += f"{i}. {page}\n"
            
            base_prompt += "\n\nREQUIRED COMPONENTS TO IMPLEMENT:\n"
            for i, component in enumerate(page_type_config['components'], 1):
                base_prompt += f"{i}. **{component['name']}**: {component['description']}\n"
        
        # Add questionnaire answers if available
        if request.questionnaire_answers:
            base_prompt += "\n=== USER REQUIREMENTS (from questionnaire) ===\n"
            for key, value in request.questionnaire_answers.items():
                if isinstance(value, list):
                    base_prompt += f"- {key}: {', '.join(value)}\n"
                else:
                    base_prompt += f"- {key}: {value}\n"
        
        # Add wizard inputs
        wizard_inputs = request.wizard_inputs or {}
        final_prompt = base_prompt + "USER_FIELDS:\n" + json.dumps(wizard_inputs, ensure_ascii=False)
        
        # Determine model based on page type complexity
        complex_page_types = ['crm_dashboard', 'hr_portal', 'inventory_management', 'ai_tutor_lms']
        medium_page_types = ['ecommerce_fashion', 'service_marketplace', 'hyperlocal_delivery', 'real_estate_listing']
        
        if page_type_key in complex_page_types:
            webpage_model = "gemini-3-pro-preview"
        elif page_type_key in medium_page_types:
            webpage_model = "gemini-2.0-flash"
        else:
            webpage_model = "gemini-2.0-flash"
        
        emitter.emit_progress_init(
            steps=[
                {"id": "prepare", "label": "Preparing", "status": "in_progress"},
                {"id": "generate", "label": "Generating", "status": "pending"},
                {"id": "parse", "label": "Parsing", "status": "pending"},
                {"id": "save", "label": "Saving", "status": "pending"},
            ],
            mode="inline"
        )
        
        emitter.emit_progress_update("prepare", "completed")
        emitter.emit_progress_update("generate", "in_progress")
        emitter.emit_thinking_start()
        
        # Generate project
        output = generate_text(final_prompt, model=webpage_model)
        elapsed_time = time.time() - start_time
        
        emitter.emit_thinking_end(duration_ms=int(elapsed_time * 1000))
        emitter.emit_progress_update("generate", "completed")
        emitter.emit_progress_update("parse", "in_progress")
        
        # Parse project JSON
        project = parse_project_json(output)
        
        if not project:
            emitter.emit_progress_update("parse", "failed")
            emitter.emit_error(
                scope="validation",
                message="Failed to parse JSON from model output",
                details="The model may have returned invalid JSON or non-JSON content.",
                actions=["retry", "ask_user"]
            )
            emitter.emit_stream_failed()
            raise HTTPException(
                status_code=500,
                detail="Failed to parse project JSON from model output"
            )
        
        emitter.emit_progress_update("parse", "completed")
        emitter.emit_progress_update("save", "in_progress")
        
        # Save project files
        project_json_path = f"{OUTPUT_DIR}/project.json"
        with open(project_json_path, "w") as f:
            json.dump({"project": project}, f, indent=2)
        
        save_project_files(project, f"{OUTPUT_DIR}/project")
        
        emitter.emit_progress_update("save", "completed")
        emitter.emit_chat_message("Base project generated successfully!")
        emitter.emit_stream_complete()
        
        files_count = len(project.get('files', {}))
        
        # Add the main generation model to models_used_list
        models_used_list.append(ModelInfo(**get_model_info(webpage_model)))
        
        return ProjectGenerationResponse(
            project_id=project_id,
            conversation_id=conversation_id,
            project=project,
            files_count=files_count,
            page_type=page_type_key,
            model_used=webpage_model,  # Keep for backward compatibility
            model_info=ModelInfo(**get_model_info(webpage_model)),
            models_used=models_used_list,
            generation_time_seconds=elapsed_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Project generation failed: {str(e)}")


@router.post("/project/modify", response_model=ProjectModificationResponse)
async def modify_project(request: ProjectModificationRequest):
    """
    Modify an existing project based on user instructions.
    
    This endpoint:
    1. Classifies modification complexity
    2. Selects appropriate model
    3. Generates modified project JSON
    4. Returns the modified project
    """
    try:
        start_time = time.time()
        
        # Get base project
        if request.project_json:
            base_project = request.project_json
        elif request.project_id:
            # Load from saved project
            base_path, base_project = get_latest_project()
            if not base_project:
                raise HTTPException(
                    status_code=404,
                    detail=f"Project not found: {request.project_id}"
                )
        else:
            raise HTTPException(
                status_code=400,
                detail="Either project_json or project_id must be provided"
            )
        
        # Classify modification complexity
        complexity, complexity_meta = classify_modification_complexity(request.instruction)
        mod_model = get_model_for_complexity(complexity)
        
        # Build modification prompt
        mod_prompt = f"""You are a JSON project modifier. You MUST return ONLY valid JSON, nothing else.

CRITICAL REQUIREMENTS:
1. Return ONLY a JSON object in this exact format: {{"project": {{...}}}}
2. The JSON must match the schema of the base project exactly
3. Modify ONLY what the user requests, keep everything else unchanged
4. Do NOT include any markdown, code blocks, explanations, or text outside the JSON
5. The output must be parseable JSON that starts with {{ and ends with }}

Base project JSON:
{json.dumps({"project": base_project}, indent=2)}

User modification request:
{request.instruction}

IMPORTANT: Return ONLY the complete modified project JSON. No markdown, no code blocks, no explanations. Just the raw JSON starting with {{ and ending with }}."""
        
        # Generate modification
        mod_out = generate_text(mod_prompt, model=mod_model)
        mod_project = parse_project_json(mod_out)
        
        # Fallback to pro-preview if parsing failed
        if not mod_project and mod_model != "gemini-3-pro-preview":
            mod_out = generate_text(mod_prompt, model="gemini-3-pro-preview")
            mod_project = parse_project_json(mod_out)
            mod_model = "gemini-3-pro-preview"
        
        if not mod_project:
            raise HTTPException(
                status_code=500,
                detail="Failed to parse modified project JSON"
            )
        
        # Save modified project
        project_id = request.project_id or f"proj_{int(time.time())}"
        version = f"project_{int(time.time())}"
        dest = os.path.join(MODIFIED_DIR, version)
        os.makedirs(dest, exist_ok=True)
        
        project_json_path = os.path.join(dest, "project.json")
        with open(project_json_path, "w") as f:
            json.dump({"project": mod_project}, f, indent=2)
        
        save_project_files(mod_project, os.path.join(dest, "project"))
        
        elapsed_time = time.time() - start_time
        
        return ProjectModificationResponse(
            project_id=project_id,
            modified_project=mod_project,
            complexity=complexity,
            model_used=mod_model,  # Keep for backward compatibility
            model_info=ModelInfo(**get_model_info(mod_model)),
            modification_time_seconds=elapsed_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Project modification failed: {str(e)}")


@router.get("/project/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str):
    """
    Get a project by ID.
    
    Currently returns the latest project from output directories.
    """
    try:
        base_path, base_project = get_latest_project()
        
        if not base_project:
            raise HTTPException(
                status_code=404,
                detail=f"Project not found: {project_id}"
            )
        
        return ProjectResponse(
            project_id=project_id,
            project=base_project
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get project: {str(e)}")

