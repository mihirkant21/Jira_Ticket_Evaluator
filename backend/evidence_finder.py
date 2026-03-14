import json
from bedrock_client import bedrock_client
from typing import Dict, Any

# Stage 7 - Evidence Finder Agent (Claude Sonnet 4.6)

class EvidenceFinder:
    def __init__(self):
        self.system_prompt = """
        You are an elite QA Engineer and Code Auditor. 
        Your task is to analyze whether a specific piece of code successfully implements a specific requirement.
        
        Instructions:
        1. Think step-by-step. Do not jump to conclusions.
        2. Look for explicit, concrete code evidence that proves the requirement.
        3. Check for edge cases, error handling, or database interactions if the requirement dictates it.
        4. RETURN OUTPUT STRICTLY AS STRUCTURED VALID JSON.
        
        Expected output format if found:
        {
          "requirement_id": 2,
          "statement": "Token must expire in 15 minutes",
          "status": "FOUND",
          "evidence": {
            "file": "auth/token.js",
            "line": "9",
            "code_snippet": "expiresIn: '15m'",
            "explanation": "JWT sign call explicitly sets expiry to 15 minutes"
          },
          "confidence": 0.95
        }
        
        Expected output format if NOT found:
        {
          "requirement_id": 3,
          "statement": "Password must be updated in database",
          "status": "NOT_FOUND",
          "evidence": null,
          "explanation": "No database write operation detected in any changed file snippet provided",
          "confidence": 0.88
        }
        """

    def validate_evidence(self, evidence: dict, pr_files_dict: dict, external_context: list) -> bool:
        """
        Improvement 3: Programmatic Validator.
        Checks:
        1. Does the claimed file exist?
        2. Does the claimed line number exist?
        3. Does the code at that line contain the snippet?
        """
        if not evidence or evidence.get("status") != "FOUND":
            return True # Nothing to validate if not found
            
        file_path = evidence.get("evidence", {}).get("file")
        line_num = evidence.get("evidence", {}).get("line")
        snippet = evidence.get("evidence", {}).get("code_snippet")
        
        if not file_path or not line_num or not snippet:
            return False
            
        # Check in PR diff files
        target_code = pr_files_dict.get(file_path)
        
        # Check in external context if not in diff
        if not target_code:
            for ctx in external_context:
                if f"EXTERNAL:{ctx['reference']}" == file_path:
                    target_code = ctx["code"]
                    break
        
        if not target_code:
            return False # File not found
            
        # Basic line check
        lines = target_code.split("\n")
        try:
            line_idx = int(line_num) - 1
            if line_idx < 0 or line_idx >= len(lines):
                return False # Line out of range
            
            # Fuzzy match snippet in that line or neighboring lines
            context_area = "\n".join(lines[max(0, line_idx-2):min(len(lines), line_idx+3)])
            if snippet.strip().lower() not in context_area.lower():
                return False # Snippet not found in context
                
            return True
        except (ValueError, TypeError):
            return False

    def find_requirement_evidence(self, requirement: Dict[str, Any], retrieved_code_chunks: list, functional_map: dict, pr_files_dict: dict = {}, external_context: list = []) -> dict:
        """
        Takes a single requirement and retrieved chunks.
        Includes a 2x retry loop if evidence validation fails.
        """
        attempts = 0
        max_attempts = 2
        feedback = ""
        
        while attempts < max_attempts:
            prompt = f"""
            {self.system_prompt}
            
            --- Requirement context ---
            Requirement ID: {requirement['id']}
            Requirement Statement: {requirement['statement']}
            Requirement Classification: {requirement.get('classification', 'behavioral')}
            
            --- Relevant Code Snippets (Semantic + Keyword search) ---
            {json.dumps(retrieved_code_chunks, indent=2)}
            
            --- Overall PR Functional Map ---
            {json.dumps(functional_map, indent=2)}
            
            {f"--- FEEDBACK FROM PREVIOUS ATTEMPT ---\\n{feedback}" if feedback else ""}
            
            Analyze deeply and output Strict JSON:
            """
            
            try:
                response_text = bedrock_client.invoke_model(
                    prompt=prompt,
                    model_id=bedrock_client.NOVA_PRO_MODEL_ID,
                    max_tokens=2000
                )
                
                if not response_text:
                    return {"requirement_id": requirement['id'], "status": "ERROR"}
                    
                clean_text = response_text.replace("```json", "").replace("```", "").strip()
                evidence = json.loads(clean_text)
                
                # Improvement 3: Evidence Validator check
                if self.validate_evidence(evidence, pr_files_dict, external_context):
                    return evidence
                else:
                    attempts += 1
                    feedback = "Your previous evidence was invalid. File/line did not match or snippet was not found. Please re-examine the provided code chunks carefully."
                    print(f"Evidence validation failed for Req {requirement['id']}, attempt {attempts}")
                
            except json.JSONDecodeError:
                attempts += 1
            except Exception as e:
                print(f"Error in Evidence Finder: {e}")
                return {"requirement_id": requirement['id'], "status": "ERROR"}
        
        return {"requirement_id": requirement['id'], "status": "NOT_FOUND", "explanation": "Evidence could not be programmatically verified after 2 attempts."}

evidence_finder = EvidenceFinder()
