# File: supervisor_agent.py

class SupervisorAgent:
    def __init__(self):
        self.context = []

    def receive_intent(self, intent):
        print(f"SupervisorAgent received intent: {intent}")
        intent_lower = intent.lower()
        # PRIORITIZE 'analyze' and 'analysis' FIRST
        if "analyze" in intent_lower or "analysis" in intent_lower:
            return "analysis_subagent", intent
        elif "automate" in intent_lower or "automation" in intent_lower:
            return "automation_subagent", intent
        else:
            return "fallback", intent

    def add_context(self, message):
        self.context.append(message)

    def get_context(self):
        return self.context
