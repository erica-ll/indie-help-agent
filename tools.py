import sys
import os
from pathlib import Path
from fastmcp import FastMCP
from langchain_community.tools import DuckDuckGoSearchRun, WikipediaQueryRun
from dotenv import load_dotenv

mcp = FastMCP("IndieHelp research tools")

web_search = DuckDuckGoSearchRun()

load_dotenv(Path(__file__).with_name(".env"))
RAG_REPO_PATH = Path(os.environ["RAG_REPO_PATH"]).resolve()
sys.path.insert(0, str(RAG_REPO_PATH / "src"))
from run_pipeline import run as rag_run

@mcp.tool
def search_web(query: str) -> str:
    """Search the web for current or general information about a query."""
    return web_search.run(query)

@mcp.tool
def search_rag(question: str) -> str:
    """Search the IndieHelp knowledge base for an answer."""
    return rag_run(question)["answer"]


if __name__ == "__main__":
    mcp.run()
