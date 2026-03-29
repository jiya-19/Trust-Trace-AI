import logging
from agents.audit_agent import AuditAgent
from agents.detection_agent import DetectionAgent
from agents.analysis_agent import AnalysisAgent
from agents.decision_agent import DecisionAgent
from agents.action_agent import ActionAgent
from rag.retrieval_agent import RetrievalAgent
from utils.llm import LLMService

logger = logging.getLogger(__name__)

class WorkflowOrchestrator:
    def __init__(self):
        self.llm_service = LLMService()
        self.audit_agent = AuditAgent()
        
        self.detection_agent = DetectionAgent(self.llm_service)
        self.analysis_agent = AnalysisAgent(self.llm_service)
        self.decision_agent = DecisionAgent(self.llm_service)
        self.action_agent = ActionAgent(self.llm_service)
        self.retrieval_agent = RetrievalAgent()
        
    def _compute_fallback_risk(self, message: str) -> tuple:
        msg_lower = message.lower()
        high_keywords = ["urgent", "block", "verify", "prize", "won", "reward", "lottery", "cashback", "suspend", "kyc", "pin", "approve"]
        low_keywords = ["safe", "successful", "official", "alert"]
        for k in high_keywords:
            if k in msg_lower: return "High", 85, True
        for k in low_keywords:
            if k in msg_lower: return "Low", 15, False
        return "Medium", 50, True

    def process_message(self, message: str) -> dict:
        self.audit_agent.clear()
        self.audit_agent.log_step("Initialization", {"message": message}, {}, "Started")
        
        fb_risk, fb_score, fb_is_scam = self._compute_fallback_risk(message)
        
        try:
            # 1. Detection
            detection_res = self._run_with_retry(
                self.detection_agent.execute,
                message,
                fallback_response={
                    "is_scam": fb_is_scam,
                    "risk_score": fb_score,
                    "reasoning": f"Fallback heuristic reasoning: Contains keywords mapped to {fb_risk} risk."
                }
            )
            self.audit_agent.log_step("Detection", {"message": message}, detection_res, f"Risk={detection_res.get('risk_score')}")
            
            risk_score = detection_res.get("risk_score", 0)
            
            rag_context = []
            analysis_res = {}
            decision_res = {}
            action_res = {}
            
            if risk_score > 10 or detection_res.get("is_scam"):
                # 2. Retrieval
                rag_context = self.retrieval_agent.retrieve_similar_cases(message, top_k=3)
                self.audit_agent.log_step("Retrieval", {"query": message}, {"retrieved": len(rag_context)}, "Fetched RAG context")
                
                # 3. Analysis
                analysis_res = self._run_with_retry(
                    self.analysis_agent.execute,
                    message,
                    fallback_response={
                        "urgency_level": "Medium",
                        "impersonation_detected": True,
                        "suspicious_links": [],
                        "malicious_intent": "Fallback intent: Potential financial compromise detected by rules."
                    }
                )
                self.audit_agent.log_step("Analysis", {"message": message}, analysis_res, "Completed deep analysis")
                
                # 4. Decision
                decision_res = self._run_with_retry(
                    self.decision_agent.execute,
                    message, detection_res, analysis_res, rag_context,
                    fallback_response={
                        "final_risk_category": fb_risk,
                        "justification": "Automated fallback heuristic classification.",
                        "confidence_score": fb_score
                    }
                )
                self.audit_agent.log_step("Decision", {"analysis": analysis_res}, decision_res, f"Final Risk Category: {decision_res.get('final_risk_category')}")
                
            else:
                decision_res = {
                    "final_risk_category": "Low",
                    "justification": "Initial detection flagged this as very low risk/not a scam.",
                    "confidence_score": 95
                }
                self.audit_agent.log_step("Decision", {"detection": detection_res}, decision_res, "Bypassed analysis due to low risk")

            # 5. Action
            if decision_res.get("final_risk_category") in ["High", "Medium"]:
                action_res = self._run_with_retry(
                    self.action_agent.execute,
                    message, decision_res,
                    fallback_response={
                        "suggested_actions": ["Block Sender", "Report to Bank", "Do NOT click links"],
                        "complaint_template": "A suspicious activity/message was detected and requires investigation."
                    }
                )
                self.audit_agent.log_step("Action", {"decision": decision_res}, action_res, f"Generated {len(action_res.get('suggested_actions', []))} actions")
            else:
                action_res = {
                    "suggested_actions": ["None required"],
                    "complaint_template": "No complaint necessary."
                }
                self.audit_agent.log_step("Action", {"decision": decision_res}, action_res, "No action required")
             
            # Calculate a generic User Safety Score (example metric: 100 - risk_score, bounded)
            confidence = decision_res.get("confidence_score", 50)
            try:
                confidence = int(confidence)
            except (ValueError, TypeError):
                confidence = 50
                
            final_score = confidence if decision_res.get("final_risk_category") == "Low" else (100 - confidence)
                
            return {
                "status": "success",
                "detection": detection_res,
                "analysis": analysis_res,
                "rag_context": rag_context,
                "decision": decision_res,
                "action": action_res,
                "audit_trail": self.audit_agent.get_audit_trail(),
                "user_safety_score": max(0, min(100, final_score))
            }
            
        except Exception as e:
            logger.error(f"Workflow failed: {e}")
            self.audit_agent.log_step("Error/Escalation", {"error": str(e)}, {}, "Escalated for manual review")
            return {
                "status": "error",
                "message": "The workflow encountered an unrecoverable error and escalated for manual review.",
                "error_details": str(e),
                "audit_trail": self.audit_agent.get_audit_trail()
            }
            
    def _run_with_retry(self, func, *args, fallback_response=None, max_retries=1):
        last_exception = None
        for attempt in range(max_retries):
            try:
                return func(*args)
            except Exception as e:
                logger.warning(f"Step {func.__name__} failed on attempt {attempt+1}. Retrying... Error: {e}")
                last_exception = e
        
        logger.error(f"Step {func.__name__} fundamentally failed after {max_retries} attempts.")
        if fallback_response is not None:
            logger.info(f"Using fallback response for {func.__name__}")
            return fallback_response
            
        if last_exception is not None:
            raise last_exception
        else:
            raise RuntimeError(f"Step {func.__name__} fundamentally failed.")
