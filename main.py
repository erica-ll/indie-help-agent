import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()


class ResearchResponse(BaseModel):
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str]


llm = ChatOpenAI(model="gpt-4o-mini")


async def main():
    tools_server_path = Path(__file__).with_name("tools.py")
    client = MultiServerMCPClient(
        {
            "research": {
                "transport": "stdio",
                "command": sys.executable,
                "args": [str(tools_server_path)],
            }
        }
    )
    tools = await client.get_tools()

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=(
            "You are a research assistant. Answer the user's research question clearly. "
            "Use the available search tools when useful, and only cite sources you can identify accurately."
        ),
        response_format=ResearchResponse,
    )

    query = input("What can I help you with today? ")
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": query}]}
    )
    print(result["structured_response"])


if __name__ == "__main__":
    asyncio.run(main())
