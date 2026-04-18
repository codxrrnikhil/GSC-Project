import random

from app.agents.base_agent import BaseAgent


class ContentAgent(BaseAgent):
    def decide(self, input_data):
        url = str(input_data.get("url", ""))
        action = "flag" if "pirated" in url else "ignore"
        confidence = random.uniform(0.7, 0.99)
        return {"action": action, "confidence": confidence}
