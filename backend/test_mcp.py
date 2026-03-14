import asyncio
import os
import shutil
import traceback
from mcp.client.stdio import stdio_client, StdioServerParameters

async def main():
    npx_path = shutil.which("npx") or "npx"
    print(f"Using npx path: {npx_path}")
    
    server_params = StdioServerParameters(
        command=npx_path,
        args=["-y", "@modelcontextprotocol/server-github"],
        env={**os.environ, "GITHUB_PERSONAL_ACCESS_TOKEN": "dummy"}
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            print("Successfully connected!")
            return
    except BaseException as e:
        print(f"Failed to connect. Error type: {type(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
