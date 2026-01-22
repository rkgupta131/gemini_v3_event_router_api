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
    generate_text as gemini_generate_text,
    parse_project_json,
    save_project_files
)
# Import other providers' generate_text functions with aliases to avoid name conflicts
try:
    from models.claude_client import generate_text as claude_generate_text
except ImportError:
    claude_generate_text = None
try:
    from models.gpt_client import generate_text as gpt_generate_text
except ImportError:
    gpt_generate_text = None
from models.unified_client import (
    classify_page_type_unified,
    analyze_query_detail_unified,
    classify_modification_complexity_unified
)
from router.router_config import get_router_model, get_main_model, get_modification_model, get_provider
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
        
        # Get model_family from request (default to Gemini)
        from router.router_config import normalize_model_family
        model_family = request.model_family or "Gemini"
        model_key = normalize_model_family(model_family)
        
        # Initialize event system
        event_logger = get_event_logger()
        project_id = request.project_id or f"proj_{int(time.time())}"
        conversation_id = request.conversation_id or f"conv_{int(time.time())}"
        
        emitter = EventEmitter(
            project_id=project_id,
            conversation_id=conversation_id,
            callback=lambda event: event_logger.log_event(event),
            model_name=model_family  # EventEmitter stores model_family
        )
        
        # Emit initial events
        emitter.emit_chat_message("Starting project generation...")
        
        # Track all models used in the pipeline
        models_used_list = []
        
        # Classify page type if not provided
        page_type_key = request.page_type_key
        page_type_model = None
        if not page_type_key:
            page_type_key, page_type_meta = classify_page_type_unified(request.user_query, model_name=model_key)
            page_type_model = page_type_meta.get("model", get_router_model(model_family))
            models_used_list.append(ModelInfo(**get_model_info(page_type_model)))
        
        page_type_config = get_page_type_by_key(page_type_key)
        
        # Analyze query detail
        query_model = get_router_model(model_family)
        needs_followup, confidence = analyze_query_detail_unified(request.user_query, model_name=model_key)
        models_used_list.append(ModelInfo(**get_model_info(query_model)))
        
        # Handle follow-up questions if needed
        # If needs_followup is True and no questionnaire_answers provided, emit questions as events
        # But continue with generation (non-blocking for REST API)
        if needs_followup and not request.questionnaire_answers:
            from data.questionnaire_config import get_questionnaire, has_questionnaire
            
            if has_questionnaire(page_type_key):
                questionnaire = get_questionnaire(page_type_key)
                emitter.emit_chat_message("I need to gather some additional information to create the perfect page for you.")
                
                # Emit questions as events (non-blocking - API continues)
                type_mapping = {
                    "radio": "mcq",
                    "multiselect": "multi_select",
                    "open_ended": "open_ended"
                }
                
                for question_data in questionnaire.get("questions", []):
                    q_id = question_data.get("id", f"q_{len(questionnaire.get('questions', []))}")
                    question_type = type_mapping.get(question_data.get("type", "radio"), "mcq")
                    label = question_data.get("question", "")
                    is_skippable = True  # Questions are skippable in API context
                    
                    content = {}
                    if question_type in ["mcq", "multi_select"]:
                        content["options"] = question_data.get("options", [])
                    elif question_type == "open_ended":
                        content["placeholder"] = question_data.get("placeholder", "Enter your answer...")
                    
                    emitter.emit_chat_question(
                        q_id=q_id,
                        question_type=question_type,
                        label=label,
                        is_skippable=is_skippable,
                        content=content
                    )
                
                emitter.emit_chat_message("Proceeding with generation using defaults. You can provide questionnaire_answers in a follow-up request for more customization.")
        
        # Build generation prompt - make it more explicit for Claude/GPT
        provider = get_provider(model_family)
        if provider == "gemini":
            base_prompt = (
                "Return exactly one JSON object describing a React+Vite+TypeScript project. "
                "Schema must be: {\"project\": {\"name\": string, \"description\": string, \"files\": {...}, \"dirents\": {...}, \"meta\": {...}}}. "
                "Files should be strings (escaped) or objects with a 'content' key. "
                "Return only the JSON object and nothing else.\n\n"
            )
        else:
            # More explicit prompt for Claude/GPT to ensure JSON-only output
            base_prompt = (
                "CRITICAL: You MUST return ONLY valid JSON. No markdown, no code blocks, no explanations, no text before or after.\n\n"
                "Return exactly one JSON object describing a React+Vite+TypeScript project. "
                "Schema must be: {\"project\": {\"name\": string, \"description\": string, \"files\": {...}, \"dirents\": {...}, \"meta\": {...}}}. "
                "Files should be strings (escaped) or objects with a 'content' key.\n\n"
                "IMPORTANT: Your response must start with { and end with }. Do NOT wrap in ```json or markdown. Return ONLY the raw JSON object.\n\n"
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
        
        # Use main_model for generation (based on model_family)
        webpage_model = get_main_model(model_family)
        
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
        
        # Generate project - route to appropriate provider
        # Use higher max_tokens for project generation (projects can be large)
        if provider == "gemini":
            output = gemini_generate_text(final_prompt, model=webpage_model)
        elif provider == "anthropic":
            if claude_generate_text is None:
                raise HTTPException(status_code=500, detail="Claude client not available")
            output = claude_generate_text(final_prompt, model=webpage_model, max_tokens=16384)
        elif provider == "openai":
            if gpt_generate_text is None:
                raise HTTPException(status_code=500, detail="GPT client not available")
            output = gpt_generate_text(final_prompt, model=webpage_model, max_tokens=16384)
        else:
            output = gemini_generate_text(final_prompt, model=webpage_model)
        elapsed_time = time.time() - start_time
        
        emitter.emit_thinking_end(duration_ms=int(elapsed_time * 1000))
        emitter.emit_progress_update("generate", "completed")
        emitter.emit_progress_update("parse", "in_progress")
        
        # Parse project JSON
        project = parse_project_json(output)
        
        # If parsing failed, try with a stricter prompt (retry once)
        if not project and provider != "gemini":
            print(f"[PROJECT_GEN] First parse attempt failed. Output length: {len(output)} chars")
            print(f"[PROJECT_GEN] Output preview (first 500 chars): {output[:500]}")
            print(f"[PROJECT_GEN] Output preview (last 500 chars): {output[-500:]}")
            
            # Check if JSON appears incomplete (doesn't end with })
            if not output.strip().endswith('}'):
                print("[PROJECT_GEN] WARNING: Output doesn't end with '}', might be truncated!")
                emitter.emit_chat_message("Response appears truncated. Retrying with higher token limit...")
            
            emitter.emit_chat_message("Retrying with stricter JSON prompt...")
            
            # Create a stricter prompt
            strict_prompt = (
                "You are a JSON generator. Return ONLY valid JSON, nothing else.\n\n"
                "CRITICAL RULES:\n"
                "1. Start your response with {\n"
                "2. End your response with }\n"
                "3. Do NOT include markdown code blocks (no ```json or ```)\n"
                "4. Do NOT include any text before or after the JSON\n"
                "5. Do NOT include explanations or comments\n"
                "6. Ensure all strings are properly escaped (use \\n for newlines, \\\" for quotes)\n"
                "7. Ensure the JSON is complete and valid\n\n"
            ) + final_prompt
            
            # Retry generation with higher token limit
            if provider == "anthropic":
                if claude_generate_text is None:
                    raise HTTPException(status_code=500, detail="Claude client not available")
                output = claude_generate_text(strict_prompt, model=webpage_model, max_tokens=16384)
            elif provider == "openai":
                if gpt_generate_text is None:
                    raise HTTPException(status_code=500, detail="GPT client not available")
                output = gpt_generate_text(strict_prompt, model=webpage_model, max_tokens=16384)
            else:
                # Fallback to gemini client (shouldn't happen due to condition, but safe)
                output = gemini_generate_text(strict_prompt, model=webpage_model)
            
            project = parse_project_json(output)
        
        if not project:
            # Log the actual output for debugging
            output_preview = output[:1000] if output else "No output received"
            output_end = output[-500:] if output and len(output) > 500 else output
            print(f"[PROJECT_GEN] Parse failed. Model: {webpage_model}, Provider: {provider}")
            print(f"[PROJECT_GEN] Output length: {len(output) if output else 0} characters")
            print(f"[PROJECT_GEN] Output preview (first 1000 chars): {output_preview}")
            print(f"[PROJECT_GEN] Output preview (last 500 chars): {output_end}")
            
            # Try to get more detailed error from the parser
            try:
                # Try to find where JSON breaks
                first_brace = output.find('{')
                last_brace = output.rfind('}')
                if first_brace != -1 and last_brace != -1:
                    json_candidate = output[first_brace:last_brace+1]
                    json.loads(json_candidate)  # This will raise with specific error
            except json.JSONDecodeError as e:
                print(f"[PROJECT_GEN] JSON decode error at position {e.pos}: {e.msg}")
                error_context_start = max(0, e.pos - 100)
                error_context_end = min(len(output), e.pos + 100)
                print(f"[PROJECT_GEN] Error context: {output[error_context_start:error_context_end]}")
            
            emitter.emit_progress_update("parse", "failed")
            emitter.emit_error(
                scope="validation",
                message="Failed to parse JSON from model output",
                details=f"The model returned output that could not be parsed as JSON. Output length: {len(output) if output else 0} chars. Preview: {output_preview[:200]}...",
                actions=["retry", "ask_user"]
            )
            emitter.emit_stream_failed()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse project JSON from model output. Model: {webpage_model}. Output length: {len(output) if output else 0} chars. Check server logs for details."
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
        
        # Get model_family from request (default to Gemini)
        from router.router_config import normalize_model_family
        model_family = request.model_family or "Gemini"
        model_key = normalize_model_family(model_family)
        
        # Initialize event system
        event_logger = get_event_logger()
        project_id = request.project_id or f"proj_{int(time.time())}"
        conversation_id = request.conversation_id or f"conv_{int(time.time())}"
        
        emitter = EventEmitter(
            project_id=project_id,
            conversation_id=conversation_id,
            callback=lambda event: event_logger.log_event(event),
            model_name=model_family  # EventEmitter stores model_family
        )
        
        emitter.emit_chat_message("Starting project modification...")
        
        # Classify modification complexity using router model
        complexity, complexity_meta = classify_modification_complexity_unified(
            request.instruction, 
            model_name=model_key
        )
        
        # Select model based on complexity + model_family
        mod_model = get_modification_model(model_family, complexity)
        
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
        
        # Generate modification - route to appropriate provider
        from router.router_config import get_provider
        provider = get_provider(model_family)
        
        if provider == "gemini":
            mod_out = gemini_generate_text(mod_prompt, model=mod_model)
        elif provider == "anthropic":
            if claude_generate_text is None:
                raise HTTPException(status_code=500, detail="Claude client not available")
            mod_out = claude_generate_text(mod_prompt, model=mod_model, max_tokens=16384)
        elif provider == "openai":
            if gpt_generate_text is None:
                raise HTTPException(status_code=500, detail="GPT client not available")
            mod_out = gpt_generate_text(mod_prompt, model=mod_model, max_tokens=16384)
        else:
            mod_out = gemini_generate_text(mod_prompt, model=mod_model)
        
        mod_project = parse_project_json(mod_out)
        
        # If parsing failed, try with a stricter prompt (retry once)
        if not mod_project and provider != "gemini":
            print(f"[PROJECT_MOD] First parse attempt failed. Output preview (first 500 chars): {mod_out[:500]}")
            emitter.emit_chat_message("Retrying with stricter JSON prompt...")
            
            # Create a stricter prompt
            strict_mod_prompt = (
                "You are a JSON generator. Return ONLY valid JSON, nothing else.\n\n"
                "CRITICAL RULES:\n"
                "1. Start your response with {\n"
                "2. End your response with }\n"
                "3. Do NOT include markdown code blocks (no ```json or ```)\n"
                "4. Do NOT include any text before or after the JSON\n"
                "5. Do NOT include explanations or comments\n\n"
            ) + mod_prompt
            
            # Retry generation with higher token limit
            if provider == "anthropic":
                if claude_generate_text is None:
                    raise HTTPException(status_code=500, detail="Claude client not available")
                mod_out = claude_generate_text(strict_mod_prompt, model=mod_model, max_tokens=16384)
            elif provider == "openai":
                if gpt_generate_text is None:
                    raise HTTPException(status_code=500, detail="GPT client not available")
                mod_out = gpt_generate_text(strict_mod_prompt, model=mod_model, max_tokens=16384)
            else:
                # Fallback to gemini client (shouldn't happen due to condition, but safe)
                mod_out = gemini_generate_text(strict_mod_prompt, model=mod_model)
            
            mod_project = parse_project_json(mod_out)
        
        # Fallback to main_model if parsing failed
        if not mod_project:
            main_model = get_main_model(model_family)
            if mod_model != main_model:
                emitter.emit_chat_message(f"Retrying with {main_model}...")
                if provider == "gemini":
                    mod_out = gemini_generate_text(mod_prompt, model=main_model)
                elif provider == "anthropic":
                    if claude_generate_text is None:
                        raise HTTPException(status_code=500, detail="Claude client not available")
                    mod_out = claude_generate_text(mod_prompt, model=main_model, max_tokens=16384)
                elif provider == "openai":
                    if gpt_generate_text is None:
                        raise HTTPException(status_code=500, detail="GPT client not available")
                    mod_out = gpt_generate_text(mod_prompt, model=main_model, max_tokens=16384)
                else:
                    mod_out = gemini_generate_text(mod_prompt, model=main_model)
                mod_project = parse_project_json(mod_out)
                mod_model = main_model
        
        if not mod_project:
            # Log the actual output for debugging
            output_preview = mod_out[:1000] if mod_out else "No output received"
            print(f"[PROJECT_MOD] Parse failed. Model: {mod_model}, Provider: {provider}")
            print(f"[PROJECT_MOD] Output preview (first 1000 chars): {output_preview}")
            
            emitter.emit_error(
                scope="validation",
                message="Failed to parse modified project JSON",
                details=f"The model returned output that could not be parsed as JSON. Output preview: {output_preview[:200]}...",
                actions=["retry", "ask_user"]
            )
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse modified project JSON. Model: {mod_model}. Output preview: {output_preview[:200]}..."
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

