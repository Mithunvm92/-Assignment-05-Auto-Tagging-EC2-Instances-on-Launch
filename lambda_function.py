import boto3

ec2 = boto3.client("ec2")


def lambda_handler(event, context):
    print("===== EC2 AUTO TAGGING STARTED =====")
    print(f"Event: {event}")

    detail = event.get("detail", {})
    instance_id = detail.get("instance-id")
    state = detail.get("state")

    if not instance_id:
        print("No instance ID found in event.")
        return {
            "statusCode": 400,
            "message": "Instance ID not found"
        }

    print(f"Instance ID: {instance_id}")
    print(f"Instance State: {state}")

    tags = [
        {
            "Key": "Environment",
            "Value": "AutoTagged"
        },
        {
            "Key": "ManagedBy",
            "Value": "Lambda"
        },
        {
            "Key": "Project",
            "Value": "EC2-AutoTagging"
        }
    ]

    response = ec2.create_tags(
        Resources=[instance_id],
        Tags=tags
    )

    print("Tags applied successfully.")
    print(f"Tag response: {response}")

    return {
        "statusCode": 200,
        "instance_id": instance_id,
        "state": state,
        "tags_applied": tags
    }
