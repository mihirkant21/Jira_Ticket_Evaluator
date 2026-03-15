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
        1. Does the claimed code snippet exist anywhere in the PR diff or external context?
        """
        import re
        if not evidence or evidence.get("status") != "FOUND":
            return True # Nothing to validate if not found
            
        snippet = evidence.get("evidence", {}).get("code_snippet")
        
        if not snippet:
            return False
            
        snippet_lower = snippet.strip().lower()
        normalized_snippet = re.sub(r'[\s\+\-]', '', snippet_lower)
        print(f"DEBUG: AI suggested snippet [{snippet_lower}]")
        
        # Check in PR diff files
        for target_code in pr_files_dict.values():
            if target_code:
                normalized_target = re.sub(r'[\s\+\-]', '', target_code.lower())
                if normalized_snippet in normalized_target:
                    print("DEBUG: Snippet validated successfully!")
                    return True
                
        # Check in external context if not in diff
        for ctx in external_context:
            target_code = ctx.get("code", "")
            if target_code:
                normalized_target = re.sub(r'[\s\+\-]', '', target_code.lower())
                if normalized_snippet in normalized_target:
                    return True
                
        return False
            
        snippet_lower = snippet.strip().lower()
        print(f"DEBUG: AI suggested snippet [{{snippet_lower}}]")
        
        # Check in PR diff files
        for target_code in pr_files_dict.values():
            if target_code:
                # print(f"DEBUG: Diff content [{{target_code}}]") # Too noisy
                if snippet_lower in target_code.lower():
                    print("DEBUG: Snippet validated successfully!")
                    return True
            if target_code and snippet_lower in target_code.lower():
                return True
                
        # Check in external context if not in diff
        for ctx in external_context:
            target_code = ctx.get("code", "")
            if target_code:
                normalized_target = re.sub(r'[\s\+\-]', '', target_code.lower())
                if normalized_snippet in normalized_target:
                    return True
                
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
            feedback_section = f"--- FEEDBACK FROM PREVIOUS ATTEMPT ---\n{feedback}" if feedback else ""
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
            
            {feedback_section}
            
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

