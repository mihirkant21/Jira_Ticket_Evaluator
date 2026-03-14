import boto3
import uuid
import datetime
import os
import json
from botocore.exceptions import ClientError

# Stage 10 - Persisting Evaluation Data to DynamoDB

class DynamoDBClient:
    def __init__(self, table_name="JiraEvaluations", region_name="us-east-1"):
        self.dynamodb = boto3.resource('dynamodb', region_name=region_name)
        self.table_name = table_name
        self.table = self.dynamodb.Table(self.table_name)
        
    def create_table_if_not_exists(self):
        """Creates the DynamoDB table if it doesn't already exist."""
        try:
            self.dynamodb.meta.client.describe_table(TableName=self.table_name)
            print(f"DynamoDB Table {self.table_name} already exists.")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print(f"Creating DynamoDB table {self.table_name}...")
                self.dynamodb.create_table(
                    TableName=self.table_name,
                    KeySchema=[
                        {'AttributeName': 'eval_id', 'KeyType': 'HASH'}
                    ],
                    AttributeDefinitions=[
                        {'AttributeName': 'eval_id', 'AttributeType': 'S'}
                    ],
                    BillingMode='PAY_PER_REQUEST'
                )
                print("Table creation successfully requested. It may take a moment to become active.")
            else:
                print(f"Error checking/creating table: {e}")

    def save_evaluation(self, jira_id: str, github_pr_url: str, final_verdict: dict) -> str:
        """Saves the Stage 9 verdict into DynamoDB and returns the unique eval_id."""
        eval_id = str(uuid.uuid4())
        timestamp = datetime.datetime.utcnow().isoformat()
        
        from decimal import Decimal
        
        # Boto3 DynamoDB requires floats to be cast to Decimal
        # The easiest way to deep convert a nested dict is json dump & load with parse_float
        clean_verdict = json.loads(json.dumps(final_verdict), parse_float=Decimal)
        
        item = {
            "eval_id": eval_id,
            "jira_id": jira_id,
            "github_pr_url": github_pr_url,
            "timestamp": timestamp,
            "final_verdict": clean_verdict
        }
        
        try:
            self.table.put_item(Item=item)
            return eval_id
        except Exception as e:
            print(f"Error saving to DynamoDB: {e}")
            return None

# Singleton instance
dynamodb_client = DynamoDBClient()
