import os
from typing import Optional


class MockClient:
    """
    Offline stand-in for an LLM client.
    This lets the app run without an API key.
    """

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        # Very small, predictable behavior for demos.
        if "Return ONLY valid JSON" in system_prompt:
            # Purposely not JSON to force fallback unless students change behavior.
            return "I found some issues, but I'm not returning JSON right now."
        return "# MockClient: no rewrite available in offline mode.\n"


class GeminiClient:
    """
    Minimal Gemini API wrapper with added error resilience.

    Requirements:
    - google-generativeai installed #deprecated, replaced by google-genai
    - GEMINI_API_KEY set in environment (or loaded via python-dotenv) #confirmed its in .env and the key is in quotes
    """

    def __init__(self, model_name: str = "gemini-2.5-flash", temperature: float = 0.2):
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError(
                "Missing GEMINI_API_KEY. Create a .env file and set GEMINI_API_KEY=..."
            )

        # Import here so heuristic mode doesn't require the dependency at import time.
        #import google.generativeai as genai
        import google.genai as genai #added since above is deprecated



        #genai.configure(api_key=api_key)
        #self.model = genai.GenerativeModel(model_name)
        
        key = api_key or os.environ.get("GEMINI_API_KEY")
        self.client = genai.Client(api_key=key)
        self.model = model_name
        self.temperature = float(temperature)

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        """
        Sends a single request to Gemini.

        UPDATED: Added try/except to handle rate limits and API errors gracefully.
        If an error occurs, it returns an empty string, triggering the agent's
        heuristic fallback logic.
        """
        # from google.genai import types  # re-enable when using GenerateContentConfig

        # Gemma models don't support system_instruction, so we prepend it directly.
        combined = f"{system_prompt}\n\n{user_prompt}"

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=combined,
                # config=types.GenerateContentConfig(
                #     temperature=self.temperature,  # re-enable to tune response style
                # ),
            )

            # Defensive: response.text can be None or raise an error if blocked by filters.
            return response.text or ""

        except Exception as e:
            # Returning empty string allows the agent to detect the failure
            # and switch to offline rules.
            return ""
