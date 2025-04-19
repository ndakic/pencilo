from app import lambda_handler

context = {}

create_user_event = {
    "action": "create",
    "email": "ndakic94@gmail.com",
}


create_user_event_result = lambda_handler(create_user_event, context)
print("create_user_event_result:", create_user_event_result)
