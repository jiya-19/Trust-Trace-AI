import json
from utils.llm import LLMService

class DecisionAgent:
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service

    def execute(self, message: str, detection_result: dict, analysis_result: dict, rag_context: list) -> dict:
        prompt = f"""
You are the final decision-making agent for a financial fraud handling system.
Based on the inputs provided below, assign a final risk category and provide a detailed justification.

Original Message: "{message}"

Detection Result:
{json.dumps(detection_result, indent=2)}

Analysis Result:
{json.dumps(analysis_result, indent=2)}

Similar Fraud Cases Retrieved (RAG context):
{json.dumps(rag_context, indent=2)}

Synthesize this information. Calculate a final confidence score (0-100) and choose a risk category: High, Medium, or Low.
"""
        schema = {
            "type": "object",
            "properties": {
                "final_risk_category": {"type": "string", "enum": ["High", "Medium", "Low"]},
                "justification": {"type": "string", "description": "Why this category was chosen based on the inputs"},
                "confidence_score": {"type": "integer", "description": "0 to 100"}
            },
            "required": ["final_risk_category", "justification", "confidence_score"]
        }
        
        return self.llm.generate_json(prompt, schema)
