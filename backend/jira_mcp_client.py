import os
import asyncio
from typing import Dict, Any, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Stage 2 - Jira MCP Integration
# This client communicates with the official Jira MCP server using standard I/O.
# It requires `npx` to be available to run the MCP server package.

class JiraMCPClient:
    def __init__(self):
        # We use the official @modelcontextprotocol/server-jira package
        self.server_params = StdioServerParameters(
            command="npx",
            args=[
                "-y",
                "@modelcontextprotocol/server-jira"
            ],
            env={
                **os.environ,
                "JIRA_API_TOKEN": os.getenv("JIRA_API_TOKEN", ""),
                "JIRA_EMAIL": os.getenv("JIRA_EMAIL", ""),
                "JIRA_DOMAIN": os.getenv("JIRA_DOMAIN", "")
            }
        )

    async def fetch_jira_ticket(self, issue_key: str) -> Optional[Dict[str, Any]]:
        """
        Connects to the Jira MCP Server and fetches full ticket details.
        Maps to Stage 2 of the pipeline.
        """
        try:
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    # The Jira MCP Server provides a standard "get-issue" tool
                    result = await session.call_tool("get-issue", arguments={"issueKey": issue_key})
                    
                    if not result or not result.content:
                        return None
                        
                    # Parse the text content returned by the MCP tool
                    raw_content = result.content[0].text
                    
                    return {
                        "issue_key": issue_key,
                        "raw_data": raw_content
                    }
                    
        except Exception as e:
            print(f"Error fetching Jira ticket via MCP: {e}")
            return None

# Singleton instance for the FastAPI app to use
jira_mcp = JiraMCPClient()
