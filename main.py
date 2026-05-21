import boto3
import json
import random
import string

# Prints once when Lambda container is initialized (cold start)
print("Loading function")

# Connect to DynamoDB service using resource interface (higher-level than client)
# Resource lets us work with tables directly (cleaner for CRUD operations)
dynamo = boto3.resource("dynamodb")

# Reference the DynamoDB table where URLs will be stored
table = dynamo.Table("url-shortener")


def generate_short_id(length=6):
    """
    Generates a random alphanumeric string to use as the short URL ID.

    Example output: 'aZ93kL'

    This acts as the key for mapping short URL -> long URL in DynamoDB.
    """
    return "".join(
        random.choices(
            string.ascii_letters + string.digits,
            k=length
        )
    )


def lambda_handler(event, context):
    """
    AWS Lambda entry point triggered by API Gateway.

    Expected input:
    {
        "body": "{\"url\": \"https://example.com\"}"
    }

    Flow:
    1. Parse incoming request body
    2. Validate required URL field
    3. Generate short ID
    4. Store mapping in DynamoDB
    5. Return short ID to user
    """

    # Parse JSON body safely (fallback to empty dict if missing)
    body = json.loads(event.get("body", "{}"))

    # Extract long URL from request
    long_url = body.get("url")

    # Validate input early to avoid storing invalid data
    if not long_url:
        return {
            "statusCode": 400,  # Bad request
            "headers": {
                "Access-Control-Allow-Origin": "*",  # Enable CORS
                "Content-Type": "application/json"
            },
            "body": json.dumps({"error": "url is required"})
        }

    # Generate unique short identifier for the URL
    short_id = generate_short_id()

    # Store mapping in DynamoDB:
    # id  -> short URL code
    # url -> original long URL
    table.put_item(
        Item={
            "id": short_id,
            "url": long_url
        }
    )

    # Return success response with generated short ID
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",  # Allow frontend access
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "short_id": short_id
        })
    }