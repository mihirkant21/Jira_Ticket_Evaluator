import json
from bedrock_client import bedrock_client
from typing import List, Dict, Any

# Stage 9 - Verdict Agent (Claude Haiku 4.5)

class VerdictAgent:
    def __init__(self):
        self.system_prompt = """
        You are the Final Lead Judge.
        You take the raw results of Requirements, Evidence, and Tests, and produce the final, definitive Verdict.
        
        Logic Rules:
        - If ALL requirements have evidence and tests PASS -> PASS
        - If SOME requirements have evidence but some are missing -> PARTIAL
        - If NO or VERY FEW requirements have evidence -> FAIL
        
        RETURN OUTPUT STRICTLY AS STRUCTURED VALID JSON.
        
        Expected output format:
        {
          "overall_verdict": "PARTIAL",
          "requirements": [
            {
              "id": 1,
              "statement": "Reset email must be sent",
              "verdict": "PASS",
              "evidence": "auth/email.js line 15",
              "test_result": "PASS",
              "confidence": 0.93
            }
          ],
          "summary": "2 of 3 requirements implemented. Database update logic is missing."
        }
        """

    def generate_final_verdict(self, requirements: List[dict], evidence_results: List[dict], test_results: List[dict], planner_info: dict = {}) -> dict:
        """
        Creates the final unified JSON Verdict aggregating all previous stages (Stage 9).
        Includes Planner's decisions in the justification.
        """
        prompt = f"""
        {self.system_prompt}
        
        --- Data ---
        Requirements: {json.dumps(requirements, indent=2)}
        Evidence Results: {json.dumps(evidence_results, indent=2)}
        Test Results: {json.dumps(test_results, indent=2)}
        Planner Logic: {json.dumps(planner_info, indent=2)}
        
        Strict JSON Output:
        """
        
        try:
            response_text = bedrock_client.invoke_model(
                prompt=prompt,
                model_id=bedrock_client.NOVA_LITE_MODEL_ID,
                max_tokens=2000
            )
            
            if not response_text:
                return {"overall_verdict": "ERROR", "summary": "Failed to generate verdict."}
                
            clean_text = response_text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_text)
            
        except Exception as e:
            print(f"Error in Verdict Agent: {e}")
            return {
                "overall_verdict": "ERROR",
                "summary": f"Exception occurred: {e}",
                "requirements": []
            }

verdict_agent = VerdictAgent()
