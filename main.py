import asyncio
import sys
from pathlib import Path
from typing import TypedDict

from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents.structured_output import ToolStrategy
from langgraph.graph import StateGraph, START, END


load_dotenv()

class PipelineState(TypedDict):
    question: str
    tools_called: list[str]

class ResearchResponse(BaseModel):
    # topic: str
    # summary: str
    # sources: list[str]
    tools_used: list[str]
    file_path: str


llm = ChatOpenAI(model="gpt-4o")


def build_graph(agent):
    """Graph-based orchestration. For now, just wrap around single node."""
    # Add checkpoint later

    async def research_node(state: PipelineState) -> dict:
        result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": state["question"]}]}
        )
        tools_called = [
            call["name"]
            for m in result["messages"]
            for call in getattr(m, "tool_calls", [])
            if call["name"] != "ResearchResponse"  # ToolStrategy's own "final answer" tool
        ]
        return {
            "file_path": result["structured_response"].file_path,
            "tools_called": tools_called,
        }
        
    graph = StateGraph(PipelineState)
    graph.add_node("research", research_node)
    graph.add_edge(START, "research")
    graph.add_edge("research", END)

    return graph.compile()


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
            "You are a research assistant. "
            "Use search_rag first; if the info is outdated or missing, use search_web. "
            "Then write a well-structured Markdown response (headings, code blocks, sources section) and save it with write_draft_to_file."
        ),
        response_format=ToolStrategy(ResearchResponse),
    )

    # for m in result["messages"]:
    #     m.pretty_print()
    app = build_graph(agent)
    question = input("What can I help you with today? ")
    result = await app.ainvoke({"question": question})
    print(result)



if __name__ == "__main__":
    asyncio.run(main())
