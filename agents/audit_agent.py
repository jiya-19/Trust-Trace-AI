import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class AuditAgent:
    def __init__(self):
        self.logs = []

    def log_step(self, step_name: str, input_data: dict, output_data: dict, decision: str = "N/A"):
        """
        Logs an execution step.
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "step": step_name,
            "input": input_data,
            "output": output_data,
            "decision": decision
        }
        self.logs.append(entry)
        logger.info(f"Audit Log - {step_name}: Decision: {decision}")
        return entry

    def get_audit_trail(self) -> list:
        return self.logs
        
    def export_trail_json(self) -> str:
        return json.dumps(self.logs, indent=2)

    def clear(self):
        self.logs = []
