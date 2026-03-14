import json
from bedrock_client import bedrock_client

# Stage 5 - PR Analyzer Agent (Claude Haiku 4.5)

class PRAnalyzer:
    def __init__(self):
        self.system_prompt = """
        You are an Expert Senior Code Reviewer.
        You will receive the metadata of a GitHub Pull Request, including the description, commit messages, and a list of changed files with their paths (but NOT the full code diff yet).
        
        Instructions:
        1. Read each changed file name and path.
        2. Read PR description and commit messages.
        3. Infer the functional purpose of each file change.
        4. Identify the overall purpose of this PR.
        5. RETURN OUTPUT STRICTLY AS STRUCTURED VALID JSON. Do not include markdown or explanations.
        
        Expected output format:
        {
          "pr_purpose": "Implements password reset flow",
          "file_map": [
            { "file": "auth/reset.js", "purpose": "Password reset controller logic" },
            { "file": "auth/email.js", "purpose": "Email dispatch for reset link" }
          ]
        }
        """

    def analyze_pr_structure(self, pr_metadata: str, pr_files: str, requirements_context: str = "") -> dict:
        """
        Takes PR metadata and file lists and uses Claude Haiku to map the architectural intent (Stage 5).
        Optional requirements_context helps the agent focus on relevant parts of the PR.
        """
        prompt = f"{self.system_prompt}\n\n--- Requirements Context ---\n{requirements_context}\n\n--- PR Metadata ---\n{pr_metadata}\n\n--- Files ---\n{pr_files}\n\nStrict JSON Output:"
        
        try:
            # We use Haiku 4.5 for rapid structural analysis of the PR metadata
            response_text = bedrock_client.invoke_claude(
                prompt=prompt,
                model_id=bedrock_client.HAIKU_MODEL_ID,
                max_tokens=1500
            )
            
            if not response_text:
                return {"pr_purpose": "unknown", "file_map": []}
                
            clean_text = response_text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_text)
            
        except json.JSONDecodeError:
            print("Failed to parse Claude PR Analyzer Output as JSON")
            return {"pr_purpose": "unknown", "file_map": []}
        except Exception as e:
            print(f"Error in PR Analyzer: {e}")
            return {"pr_purpose": "unknown", "file_map": []}

pr_analyzer = PRAnalyzer()
