from app import lambda_handler

context = {}

event = {
    "text": "This is a test text with a speling error.",
    "mode": "validate",
    "tone": "default",
    "api_key": "your_api_key_here"  # Replace with your actual API key
}

result = lambda_handler(event, context)
print("Result:", result)
