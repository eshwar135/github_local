# File: a2a_protocol.py

from supervisor_agent import SupervisorAgent
from subagent_automation import AutomationSubAgent
from subagent_analysis import AnalysisSubAgent

class A2ACommunicator:
    def __init__(self):
        self.supervisor = SupervisorAgent()
        self.automation_agent = AutomationSubAgent()
        self.analysis_agent = AnalysisSubAgent()
    
    def route_intent(self, intent):
        subagent_name, routed_intent = self.supervisor.receive_intent(intent)
        
        if subagent_name == "automation_subagent":
            response = self.automation_agent.handle_intent(routed_intent)
        elif subagent_name == "analysis_subagent":
            response = self.analysis_agent.handle_intent(routed_intent)
        else:
            response = "Fallback: Sorry, I cannot handle this request."
        
        self.supervisor.add_context({"intent": intent, "response": response})
        return response
