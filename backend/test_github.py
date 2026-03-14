import asyncio
from dotenv import load_dotenv
load_dotenv()
from github_mcp_client import github_mcp

async def main():
    # Calling fetch_github_pr on the user's PR URL (assuming public PR for test)
    # The actual URL the user might be using or a test one
    pr_url = "https://github.com/Abhinavkumar2025/Jira_Ticket_Evaluator/pull/1"
    
    result = await github_mcp.fetch_github_pr(pr_url)
    
    if result:
        print("Diff text preview (first 200 chars):")
        print(result["pr_files_diffs"][:200])
        print("Metadata preview (first 200 chars):")
        print(result["pr_metadata"][:200])
    else:
        print("Fetch failed.")

if __name__ == "__main__":
    asyncio.run(main())
