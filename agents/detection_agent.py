from utils.llm import LLMService

class DetectionAgent:
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service

    def execute(self, message: str) -> dict:
        prompt = f"""
You are a preliminary fraud detection agent.
Analyze the following message and determine if it is likely a scam.

Message: "{message}"

Provide a boolean indicating if it is a scam, a risk score from 0 to 100, and a brief reasoning.
"""
        schema = {
            "type": "object",
            "properties": {
                "is_scam": {"type": "boolean"},
                "risk_score": {"type": "integer", "description": "0 to 100"},
                "reasoning": {"type": "string"}
            },
            "required": ["is_scam", "risk_score", "reasoning"]
        }
        
        return self.llm.generate_json(prompt, schema)
