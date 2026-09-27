# Assignment 5 – Auto-Tagging EC2 Instances on Launch

## Objective

Create an AWS Lambda function using Python and Boto3 to automatically apply predefined tags to EC2 instances when they enter the `running` state.

The solution will:

- Monitor EC2 instance state changes.
- Use Amazon EventBridge to detect EC2 state-change events.
- Trigger an AWS Lambda function when an EC2 instance changes to the `running` state.
- Retrieve the EC2 instance ID and new state.
- Automatically apply predefined tags to the EC2 instance.
- Record Lambda execution details in CloudWatch Logs.

---

## AWS Services Used

- Amazon EC2
- AWS Lambda
- Amazon EventBridge
- AWS IAM
- Amazon CloudWatch Logs

---

# Architecture

```text
                   Amazon EC2
                       |
                       | State Change
                       v
                Amazon EventBridge
                       |
                       | Event
                       v
                  AWS Lambda
                       |
              +--------+--------+
              |                 |
              v                 v
       EC2 CreateTags     CloudWatch Logs
              |
              v
        Tagged EC2 Instance
````

---

# Prerequisites

Before starting this assignment, make sure you have:

* An AWS account.
* Permission to create Lambda functions.
* Permission to create IAM roles and policies.
* Permission to create EventBridge rules.
* Permission to modify EC2 resources and tags.
* At least one EC2 instance for testing.
* Python 3.x supported by AWS Lambda.
* Git installed on your local machine.
* A GitHub account.

---

# Project Structure

The project uses the following structure:

```text
assignment-05-ec2-auto-tagging/
│
├── lambda_function.py
├── README.md
```

---


# AWS Region

Use the following AWS Region for this assignment:

```text
Region:
Asia Pacific (Mumbai)

Region Code:
ap-south-1
```

Make sure that the EC2 instance, Lambda function, and EventBridge rule are created in the same AWS Region.

---

# Step 1 – Create IAM Role

The Lambda function requires an IAM execution role.

The role will provide Lambda with permission to:

* Write execution logs to CloudWatch Logs.
* Create EC2 tags.
* Describe EC2 instances.

Go to:

```text
AWS Console
    ↓
IAM
    ↓
Roles
    ↓
Create role
```

Under:

```text
Trusted entity type
```

select:

```text
AWS service
```

Under:

```text
Service or use case
```

select:

```text
Lambda
```

Click:

```text
Next
```

---

## Attach Lambda Logging Permission

Search for:

```text
AWSLambdaBasicExecutionRole
```

Select:

```text
AWSLambdaBasicExecutionRole
```

This policy allows the Lambda function to create CloudWatch log groups, log streams, and write log events.

Click:

```text
Next
```

---

## Enter Role Name

Under:

```text
Role name
```

enter:

```text
ec2-auto-tag-lambda-role
```

You may add a description such as:

```text
Execution role for EC2 automatic tagging Lambda function
```

Click:

```text
Create role
```

---

## Verify IAM Role

Open:

```text
IAM
    ↓
Roles
    ↓
ec2-auto-tag-lambda-role
```

Verify:

```text
Trusted entity:
Lambda
```

and:

```text
Permissions:
AWSLambdaBasicExecutionRole
```

### Screenshot

**Screenshot required:** Yes

Capture:

* IAM role name.
* Lambda trusted entity.
* `AWSLambdaBasicExecutionRole`.

<img width="1138" height="781" alt="image" src="https://github.com/user-attachments/assets/e503b77e-ae6d-49dd-a72b-24fe999bbb6d" />

```

---

# Step 2 – Add EC2 Tagging Permissions

Lambda also needs permission to create EC2 tags.

Open:

```text
IAM
    ↓
Roles
    ↓
ec2-auto-tag-lambda-role
```

Click:

```text
Add permissions
    ↓
Create inline policy
```

Select:

```text
JSON
```

Replace the existing policy with:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowEC2Tagging",
      "Effect": "Allow",
      "Action": [
        "ec2:CreateTags",
        "ec2:DescribeInstances"
      ],
      "Resource": "*"
    }
  ]
}
```

Click:

```text
Next
```

---

## Policy Name

Enter:

```text
EC2AutoTaggingPolicy
```

Click:

```text
Create policy
```

---

## Verify Permissions

Return to:

```text
IAM
    ↓
Roles
    ↓
ec2-auto-tag-lambda-role
    ↓
Permissions
```

You should see:

```text
AWSLambdaBasicExecutionRole
EC2AutoTaggingPolicy
```

Open:

```text
EC2AutoTaggingPolicy
```

Verify the permissions:

```text
ec2:CreateTags
ec2:DescribeInstances
```

The resource is:

```text
*
```

---

## Permission Description

| Permission                    | Purpose                                            |
| ----------------------------- | -------------------------------------------------- |
| `ec2:CreateTags`              | Allows Lambda to create or modify EC2 tags         |
| `ec2:DescribeInstances`       | Allows Lambda to retrieve EC2 instance information |
| `AWSLambdaBasicExecutionRole` | Allows Lambda to write CloudWatch Logs             |

<img width="1916" height="805" alt="image" src="https://github.com/user-attachments/assets/e57c10d1-1a57-414b-a6f5-083086266b52" />

---

# Step 3 – Create Lambda Function

Go to:

```text
AWS Console
    ↓
Lambda
    ↓
Functions
    ↓
Create function
```

Select:

```text
Author from scratch
```

---

## Configure Function

Enter:

| Configuration | Value                   |
| ------------- | ----------------------- |
| Function name | `auto-tag-ec2-instance` |
| Runtime       | Python 3.x              |
| Architecture  | x86_64                  |

---

## Configure Execution Role

Under:

```text
Change default execution role
```

select:

```text
Use an existing role
```

Choose:

```text
ec2-auto-tag-lambda-role
```

Verify the selected role is:

```text
ec2-auto-tag-lambda-role
```

Click:

```text
Create function
```

Wait for the Lambda function to be created.

---

## Verify Lambda Function

The function name should be:

```text
auto-tag-ec2-instance
```

The runtime should be:

```text
Python 3.x
```

The architecture should be:

```text
x86_64
```

The execution role should be:

```text
ec2-auto-tag-lambda-role
```
<img width="1147" height="796" alt="image" src="https://github.com/user-attachments/assets/14545b60-1169-426e-9828-57385d762ced" />

```

---

# Step 4 – Add Lambda Function Code

Open:

```text
Lambda
    ↓
Functions
    ↓
auto-tag-ec2-instance
    ↓
Code
```

Open:

```text
lambda_function.py
```

Delete the default Lambda code.

Paste the following code:

```python
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
```

Click:

```text
Deploy
```

Wait for the deployment to complete.

---

## Lambda Code Explanation

The Lambda function imports Boto3:

```python
import boto3
```

It creates an EC2 client:

```python
ec2 = boto3.client("ec2")
```

The Lambda handler receives the EventBridge event:

```python
def lambda_handler(event, context):
```

The EC2 event details are extracted:

```python
detail = event.get("detail", {})
```

The instance ID is extracted:

```python
instance_id = detail.get("instance-id")
```

The instance state is extracted:

```python
state = detail.get("state")
```

The Lambda creates the following tags:

```text
Environment = AutoTagged
ManagedBy = Lambda
Project = EC2-AutoTagging
```

The tags are applied using:

```python
ec2.create_tags(
    Resources=[instance_id],
    Tags=tags
)
```

---
<img width="781" height="589" alt="image" src="https://github.com/user-attachments/assets/4d7e0fbf-570a-4ae7-9da3-cf64156d7c56" />
```

---

# Step 5 – Understand the EventBridge Event

Amazon EC2 generates a state-change event when the instance changes state.

An event will contain information similar to:

```json
{
  "source": "aws.ec2",
  "detail-type": "EC2 Instance State-change Notification",
  "detail": {
    "instance-id": "i-0123456789abcdef0",
    "state": "running"
  }
}
```

The Lambda function reads:

```text
detail.instance-id
```

and:

```text
detail.state
```

For example:

```text
Instance ID:
i-0123456789abcdef0

State:
running
```

The Lambda then applies the predefined tags.

---

# Step 6 – Create EventBridge Rule

Amazon EventBridge will monitor EC2 state-change events.

Go to:

```text
AWS Console
    ↓
Amazon EventBridge
    ↓
Rules
    ↓
Create rule
```

Enter:

```text
Name:
ec2-auto-tagging-rule
```

Enter a description:

```text
Automatically tag EC2 instances when they enter the running state
```

Select the event bus:

```text
default
```

Select the rule type:

```text
Rule with an event pattern
```

Click:

```text
Next
```

---

# Step 7 – Configure EventBridge Event Pattern

Configure the event pattern so that the rule only matches EC2 instances entering the `running` state.

Use the following event pattern:

```json
{
  "source": [
    "aws.ec2"
  ],
  "detail-type": [
    "EC2 Instance State-change Notification"
  ],
  "detail": {
    "state": [
      "running"
    ]
  }
}
```

---

## Event Pattern Explanation

The first section:

```json
"source": [
  "aws.ec2"
]
```

means the event must originate from Amazon EC2.

The second section:

```json
"detail-type": [
  "EC2 Instance State-change Notification"
]
```

means the event must be an EC2 instance state-change event.

The third section:

```json
"detail": {
  "state": [
    "running"
  ]
}
```

means the rule only matches when the instance enters the `running` state.

Therefore:

```text
EC2 state = running
```

will trigger Lambda.

---
<img width="1148" height="789" alt="image" src="https://github.com/user-attachments/assets/f136847a-e201-402f-8184-8a4c17980d00" />

```

---

# Step 8 – Configure EventBridge Target

Continue to the target configuration.

Under:

```text
Target
```

select:

```text
Target type:
AWS service
```

Select:

```text
Service:
Lambda function
```

Select:

```text
Lambda function:
auto-tag-ec2-instance
```

Verify that the target is:

```text
auto-tag-ec2-instance
```

Continue through the remaining rule configuration.

Review the rule.

Click:

```text
Create rule
```

---

## Expected Configuration

The EventBridge rule should have:

```text
Rule name:
ec2-auto-tagging-rule
```

Event bus:

```text
default
```

Target:

```text
auto-tag-ec2-instance
```

---

EventBridge target:

```text
Lambda function:
auto-tag-ec2-instance
```
<img width="1919" height="850" alt="image" src="https://github.com/user-attachments/assets/20b29765-db6c-4721-a562-35ffe597899c" />

```

---

# Step 9 – Verify EventBridge Rule

Go to:

```text
Amazon EventBridge
    ↓
Rules
```

Find:

```text
ec2-auto-tagging-rule
```

Open the rule.

Verify:

```text
Status:
Enabled
```

Verify the event pattern:

```text
source:
aws.ec2
```

Verify:

```text
detail-type:
EC2 Instance State-change Notification
```

Verify:

```text
state:
running
```

Verify the target:

```text
auto-tag-ec2-instance
```

---

# Step 10 – Verify Lambda Invocation Permission

Go to:

```text
AWS Console
    ↓
Lambda
    ↓
Functions
    ↓
auto-tag-ec2-instance
    ↓
Configuration
    ↓
Permissions
```

Check the resource-based policy.

EventBridge should have permission to invoke:

```text
auto-tag-ec2-instance
```

The permission should be associated with the EventBridge rule:

```text
ec2-auto-tagging-rule
```


---

# Step 11 – Prepare EC2 Test Instance

Go to:

```text
AWS Console
    ↓
EC2
    ↓
Instances
```

Select an EC2 instance that can safely be used for testing.

Record the instance ID.

Example:

```text
i-0123456789abcdef0
```

---

## If the Instance Is Stopped

Select:

```text
Instance state
    ↓
Start instance
```

Wait until the instance reaches:

```text
running
```

---

## If the Instance Is Already Running

For a clean test, stop and start the instance.

Select:

```text
Instance state
    ↓
Stop instance
```

Wait until:

```text
stopped
```

Then select:

```text
Instance state
    ↓
Start instance
```

Wait until:

```text
running
```

The transition to `running` generates the EventBridge event.

---

## Expected EC2 State Flow

```text
stopping
    ↓
stopped
    ↓
pending
    ↓
running
```

The EventBridge rule is specifically looking for:

```text
running
```
<img width="1919" height="852" alt="image" src="https://github.com/user-attachments/assets/21b37c3a-50d1-4953-9e1a-aed457c431e0" />

---

```
```


# Step 12 – Verify EventBridge Trigger

After the EC2 instance reaches the `running` state, EventBridge should match the event.

The expected workflow is:

```text
EC2
    ↓
State = running
    ↓
EventBridge
    ↓
ec2-auto-tagging-rule
    ↓
auto-tag-ec2-instance
```


---

# Step 13 – Verify Lambda Execution

Go to:

```text
AWS Console
    ↓
Lambda
    ↓
Functions
    ↓
auto-tag-ec2-instance
    ↓
Monitor
    ↓
View CloudWatch logs
```

Open the latest log stream.

The logs should contain:

```text
===== EC2 AUTO TAGGING STARTED =====
```

followed by the event.

You should see information similar to:

```text
Instance ID: i-0123456789abcdef0
Instance State: running
```

The Lambda should then print:

```text
Tags applied successfully.
```

The execution should not contain:

```text
AccessDenied
```

or:

```text
InvalidInstanceID
```

---

## Expected Lambda Output

```text
===== EC2 AUTO TAGGING STARTED =====
Event: {...}

Instance ID: i-0123456789abcdef0
Instance State: running

Tags applied successfully.
Tag response: {...}
```

---

---

# Step 14 – Verify EC2 Automatic Tags

Return to:

```text
AWS Console
    ↓
EC2
    ↓
Instances
```

Select the test instance.

Open:

```text
Tags
```

The following tags should now exist:

| Key           | Value             |
| ------------- | ----------------- |
| `Environment` | `AutoTagged`      |
| `ManagedBy`   | `Lambda`          |
| `Project`     | `EC2-AutoTagging` |

These tags should have been created automatically by Lambda.

No manual tag creation should be required.

---


```text
Environment = AutoTagged
ManagedBy = Lambda
Project = EC2-AutoTagging
```
<img width="1148" height="784" alt="image" src="https://github.com/user-attachments/assets/7ef1332f-3e1d-4819-8b5e-3c0249122861" />
<img width="902" height="370" alt="image" src="https://github.com/user-attachments/assets/66d1329c-6158-4449-b4a4-f252d5cedb36" />




---

# Step 15 – Verify CloudWatch Logs

Lambda automatically writes its execution output to CloudWatch Logs.

Go to:

```text
AWS Console
    ↓
CloudWatch
    ↓
Logs
    ↓
Log groups
```

<img width="1666" height="498" alt="image" src="https://github.com/user-attachments/assets/d078001f-9add-4e58-a45d-87396f149d19" />

Open the latest log stream.

Verify:

```text
===== EC2 AUTO TAGGING STARTED =====
```

and:

```text
Instance ID: i-xxxxxxxxxxxxxxxxx
```

and:

```text
Instance State: running
```

and:

```text
Tags applied successfully.
```

### Screenshot

**Screenshot required:** No

The Lambda execution screenshot from Step 13 provides the required evidence.

---

# Step 16 – Verify the Complete Workflow

The complete automation should now work as follows:

```text
EC2 Instance
     |
     | Instance enters running state
     v
Amazon EventBridge
     |
     | Event matches rule
     v
AWS Lambda
     |
     | Boto3 CreateTags
     v
EC2 Instance
     |
     +---- Environment = AutoTagged
     +---- ManagedBy = Lambda
     +---- Project = EC2-AutoTagging
```

The Lambda execution should show:

```text
Instance State: running
Tags applied successfully.
```

The EC2 instance should show:

```text
Environment = AutoTagged
ManagedBy = Lambda
Project = EC2-AutoTagging
```

### Screenshot

**Screenshot required:** No

---

# Testing

## Test Scenario

The automation is tested by changing the state of an EC2 instance.

## Test Procedure

1. Select a test EC2 instance.
2. Stop the instance if it is already running.
3. Wait until the instance reaches `stopped`.
4. Start the instance.
5. Wait until the instance reaches `running`.
6. EC2 generates the state-change event.
7. EventBridge receives the event.
8. EventBridge evaluates the event pattern.
9. The event matches because the state is `running`.
10. EventBridge invokes the Lambda function.
11. Lambda receives the event.
12. Lambda extracts the instance ID.
13. Lambda extracts the instance state.
14. Lambda creates the predefined tags.
15. Lambda calls the EC2 `CreateTags` API.
16. EC2 receives the tags.
17. Lambda writes execution information to CloudWatch Logs.

---

# Expected Workflow

```text
EC2 State Change
       |
       v
EventBridge Rule
       |
       v
Lambda Function
       |
       +----------------------+
       |                      |
       v                      v
EC2 CreateTags          CloudWatch Logs
       |
       v
EC2 Instance
       |
       +-- Environment = AutoTagged
       +-- ManagedBy = Lambda
       +-- Project = EC2-AutoTagging
```

---

# Expected Result

Lambda execution should complete successfully.

Expected CloudWatch output:

```text
===== EC2 AUTO TAGGING STARTED =====

Instance ID: i-0123456789abcdef0
Instance State: running

Tags applied successfully.
```

Expected EC2 tags:

```text
Environment = AutoTagged
ManagedBy = Lambda
Project = EC2-AutoTagging
```

---

```

---

# Final Project Structure

```text
assignment-05-ec2-auto-tagging/
│
├── lambda_function.py
├── README.md

```

---




---



# Conclusion

This assignment demonstrates an event-driven AWS automation workflow using:

* Amazon EC2
* Amazon EventBridge
* AWS Lambda
* AWS IAM
* Amazon CloudWatch Logs
* Python
* Boto3

When an EC2 instance enters the `running` state, Amazon EventBridge detects the state-change event and invokes the Lambda function.

The Lambda function retrieves the EC2 instance ID and state from the EventBridge event.

It then uses the Boto3 EC2 `CreateTags` API to automatically apply the following tags:

```text
Environment = AutoTagged
ManagedBy = Lambda
Project = EC2-AutoTagging
```

The Lambda execution details are recorded in CloudWatch Logs.

The final workflow is:

```text
EC2 Instance
      |
      | State changes to running
      v
Amazon EventBridge
      |
      | Matching EventBridge Rule
      v
AWS Lambda
      |
      | Boto3 CreateTags
      v
EC2 Instance
      |
      +-- Environment = AutoTagged
      +-- ManagedBy = Lambda
      +-- Project = EC2-AutoTagging
```

This completes the EC2 automatic tagging automation using AWS Lambda, EventBridge, IAM, CloudWatch Logs, Python, and Boto3.

