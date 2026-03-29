import json
from utils.llm import LLMService

class ActionAgent:
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service

    def execute(self, message: str, decision_result: dict) -> dict:
        prompt = f"""
You are the action simulation agent for a financial fraud handling system.
Based on the message and the final decision risk category, suggest system actions (e.g., 'Block Sender', 'Warn User', 'Delete Message') and generate a formal complaint template that the user can submit to authorities or their bank.

Original Message: "{message}"

Decision Result:
{json.dumps(decision_result, indent=2)}
"""
        schema = {
            "type": "object",
            "properties": {
                "suggested_actions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of actions to take"
                },
                "complaint_template": {
                    "type": "string",
                    "description": "A formal complaint text explaining the fraud attempt"
                }
            },
            "required": ["suggested_actions", "complaint_template"]
        }
        
        return self.llm.generate_json(prompt, schema)
