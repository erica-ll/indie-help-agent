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
    try:
        results = rag_run(question)["answer"]
        return results
    except Exception as e:
        return f"RAG Search faild{ str(e)}"


DRAFTS_DIR = Path(__file__).with_name("drafts")

@mcp.tool
def write_draft_to_file(content: str, filename: str) -> str:
    """Save a finished Markdown draft to a local file. Call this once the response is fully written.
    `content` is the complete Markdown text; `filename` is a short name like 'unity-input-system'."""
    try:
        DRAFTS_DIR.mkdir(exist_ok=True)
        safe_name = Path(filename).stem + ".md"   # strip directories/extensions the LLM might add
        path = DRAFTS_DIR / safe_name
        path.write_text(content, encoding="utf-8")
        return f"Draft saved to {path}"
    except Exception as e:
        return f"Failed to save draft: {e}"



if __name__ == "__main__":
    mcp.run()
