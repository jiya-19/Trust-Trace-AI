import os
from utils.orchestrator import WorkflowOrchestrator

try:
    print("Initializing Orchestrator...")
    orc = WorkflowOrchestrator()
    print("Processing message...")
    res = orc.process_message("URGENT: Your account is locked. Click here to verify your identity.")
    
    if res.get("status") == "error":
        print(f"Workflow error: {res.get('error_details')}")
    else:
        print("SUCCESS! Output:")
        print(res["decision"])
except Exception as e:
    import traceback
    print("Caught Exception during setup/execution:")
    traceback.print_exc()
