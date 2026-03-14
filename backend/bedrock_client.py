import boto3
import json
import os
from botocore.config import Config

# Helper module for AWS Bedrock integration

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
        self.HAIKU_MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"
        self.SONNET_MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"
        self.TITAN_EMBEDDING_MODEL_ID = "amazon.titan-embed-text-v2:0"

    def invoke_claude(self, prompt: str, model_id: str, max_tokens: int = 1000):
        """Generic method to invoke Anthropic Claude models via Bedrock"""
        
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}]
                }
            ]
        })

        try:
            response = self.client.invoke_model(
                body=body,
                modelId=model_id,
                accept="application/json",
                contentType="application/json"
            )
            response_body = json.loads(response.get("body").read())
            return response_body["content"][0]["text"]
        except Exception as e:
            print(f"Error invoking Bedrock Claude: {e}")
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
