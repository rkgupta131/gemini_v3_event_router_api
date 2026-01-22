# System Prompts - Quick Reference
## One-Page Cheat Sheet for Developers

---

## 1️⃣ Intent Classification

**When:** First user interaction  
**Returns:** `webpage_build | chat | greeting_only | illegal | other`

```python
prompt = """
You are an intent classifier. Return exactly one JSON object (no extra text):
{ "label": "<webpage_build|chat|greeting_only|illegal|other>", "explanation": "<text>", "confidence": 0.0 }
""" + user_input
```

---

## 2️⃣ Page Type Classification

**When:** After `webpage_build` detected  
**Returns:** One of 12 page types

```python
prompt = """
Page type classifier. Return JSON:
{ "page_type": "<landing_page|crm_dashboard|hr_portal|inventory_management|ecommerce_fashion|
                 digital_product_store|service_marketplace|student_portfolio|hyperlocal_delivery|
                 real_estate_listing|ai_tutor_lms|generic>", 
  "explanation": "<text>", 
  "confidence": 0.0 }

Types:
- landing_page: Marketing page, lead capture
- crm_dashboard: Customer management, leads
- hr_portal: Employee management, onboarding
- inventory_management: Stock tracking
- ecommerce_fashion: Online store
- digital_product_store: Digital downloads
- service_marketplace: Two-sided platform
- student_portfolio: Resume, projects
- hyperlocal_delivery: Food/grocery delivery
- real_estate_listing: Property listings
- ai_tutor_lms: Online courses
- generic: Fallback
""" + user_input
```

---

## 3️⃣ Detail Analysis

**When:** After page type detected  
**Returns:** `needs_followup: boolean`

```python
prompt = """
Requirements analyzer. Return JSON:
{ "needs_followup": true/false, "explanation": "<text>", "confidence": 0.0 }

true = vague ("build a CRM")
false = detailed ("build a CRM for marketing agency with 10 people, lead tracking, and email integration")
""" + user_input
```

---

## 4️⃣ Chat Response

**When:** Intent = `chat`  
**Returns:** Plain text

```python
prompt = f"Reply in max 4 sentences.\nUser: {user_input}"
```

---

## 5️⃣ AI Defaults

**When:** User selects "AI-recommended" mode  
**Returns:** JSON with defaults

```python
prompt = """
Return ONLY valid JSON.
Allowed keys: hero_text, subtext, cta, theme.

User intent:
""" + user_initial_query
```

---

## 6️⃣ Project Generation (MAIN)

**When:** Step 3 - Generate button clicked  
**Returns:** Complete project JSON

### Template:

```python
base_prompt = """
Return exactly one JSON object describing a React+Vite+TypeScript project.
Schema: {"project": {"name": string, "description": string, "files": {...}, "dirents": {...}, "meta": {...}}}
Return only the JSON object.
"""

# If page type detected:
base_prompt += f"""
=== PAGE TYPE: {page_type_name} ({category}) ===
Target User: {end_user_description}

REQUIRED CORE PAGES:
{list_of_pages}

REQUIRED COMPONENTS:
{list_of_components_with_descriptions}

IMPORTANT: Implement ALL pages and components. Use React best practices. TypeScript for type safety. Include routing.
"""

# If questionnaire answers exist:
base_prompt += """
=== USER REQUIREMENTS ===
{questionnaire_answers}

IMPORTANT: Tailor design and features to these requirements.
"""

# Always include:
final_prompt = base_prompt + f"""
USER_FIELDS:
{json.dumps(collected_data)}
"""
```

---

## Flow Chart

```
Input → classify_intent()
         ↓
    webpage_build?
         ↓
    classify_page_type()
         ↓
    generic? → Show category selector → User picks → Set page_type
         ↓
    analyze_query_detail()
         ↓
    needs_followup? → Show MCQ questionnaire → Collect answers
         ↓
    Wizard mode (hero_text, subtext, cta, theme)
         ↓
    Generate project with:
    - Base prompt
    - Page type config (pages + components)
    - Questionnaire answers
    - User fields
```

---

## JSON Response Parsing

```javascript
function extractJSON(response) {
  const start = response.indexOf("{");
  const end = response.lastIndexOf("}");
  if (start !== -1 && end !== -1 && end > start) {
    return JSON.parse(response.substring(start, end + 1));
  }
  throw new Error("No JSON found");
}
```

---

## Error Handling

| Scenario | Fallback |
|----------|----------|
| Intent classification fails | Default to `chat` |
| Page type classification fails | Default to `generic` |
| Detail analysis fails | Default to `needs_followup=true` |
| Project generation fails | Show raw output + error |

---

## Model Config

- **Model:** `gemini-3-pro-preview`
- **Output:** Always JSON (except chat response)
- **Parse:** Extract JSON with regex/substring
- **Confidence:** Use for UI feedback

---

## File References

- Classifiers: `/models/gemini_client.py`
- Page configs: `/data/page_types_reference.py`
- Questions: `/data/questionnaire_config.py`
- Categories: `/data/page_categories.py`
- Main flow: `/app.py`

---

**Last Updated:** Jan 7, 2026





