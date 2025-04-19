import os
import boto3
import datetime
import uuid

from datetime import timezone

if os.getenv("ENV", None) == "local":
    boto3.setup_default_session(profile_name='otterlab')

dynamodb = boto3.resource('dynamodb')
usage_table = dynamodb.Table('lang-ai-api-usage')


def lambda_handler(event, context):
    """
    Lambda function to handle API requests for setting the OpenAI API key.
    """
    try:
        if event.get('action') == "create":
            email = event.get("email")
            if not email:
                return _response(400, "Email is required.")
            user_id = init_user(email=email)

            return _response(200, f"User created successfully with apiKey: {user_id}")

    except Exception as e:
        return _response(400, f"Invalid action: {e}")


def _response(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": body
    }


def init_user(email, tokens=100000, package="beta", status="active"):
    now = datetime.datetime.now(timezone.utc).isoformat()

    users = get_all_users()
    for user in users:
        if user["email"] == email:
            raise Exception(f"User with email {email} already exists.")

    api_key = str(uuid.uuid4())
    usage_table.put_item(Item={
        'apiKey': api_key,
        'email': email,
        'totalTokensUsed': 0,
        'allocatedTokens': tokens,
        'packageType': package,
        'status': status,
        'startedDate': now,
        'lastUpdated': now
    })

    return api_key


def get_all_users():
    # Note: This will be removed later when I add user table
    response = usage_table.scan()
    items = response.get('Items', [])
    while 'LastEvaluatedKey' in response:
        response = usage_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response.get('Items', []))
    return items
