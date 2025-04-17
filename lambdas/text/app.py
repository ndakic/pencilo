import os
import json

from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini-2024-07-18")
TEXT_MAX_LENGTH = 5000


def lambda_handler(event, context):
    try:
        text = event.get("text", "").strip()
        mode = event.get("mode", "improve")
        tone = event.get("tone", "default")

        if len(text) < 3:
            return _response(400, {"error": "Text too short"})

        if len(text) >= TEXT_MAX_LENGTH:
            return _response(400, {"error": f"Text too long. Max length is {TEXT_MAX_LENGTH} characters."})

        if mode == "validate":
            system_prompt = "You are a helpful assistant that validates grammar and fluency."
            user_prompt = (f"Validate the following text. If correct, return it unchanged. "
                           f"If errors, return the corrected version only:\n\n{text}")
        elif mode == "rephrase":
            system_prompt = (f"You are a writing assistant. Improve grammar, clarity, and tone. Use a {tone} tone. "
                             f"Make sure to return the text in the same language, and to ALWAYS return "
                             f"just the text(modified version of text), without any additional information.")
            user_prompt = f"Please improve this text with a {tone} tone:\n\n{text}"
        else:
            raise ValueError("Invalid mode!")

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.4
        )

        content = response.choices[0].message.content.strip()

        return _response(200, {"result": content})

    except Exception as e:
        return _response(500, {"error": str(e)})


def _response(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": body
    }
