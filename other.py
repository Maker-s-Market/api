import boto3
import json

# Create a Lambda client
client = boto3.client(
    'lambda',
    region_name="us-east-1",
    aws_access_key_id="AKIAVY7OHB33BVFZX4WZ",
    aws_secret_access_key="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"
)

# Invoke the Lambda function
response = client.invoke(
    FunctionName='lambda_func',
    InvocationType='RequestResponse',
    Payload=json.dumps({'key1': 'value1', 'key2': 'value2'}).encode()
)

# Read and print the response
response_payload = json.loads(response['Payload'].read())
print(response_payload)

