import boto3
import json
import os
from botocore.config import Config

# Helper module for AWS Bedrock integration with Amazon Nova Models

class BedrockClient:
    def __init__(self, region_name="us-east-1"):
        # We assume standard AWS credentials (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY) 
        # are provided in the environment or via AWS profile.
        config = Config(read_timeout=120)
        self.client = boto3.client(
            service_name="bedrock-runtime",
            region_name=region_name,
            config=config
        )
        
        # Define the models we use based on the 10-stage architecture
        self.NOVA_LITE_MODEL_ID = "us.amazon.nova-lite-v1:0"
        self.NOVA_PRO_MODEL_ID = "us.amazon.nova-pro-v1:0"
        self.TITAN_EMBEDDING_MODEL_ID = "amazon.titan-embed-text-v2:0"

    def invoke_model(self, prompt: str, model_id: str, max_tokens: int = 1000):
        """Generic method to invoke Amazon Nova models via Bedrock Converse API"""
        try:
            response = self.client.converse(
                modelId=model_id,
                messages=[
                    {
                        "role": "user",
                        "content": [{"text": prompt}]
                    }
                ],
                inferenceConfig={"maxTokens": max_tokens}
            )
            return response["output"]["message"]["content"][0]["text"]
        except Exception as e:
            print(f"Error invoking Bedrock Nova model: {e}")
            return None

    def generate_embeddings(self, text: str):
        """Generate text embeddings using Amazon Titan"""
        # Basic input for Titan Text Embeddings
        body = json.dumps({"inputText": text})
        
        try:
            response = self.client.invoke_model(
                body=body,
                modelId=self.TITAN_EMBEDDING_MODEL_ID,
                accept="application/json",
                contentType="application/json"
            )
            response_body = json.loads(response.get("body").read())
            return response_body.get("embedding")
        except Exception as e:
            print(f"Error generating Bedrock Embeddings: {e}")
            return None

# Singleton-like instance
bedrock_client = BedrockClient()
