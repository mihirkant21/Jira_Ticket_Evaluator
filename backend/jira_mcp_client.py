import os
import asyncio
import httpx
from typing import Dict, Any, Optional

# Stage 2 - Jira Direct REST API Integration
# The Atlassian MCP package is currently unstable on NPM registries,
# so this client communicates directly with the Jira Cloud REST API.

class JiraMCPClient:
    def __init__(self):
        self.api_token = os.environ.get("JIRA_API_TOKEN", "")
        self.email = os.environ.get("JIRA_EMAIL", "")
        self.domain = os.environ.get("JIRA_DOMAIN", "")
        
        # Ensure domain is formatted correctly
        if self.domain and not self.domain.startswith("http"):
            self.domain = f"https://{self.domain}"

    async def fetch_jira_ticket(self, issue_key: str) -> Optional[Dict[str, Any]]:
        """
        Connects directly to the Jira REST API and fetches full ticket details.
        Maps to Stage 2 of the pipeline.
        """
        if not self.api_token or not self.email or not self.domain:
            print("Missing Jira environment variables (JIRA_API_TOKEN, JIRA_EMAIL, JIRA_DOMAIN)")
            return None
            
        try:
            url = f"{self.domain}/rest/api/3/issue/{issue_key}"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    auth=(self.email, self.api_token),
                    headers={"Accept": "application/json"}
                )
                
                if response.status_code != 200:
                    print(f"Jira API returned status code {response.status_code}: {response.text}")
                    return None
                    
                data = response.json()
                
                # Extract summary and description to mimic the text block normally passed by MCP
                summary = data.get("fields", {}).get("summary", "")
                
                # Jira API v3 uses Atlassian Document Format (ADF) for descriptions
                # We do a basic string dump here to preserve all text context for the LLM
                description_json = data.get("fields", {}).get("description", {})
                import json
                desc_text = json.dumps(description_json) if description_json else ""
                
                content_text = f"Summary: {summary}\n\nDescription Block: {desc_text}"
                
                return {
                    "issue_key": issue_key,
                    "raw_data": content_text
                }
                
        except Exception as e:
            import traceback
            print(f"Error fetching Jira ticket via REST API: {e}")
            traceback.print_exc()
            return None

# Singleton instance for the FastAPI app to use
jira_mcp = JiraMCPClient()
