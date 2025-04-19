import os
import boto3
import datetime

from decimal import Decimal
from datetime import timezone
from openai import OpenAI
from shared.consumption import OpenAIConsumption

if os.getenv("ENV", None) == "local":
    boto3.setup_default_session(profile_name='otterlab')

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini-2024-07-18")
MIN_TEXT_LENGTH = 10
TEXT_MAX_LENGTH = 5000

dynamodb = boto3.resource('dynamodb')
usage_table = dynamodb.Table('lang-ai-api-usage')

if os.getenv("ENV", None) == "local":
    boto3.setup_default_session(profile_name='otterlab')


def lambda_handler(event, context):
    try:
        text = event.get("text", "").strip()
        mode = event.get("mode", "improve")
        tone = event.get("tone", "default")

        api_key = event.get("api_key")
        if not api_key:
            return _response(400, {"error": "API key is required."})

        usage = get_api_key(api_key)
        prompt_tokens_estimated = estimate_tokens(text)
        used = usage.get("totalTokenUsed", 0)
        allocated = usage.get("allocatedTokens")

        if prompt_tokens_estimated + used > allocated:
            return _response(403, {"error": "Token limit exceeded."})

        if len(text) <= MIN_TEXT_LENGTH:
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
        consumption = OpenAIConsumption(response.to_dict())
        increment_token_usage(usage, consumption.get())

        return _response(200, {"result": content})

    except Exception as e:
        print(f"Error: {e}")
        return _response(500, {"error": str(e)})


def _response(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": body
    }


def get_api_key(api_key):
    res = usage_table.get_item(Key={'apiKey': api_key})
    if 'Item' not in res:
        raise ValueError("API key not found.")
    return res.get("Item")


def estimate_tokens(text):
    return int(len(text.split()) * 1.3)  # 1 token ≈ 0.75 words


def increment_token_usage(user, consumption):
    now = datetime.datetime.now(timezone.utc).isoformat()
    model_ = consumption["model"]

    # Extract and convert to Decimal
    prompt_tokens = Decimal(str(consumption["prompt_tokens"]))
    completion_tokens = Decimal(str(consumption["completion_tokens"]))
    total_tokens_used = Decimal(str(consumption["total_tokens_used"]))
    prompt_cost = Decimal(str(consumption["prompt_cost"]))
    completion_cost = Decimal(str(consumption["completion_cost"]))
    total_cost = Decimal(str(consumption["total_cost"]))

    usage_table.update_item(
        Key={'apiKey': user["apiKey"]},
        UpdateExpression="SET totalTokensUsed = :total_tokens_used, "
                         "lastUpdated = :now, "
                         "model = :model, "
                         "promptTokens = :prompt_tokens, "
                         "completionTokens = :completion_tokens, "
                         "promptCost = :prompt_cost, "
                         "completionCost = :completion_cost, "
                         "totalCost = :total_cost",
        ExpressionAttributeValues={
            ':now': now,
            ':model': model_,
            ':prompt_tokens': Decimal(str(user.get("promptTokens", 0))) + prompt_tokens,
            ':completion_tokens': Decimal(str(user.get("completionTokens", 0))) + completion_tokens,
            ':total_tokens_used': Decimal(str(user.get("totalTokensUsed", 0))) + total_tokens_used,
            ':prompt_cost': Decimal(str(user.get("promptCost", 0))) + prompt_cost,
            ':completion_cost': Decimal(str(user.get("completionCost", 0))) + completion_cost,
            ':total_cost': Decimal(str(user.get("totalCost", 0))) + total_cost
        }
    )
