from fastmcp import FastMCP
from langchain_community.tools import DuckDuckGoSearchRun, WikipediaQueryRun

mcp = FastMCP("IndieHelp research tools")

web_search = DuckDuckGoSearchRun()

@mcp.tool
def search_web(query: str) -> str:
    """Search the web for current or general information about a query."""
    return web_search.run(query)

if __name__ == "__main__":
    mcp.run()
