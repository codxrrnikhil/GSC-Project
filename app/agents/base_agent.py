class BaseAgent:
    def decide(self, input_data):
        raise NotImplementedError("Subclasses must implement decide().")
