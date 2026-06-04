# Mohit Research Agent

A LangGraph-powered research agent that searches the web, reads source pages, summarises findings, and synthesises a final answer — built as part of a 30-day AI engineering curriculum.

---

## Architecture

```
search_node  →  read_url_node  →  [conditional loop]
                                       │
                              (enough sources?)
                               NO ↙        YES ↘
                         search_node      summarise_node  →  synthesise_node
```

| Node | Responsibility |
|---|---|
| `search_node` | DuckDuckGo search — returns top 5 results |
| `read_url_node` | Fetches and strips HTML from top 3 URLs |
| `summarise_node` | LLM summarises each source into 3 bullet points |
| `synthesise_node` | LLM combines all summaries into a final answer |
| `should_search_more` | Conditional edge — loops back if fewer than 4 sources found |

---

## Stack

- **[LangGraph](https://github.com/langchain-ai/langgraph)** — agent graph orchestration
- **[Groq](https://groq.com)** — LLM inference (llama-3.3-70b-versatile)
- **[DuckDuckGo Search](https://pypi.org/project/duckduckgo-search/)** — web search
- **[httpx](https://www.python-httpx.org/)** — HTTP fetching
- **[LangSmith](https://smith.langchain.com)** — observability and tracing

---

## Observability

Tracing is enabled via LangSmith. Every run produces a full trace with per-node latency in the LangSmith dashboard.

**Profiling finding (Day 14):**
> Bottleneck: `read_url_node` avg ~4–6s — caused by sequential HTTP fetches in a for loop. `summarise_node` also spikes on complex queries due to sequential LLM calls per source.

---

## Setup

```bash
git clone https://github.com/mohit746/mohit-research-agent.git
cd mohit-research-agent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file:

```
GROQ_API_KEY=your_groq_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_PROJECT=mohit-research-agent
```

Run the agent:

```bash
python refined_graph_search.py
```

---

## Progress

| Day | Topic |
|---|---|
| 11–12 | LangGraph foundation — search and read_url nodes |
| 13 | Full pipeline — summarise, synthesise, conditional loop |
| 14 | LangSmith observability — tracing, profiling, bottleneck analysis |
