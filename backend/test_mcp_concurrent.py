import asyncio
import os
import shutil
import traceback
from mcp.client.stdio import stdio_client, StdioServerParameters

npx_path = shutil.which("npx") or "npx"

async def test_github():
    server_params = StdioServerParameters(
        command=npx_path,
        args=["-y", "@modelcontextprotocol/server-github"],
        env={**os.environ, "GITHUB_PERSONAL_ACCESS_TOKEN": "dummy"}
    )
    try:
        async with stdio_client(server_params) as (read, write):
            print("GitHub Successfully connected!")
            return
    except BaseException as e:
        print(f"GitHub Failed. {type(e)}")
        traceback.print_exc()

async def test_jira():
    server_params = StdioServerParameters(
        command=npx_path,
        args=["-y", "@modelcontextprotocol/server-jira"],
        env={**os.environ}
    )
    try:
        async with stdio_client(server_params) as (read, write):
            print("Jira Successfully connected!")
            return
    except BaseException as e:
        print(f"Jira Failed. {type(e)}")
        traceback.print_exc()

async def main():
    await asyncio.gather(test_github(), test_jira())

if __name__ == "__main__":
    asyncio.run(main())
