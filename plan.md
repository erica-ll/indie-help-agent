## Phase 1: The Monolithic Agent (Single Graph)

Before coordinating multiple agents, you must prove you can build a single agent that reliably manages state and handles tool-calling loops without getting stuck.

**The Goal:** A single LangGraph agent that can search your documentation, draft a response, and save it.

**Tech Stack:**

- **Orchestration:** LangGraph (Python) for the state machine.
- **LLM:** OpenAI (GPT-4o) or Anthropic (Claude 3.5 Sonnet) via LangChain.
- **Tooling Protocol:** `langchain-mcp-adapters` and FastMCP (to expose Python functions as MCP tools).
- **Vector Database:** ChromaDB (since you have experience here) or pgvector.

**Required Tools (Built as an MCP Server):**

1. `query_rag_docs(query)`: Searches ChromaDB for design patterns or technical documentation.
2. `web_search(query)`: Uses Tavily API to fetch current public information (e.g., current API syntax).
3. `write_draft_to_file(content, filename)`: Saves the agent's drafted response to a local Markdown file.

**The Architecture:** The agent runs in a single LangGraph cycle. It receives a prompt, decides to call `query_rag_docs`, gets the context, decides it needs more info, calls `web_search`, synthesizes the data, and calls `write_draft_to_file`.

## Phase 2: The Supervisor Architecture (Multi-Agent Routing)

Once Phase 1 works, a single agent will become bloated and confused if you keep adding tools. Phase 2 breaks the monolith into specialized workers managed by a Supervisor.

**The Goal:** A LangGraph Supervisor that routes tasks to either a Research Agent or a Drafting Agent based on the user's prompt.

**Tech Stack Additions:**

- **Multi-Agent Structure:** LangGraph (using `Command` or conditional edges for routing).
- **State Management:** Standardized LangGraph `State` schema to pass context between nodes.

**The Decomposition:**

- **Supervisor Node:** An LLM that does no actual work. It only analyzes the user request and routes it to the correct worker node.
- **Research Agent:** Inherits the `query_rag_docs` and `web_search` MCP tools. Its only job is to gather facts and return them to the Supervisor.
- **Drafting Agent:** Inherits the `write_draft_to_file` MCP tool. It takes the facts from the Research Agent (passed via graph state) and formats them into a cohesive document.

## Phase 3: The Executable Loop (Adding the Code Agent)

This is the portfolio centerpiece. You transition the system from passively drafting text to actively verifying code.

**The Goal:** Add a Coding Agent that can write C# or Python, test it, read the errors, and rewrite it autonomously before the user ever sees the output.

**Tech Stack Additions:**

- **Sandboxed Execution:** Docker (for safe Python execution) or a local shell subprocess (for testing Unity C# compilation).
- **Observability:** LangSmith (to visualize the agent's internal loops for your portfolio write-up).

**Required Tools for the Coding Agent:**

1. `read_file(filepath)`: To ingest existing code.
    
    freeCodeCamp
    
2. `write_file(filepath, code)`: To save the script.
3. **The Verifier Tool:** `run_python_script(filepath)` or `compile_csharp(filepath)`. This tool must capture `stderr` (compilation or runtime errors) and return it to the agent as a string.