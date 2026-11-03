"""Preflight for Module 10: is the SDK runtime available, are you signed in, which models can you use?

Makes no model calls, so it spends none of your Copilot usage.   python check_setup.py
"""
import asyncio

from copilot import CopilotClient


async def main():
    async with CopilotClient() as client:
        status = await client.get_status()
        print("runtime:", status)
        auth = await client.get_auth_status()
        print("auth   :", auth)
        models = await client.list_models()
        print(f"models : {len(models)} available")
        for m in models:
            print("  -", getattr(m, "id", m))


asyncio.run(main())
