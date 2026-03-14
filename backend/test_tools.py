import asyncio
import os
import shutil
import traceback
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp import ClientSession
from dotenv import load_dotenv

load_dotenv()

npx_path = shutil.which("npx") or "npx"

async def list_github_tools():
    print("--- Listing GitHub MCP Tools ---")
    server_params = StdioServerParameters(
        command=npx_path,
        args=["-y", "@modelcontextprotocol/server-github"],
        env={**os.environ, "GITHUB_PERSONAL_ACCESS_TOKEN": os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN", "dummy")}
    )
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                for t in tools.tools:
                    print(f"- {t.name}: {t.description}")
    except Exception as e:
        print(f"GitHub list tools failed: {type(e)}")
        traceback.print_exc()

async def list_jira_tools():
    print("\n--- Listing Jira MCP Tools ---")
    server_params = StdioServerParameters(
        command=npx_path,
        args=["-y", "@modelcontextprotocol/server-jira"],
        env={
            **os.environ,
            "JIRA_API_TOKEN": os.environ.get("JIRA_API_TOKEN", "dummy"),
            "JIRA_EMAIL": os.environ.get("JIRA_EMAIL", "dummy"),
            "JIRA_DOMAIN": os.environ.get("JIRA_DOMAIN", "dummy")
        }
    )
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                for t in tools.tools:
                    print(f"- {t.name}: {t.description}")
    except Exception as e:
        print(f"Jira list tools failed: {type(e)}")
        traceback.print_exc()

async def main():
    await list_github_tools()
    await list_jira_tools()

if __name__ == "__main__":
    asyncio.run(main())
