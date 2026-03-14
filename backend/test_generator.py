import json
from bedrock_client import bedrock_client
from typing import Dict, Any

# Stage 8 - Test Generator Agent (Claude Sonnet 4.6)

class TestGenerator:
    def __init__(self):
        self.system_prompt = """
        You are a Senior Test Engineer.
        For a given requirement and the evidence found, you will generate a specific test case.
        
        Ticket Types mapping:
        - Feature -> unit test verifying new behavior
        - Bug -> regression test verifying fix
        - Refactor -> structural test verifying no behavior change
        
        Instructions:
        1. Write the test code in Python or JS depending on the snippet's language.
        2. KEEP IT STRICTLY AS JSON output.
        
        Expected output format:
        {
          "requirement_id": 2,
          "test_code": "def test_token_expiry():\\n  assert True",
          "supports_verdict": true
        }
        """

    async def generate_and_run_tests(self, requirement: dict, evidence: dict, code_snippet: str, ticket_type: str) -> dict:
        """
        Generates specialized test cases based on requirement classification (Stage 8).
        """
        classification = requirement.get("classification", "behavioral")
        prompt = f"""
        {self.system_prompt}
        
        Ticket Type: {ticket_type}
        Requirement: {requirement['statement']}
        Classification: {classification}
        Evidence Found: {json.dumps(evidence)}
        Original Code Snippet: {code_snippet}
        
        Note: Since this is a {classification} requirement, generate a test focusing specifically on {classification} aspects.
        
        Strict JSON Output:
        """
        
        try:
            response_text = bedrock_client.invoke_claude(
                prompt=prompt,
                model_id=bedrock_client.SONNET_MODEL_ID,
                max_tokens=1000
            )
            
            if not response_text:
                return {"requirement_id": requirement['id'], "test_code": "", "test_result": "ERROR"}
                
            clean_text = response_text.replace("```json", "").replace("```", "").strip()
            result = json.loads(clean_text)
            
            # Step 8b: Test Execution (Simulated for safety in this scope)
            # A real implementation would run this in Docker or a secure python sandbox
            # and capture the actual test_output.
            result["test_result"] = "PASS" if evidence and evidence.get("status") == "FOUND" else "FAIL"
            result["execution_output"] = "Simulated run successful." if result["test_result"] == "PASS" else "Simulated run failed. Missing implementation."
            
            return result
            
        except Exception as e:
            print(f"Error in Test Generator: {e}")
            return {
                "requirement_id": requirement['id'],
                "test_code": "# code generation failed",
                "test_result": "ERROR",
                "execution_output": str(e)
            }

test_generator = TestGenerator()
