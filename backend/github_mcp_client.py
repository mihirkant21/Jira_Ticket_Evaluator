import os
import asyncio
import shutil
from typing import Dict, Any, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Stage 4 - GitHub PR Data Fetching
# Uses the official GitHub MCP server to securely fetch PR details and diffs

class GithubMCPClient:
    def get_server_params(self):
        npx_path = shutil.which("npx") or "npx"
        return StdioServerParameters(
            command=npx_path,
            args=[
                "-y",
                "@modelcontextprotocol/server-github"
            ],
            env={
                **os.environ,
                "GITHUB_PERSONAL_ACCESS_TOKEN": os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN", "")
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

            params = self.get_server_params()
            async with stdio_client(params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    # 1. Fetch Pull Request Metadata (MCP Server)
                    pr_result = await session.call_tool(
                        "get_pull_request", 
                        arguments={"owner": owner, "repo": repo, "pull_number": pr_number}
                    )
                    
                    # 2. Fetch Actual Code Diff (via httpx)
                    # The MCP Server doesn't natively expose the raw diff directly,
                    # but GitHub makes it available effortlessly via .diff URL
                    import httpx
                    diff_text = ""
                    try:
                        async with httpx.AsyncClient() as client:
                            resp = await client.get(f"{pr_url.rstrip('/')}.diff")
                            if resp.status_code == 200:
                                diff_text = resp.text
                            else:
                                print(f"Warning: Failed to fetch diff, status was {resp.status_code}")
                    except Exception as he:
                        print(f"Error fetching diff natively: {he}")
                    
                    pr_text = pr_result.content[0].text if pr_result and pr_result.content else ""
                    
                    return {
                        "pr_metadata": pr_text,
                        "pr_files_diffs": diff_text
                    }
                    
        except Exception as e:
            import traceback
            print(f"Error fetching GitHub PR via MCP: {e}")
            traceback.print_exc()
            return None
                    
    async def search_code(self, query: str, owner: str, repo: str) -> str:
        """
        Searches for code within the repository using GitHub MCP.
        Useful for Stage 5.5 Context Retrieval.
        """
        try:
            params = self.get_server_params()
            async with stdio_client(params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    # Tool: search-code (standard in GitHub MCP server)
                    result = await session.call_tool(
                        "search_code", 
                        arguments={"q": f"{query} repo:{owner}/{repo}"}
                    )
                    
                    if result and result.content:
                        return result.content[0].text
                    return ""
            return ""
        except Exception as e:
            print(f"Error searching GitHub code via MCP: {e}")
            return ""

github_mcp = GithubMCPClient()
