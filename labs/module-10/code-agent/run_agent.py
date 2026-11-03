"""Ask the agent one question; print the answer, the tool trace and the usage. (Lab 01; Lab 02 step 7)

  python run_agent.py "Why did build b-1234 fail?"                  # your Copilot sign-in
  python run_agent.py --offline "Why did build b-1234 fail?"        # scripted local model (plumbing only)
  python run_agent.py --docs docs "What is our rollback window?"    # grounded: adds search_docs over ./docs
  python run_agent.py --docs docs --strict "..."                    # grounded, with the stronger instructions
"""
import argparse
import asyncio

from agent.agent import ask, new_client


async def main(a):
    async with new_client() as client:
        ans = await ask(client, a.question, docs=a.docs, strict=a.strict)
    print("ANSWER:", ans.text)
    print("TRACE :")
    for t in ans.trace:
        print("  ", t)
    print("USAGE :", ans.usage)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("question", nargs="?", default="Why did build b-1234 fail?")
    p.add_argument("--offline", action="store_true")
    p.add_argument("--docs", default=None, help="folder of .md files to ground the agent on")
    p.add_argument("--strict", action="store_true")
    args = p.parse_args()
    if args.offline:
        import mock_model
        mock_model.use_offline()
    asyncio.run(main(args))
