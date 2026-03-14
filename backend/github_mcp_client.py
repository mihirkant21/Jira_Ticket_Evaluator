import os
import asyncio
from typing import Dict, Any, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Stage 4 - GitHub PR Data Fetching
# Uses the official GitHub MCP server to securely fetch PR details and diffs

class GithubMCPClient:
    def __init__(self):
        self.server_params = StdioServerParameters(
            command="npx",
            args=[
                "-y",
                "@modelcontextprotocol/server-github"
            ],
            env={
                **os.environ,
                "GITHUB_PERSONAL_ACCESS_TOKEN": os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN", "")
            }
        )

    async def fetch_github_pr(self, pr_url: str) -> Optional[Dict[str, Any]]:
        """
        Connects to the GitHub MCP Server and fetches PR data (Stage 4).
        """
        try:
            # Parse the owner, repo, and PR number from the URL
            # Expecting format: https://github.com/owner/repo/pull/123
            parts = pr_url.rstrip("/").split("/")
            if "pull" not in parts or len(parts) < 4:
                return None
            
            pr_number = int(parts[-1])
            repo = parts[-3]
            owner = parts[-4]
            repo_full_name = f"{owner}/{repo}"

            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    # 1. Fetch Pull Request Metadata
                    pr_result = await session.call_tool(
                        "get-pull-request", 
                        arguments={"owner": owner, "repo": repo, "pullNumber": pr_number}
                    )
                    
                    # 2. Fetch Changed Files & Diffs
                    # Depending on the precise MCP tool available, this might be `get-pull-request-files` 
                    # For now, we fetch the raw description which usually contains a lot of info
                    files_result = await session.call_tool(
                         "search-repositories", # Fallback context tool
                         arguments={"query": f"repo:{repo_full_name} pr:{pr_number}"}
                    )
                    
                    pr_text = pr_result.content[0].text if pr_result and pr_result.content else ""
                    files_text = files_result.content[0].text if files_result and files_result.content else ""
                    
                    return {
                        "pr_metadata": pr_text,
                        "pr_files_diffs": files_text
                    }
                    
        except Exception as e:
            print(f"Error fetching GitHub PR via MCP: {e}")
            return None
                    
    async def search_code(self, query: str, owner: str, repo: str) -> str:
        """
        Searches for code within the repository using GitHub MCP.
        Useful for Stage 5.5 Context Retrieval.
        """
        try:
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    # Tool: search-code (standard in GitHub MCP server)
                    result = await session.call_tool(
                        "search-code", 
                        arguments={"q": f"{query} repo:{owner}/{repo}"}
                    )
                    
                    if result and result.content:
                        return result.content[0].text
                    return ""
        except Exception as e:
            print(f"Error searching GitHub code via MCP: {e}")
            return ""

github_mcp = GithubMCPClient()
