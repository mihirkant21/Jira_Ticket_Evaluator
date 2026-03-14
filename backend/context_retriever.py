import json
import re
from bedrock_client import bedrock_client
from github_mcp_client import github_mcp

# Stage 5.5 - Codebase Context Retriever (Haiku + GitHub MCP)

class ContextRetriever:
    def __init__(self):
        self.system_prompt = """
        You are a Code Dependency Analyst.
        You will receive a code diff and a list of changed files.
        Your task is to identify external function calls, class references, or service imports that are USED in the diff but NOT defined within it.
        
        Instructions:
        1. Scan the diff for external references (e.g., `services.AuthService.verify()`).
        2. Identify 2-3 most critical external dependencies that would help understand the logic.
        3. RETURN OUTPUT STRICTLY AS STRUCTURED VALID JSON.
        
        Expected output format:
        {
          "external_references": [
            { "name": "AuthService", "query": "class AuthService", "reason": "Verifies user tokens" }
          ]
        }
        """

    async def fetch_codebase_context(self, pr_diff: str, repo_full_name: str) -> list:
        """
        Identifies and fetches external codebase context (Stage 5.5).
        """
        # Step 1: Identify what to search for using Haiku
        prompt = f"{self.system_prompt}\n\n--- PR Diff ---\n{pr_diff}\n\nStrict JSON Output:"
        
        try:
            response_text = bedrock_client.invoke_claude(
                prompt=prompt,
                model_id=bedrock_client.HAIKU_MODEL_ID,
                max_tokens=1000
            )
            
            if not response_text:
                return []
                
            clean_text = response_text.replace("```json", "").replace("```", "").strip()
            refs = json.loads(clean_text).get("external_references", [])
            
            enriched_context = []
            
            # Step 2: Use GitHub MCP to fetch actual code for those references
            # We'll use the search functionality in the GitHub MCP client
            owner, repo = repo_full_name.split("/")
            
            for ref in refs:
                # We can call 'search-code' tool via GitHub MCP
                # (Note: github_mcp needs to support this tool call)
                search_results = await github_mcp.search_code(ref["query"], owner, repo)
                if search_results:
                    enriched_context.append({
                        "reference": ref["name"],
                        "code": search_results,
                        "reason": ref["reason"]
                    })
            
            return enriched_context
            
        except Exception as e:
            print(f"Error in Context Retriever: {e}")
            return []

context_retriever = ContextRetriever()
