import os
from dotenv import load_dotenv

# -------- PROVIDERS --------
import openai
from anthropic import Anthropic
from google import genai
from google.genai import types

# Load .env
load_dotenv()


# -------------------------------------------------------
# 1️⃣ TEST OPENAI KEY
# -------------------------------------------------------
# -------------------------------------------------------
# 1️⃣ TEST OPENAI KEY  (FIXED)
# -------------------------------------------------------
def test_openai(prompt):
    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL"),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=int(os.getenv("OPENAI_MAX_TOKENS")),
        )
        print("\n✅ OPENAI SUCCESS:\n", response.choices[0].message.content)
    except Exception as e:
        print("\n❌ OPENAI ERROR:\n", e)


# -------------------------------------------------------
# 2️⃣ TEST CLAUDE (Anthropic)
# -------------------------------------------------------
def test_claude(prompt):
    try:
        client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        response = client.messages.create(
            model=os.getenv("CLAUDE_MODEL"),
            max_tokens=int(os.getenv("CLAUDE_MAX_TOKENS")),
            messages=[{"role": "user", "content": prompt}],
        )
        print("\n✅ CLAUDE SUCCESS:\n", response.content[0].text)
    except Exception as e:
        print("\n❌ CLAUDE ERROR:\n", e)


# -------------------------------------------------------
# 3️⃣ TEST GEMINI VIA VERTEX AI (Service Account JSON)
# -------------------------------------------------------
# -------------------------------------------------------
# 3️⃣ TEST GEMINI VIA VERTEX AI (Service Account JSON)  FIXED
# -------------------------------------------------------
# -------------------------------------------------------
# 3️⃣ TEST GEMINI VIA VERTEX AI (Service Account JSON)
#     Using your working style (vertexai=True)
# -------------------------------------------------------
def test_gemini_vertex(prompt):
    try:
        project_id = os.getenv("GEMINI_PROJECT_ID")
        location = os.getenv("GEMINI_VERTEX_LOCATION", "us-central1")

        # Create vertex client the correct way (matching your reference)
        client = genai.Client(
            vertexai=True,
            project=project_id,
            location=location,
        )

        response = client.models.generate_content(
            model=os.getenv("GEMINI_VERTEX_MODEL"),
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=int(os.getenv("GEMINI_VERTEX_MAX_TOKENS"))
            ),
        )

        print("\n✅ GEMINI (VERTEX SERVICE ACCOUNT) SUCCESS:\n", response.text)

    except Exception as e:
        print("\n❌ GEMINI (VERTEX) ERROR:\n", e)


# -------------------------------------------------------
# 4️⃣ TEST GEMINI USING API KEY MODE
# -------------------------------------------------------
def test_gemini_api_key(prompt):
    try:
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        response = client.models.generate_content(
            model=os.getenv("GEMINI_API_MODEL"),
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=int(os.getenv("GEMINI_API_MAX_TOKENS"))
            )
        )
        print("\n✅ GEMINI API-KEY SUCCESS:\n", response.text)
    except Exception as e:
        print("\n❌ GEMINI API-KEY ERROR:\n", e)


# -------------------------------------------------------
# MAIN MENU
# -------------------------------------------------------
def main():
    print("\n=== LLM Key Tester ===")
    print("1) Test OpenAI API Key")
    print("2) Test Claude API Key")
    print("3) Test Gemini (Vertex - service account)")
    print("4) Test Gemini (API Key mode)")
    print("======================")

    choice = input("Enter option (1-4): ").strip()
    prompt = input("\nEnter your test prompt: ")

    if choice == "1":
        test_openai(prompt)
    elif choice == "2":
        test_claude(prompt)
    elif choice == "3":
        test_gemini_vertex(prompt)
    elif choice == "4":
        test_gemini_api_key(prompt)
    else:
        print("Invalid option.")


if __name__ == "__main__":
    main()
