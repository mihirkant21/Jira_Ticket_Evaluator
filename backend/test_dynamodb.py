import time
from dynamodb_client import dynamodb_client

print("Testing DynamoDB Table creation...")
dynamodb_client.create_table_if_not_exists()
print("Success! Table initialized.")

eval_id = dynamodb_client.save_evaluation(
    jira_id="TEST-123",
    github_pr_url="https://github.com/test",
    final_verdict={"overall_verdict": "PASS"}
)
print(f"Saved evaluation with eval_id: {eval_id}")
