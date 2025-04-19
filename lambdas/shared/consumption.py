class OpenAIConsumption:
    PRICING = {
        "gpt-4o-mini-2024-07-18": {
            "prompt": 0.00015,  # $ per 1,000 tokens
            "completion": 0.0006  # $ per 1,000 tokens
        }
    }

    def __init__(self, response: dict):
        self.response = response
        self.model = response.get("model")
        self.usage = response.get("usage", {})

        self.prompt_tokens = self.usage.get("prompt_tokens", 0)
        self.completion_tokens = self.usage.get("completion_tokens", 0)
        self.total_tokens_used = self.usage.get("total_tokens", 0)

        if self.model not in self.PRICING:
            raise ValueError(f"Unsupported model: {self.model}")

    def calculate_prompt_cost(self):
        rate = self.PRICING[self.model]["prompt"]
        return round((self.prompt_tokens / 1000) * rate, 6)

    def calculate_completion_cost(self):
        rate = self.PRICING[self.model]["completion"]
        return round((self.completion_tokens / 1000) * rate, 6)

    def calculate_total_cost(self):
        return round(self.calculate_prompt_cost() + self.calculate_completion_cost(), 6)

    def get(self):
        return {
            "model": self.model,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens_used": self.total_tokens_used,
            "prompt_cost": self.calculate_prompt_cost(),
            "completion_cost": self.calculate_completion_cost(),
            "total_cost": self.calculate_total_cost()
        }
