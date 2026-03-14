import boto3
import json

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('JiraEvaluations')

response = table.scan(Limit=5)
items = response.get('Items', [])

for item in items:
    print(f"Jira ID: {item.get('jira_id')}")
    print(f"GitHub PR URL: {item.get('github_pr_url')}")
    print("-" * 20)
