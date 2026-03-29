import os
import json
import logging
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")

        if not api_key:
            logger.warning("Neither GEMINI_API_KEY nor GOOGLE_API_KEY is set. LLM calls will fail.")
            self.client = None
        else:
            self.client = genai.Client(api_key=api_key)

        # Use stable models only
        self.primary_model = "gemini-2.0-flash"
        self.fallback_model = "gemini-2.0-flash" # Use 2.0-flash exclusively since 1.5 is failing
        print("API KEY FOUND:", bool(api_key))
    def _clean_json_text(self, text: str) -> str:
        """Clean common markdown/json wrapper issues."""
        import re
        if not text:
            return "{}"

        # Try to find exactly the outermost JSON brackets
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return match.group(0)
            
        return text.strip()

    def _call_model(self, model_name: str, prompt: str) -> str:
        """Single Gemini model call."""
        response = self.client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2,
            )
        )
        return response.text

    def generate_json(self, prompt: str, schema: dict = None, max_retries: int = 1) -> dict:
        """
        Generates a JSON response from Gemini with retry + fallback model support.
        """
        if self.client is None:
            raise RuntimeError(
                "Missing API Key! Please set GEMINI_API_KEY or GOOGLE_API_KEY before running the app."
            )

        full_prompt = prompt
        if schema:
            full_prompt += (
                "\n\nReturn ONLY valid JSON that strictly follows this schema:\n"
                + json.dumps(schema, indent=2)
            )

        models_to_try = [self.primary_model, self.fallback_model]

        last_exception = None

        for model_name in models_to_try:
            for attempt in range(max_retries):
                try:
                    logger.info(f"Trying model={model_name}, attempt={attempt + 1}")
                    text_response = self._call_model(model_name, full_prompt)
                    cleaned = self._clean_json_text(text_response)
                    parsed_json = json.loads(cleaned)
                    return parsed_json

                except Exception as e:
                    last_exception = e
                    logger.error(
                        f"Attempt {attempt + 1} failed for model {model_name}. Error: {e}"
                    )

                    if attempt < max_retries - 1:
                        time.sleep(2)

            logger.warning(f"Switching to fallback model after failures on {model_name}")

        logger.error("All Gemini model attempts failed.")
        logger.error("All Gemini attempts failed. Raising RuntimeError to let orchestrator handle fallback.")
        
        if last_exception:
            raise RuntimeError(f"Failed to generate valid JSON from LLM after multiple attempts. Last error: {last_exception}")
        raise RuntimeError("Failed to generate valid JSON from LLM after multiple attempts.")