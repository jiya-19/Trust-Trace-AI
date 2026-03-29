from utils.llm import LLMService

class AnalysisAgent:
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service

    def execute(self, message: str) -> dict:
        prompt = f"""
You are an expert cybersecurity analyst.
Analyze the following message for specific fraud indicators: urgency, impersonation, suspicious links, and malicious intent.

Message: "{message}"
"""
        schema = {
            "type": "object",
            "properties": {
                "urgency_level": {"type": "string", "enum": ["High", "Medium", "Low"]},
                "impersonation_detected": {"type": "boolean"},
                "suspicious_links": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "malicious_intent": {"type": "string", "description": "Describe the potential threat or goal of the scammer"}
            },
            "required": ["urgency_level", "impersonation_detected", "suspicious_links", "malicious_intent"]
        }
        
        return self.llm.generate_json(prompt, schema)
