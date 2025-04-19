from app import lambda_handler

context = {}

event = {
    "text": "Large Language Models are a new class of models that are trained on large amounts of text data. They are able to generate text that is indistinguishable from human-written text. There is plenty of LLMs available, but one of the most popular and free to use are Code Llama models from Meta, so we will use them in this article.",
    "mode": "validate",
    "tone": "default",
    "api_key": "38881128-3827-4320-850b-6dddc01567f2"
}

result = lambda_handler(event, context)
print("Result:", result)
