# 🤖 Mohit Research Agent

A production-grade **LangGraph-powered research agent** that autonomously searches the web, reads source pages, summarizes findings, and synthesizes comprehensive answers. Built with observability and performance profiling as a 30-day AI engineering curriculum project.

---

## 🎯 What It Does

The agent answers any question by:

1. **🔍 Search** — Uses DuckDuckGo to find 5 relevant sources
2. **📖 Read** — Fetches and extracts clean text from the top 3 URLs
3. **✍️ Summarize** — LLM creates 3-bullet summaries of each source
4. **🔄 Loop** — Repeats search if fewer than 4 sources found (max 4 iterations)
5. **🧠 Synthesize** — LLM combines all summaries into a final, coherent answer

**Result:** A well-researched, cited answer in seconds.

---

## 🏗️ System Architecture

```
┌─────────────┐
│   User      │
│  Question   │
└──────┬──────┘
       │
       ▼
┌──────────────────────────────────────────────┐
│          LANGGRAPH RESEARCH AGENT             │
│                                               │
│  ┌──────────────┐                            │
│  │  search_node │ (DuckDuckGo API)           │
│  │  Get 5 URLs  │                            │
│  └───────┬──────┘                            │
│          │                                   │
│          ▼                                   │
│  ┌──────────────────┐                        │
│  │ read_url_node    │ (httpx + HTML strip)   │
│  │ Extract text     │                        │
│  └────────┬─────────┘                        │
│           │                                  │
│           ▼                                  │
│  ┌────────────────────────┐                  │
│  │ should_search_more?    │ (Conditional)    │
│  │ sources < 4 & iter < 4 │                  │
│  └──┬───────────────┬─────┘                  │
│  NO │               │ YES                    │
│     ▼               ▼                        │
│  ┌────────────┐ ┌──────────────┐            │
│  │summarise   │ │ search_node  │ (loop)     │
│  │node        │ └──────────────┘            │
│  │(Groq LLM)  │         ▲                   │
│  └─────┬──────┘         │                   │
│        │                │                   │
│        └────────────────┘                   │
│              (repeats)                      │
│        ▼                                    │
│  ┌─────────────────┐                        │
│  │ synthesise_node │ (Groq LLM)             │
│  │ Final Answer    │                        │
│  └────────┬────────┘                        │
└───────────┼────────────────────────────────┘
            │
            ▼
       ┌──────────┐
       │  Answer  │
       └──────────┘
```

### Node Responsibilities

| Node | Responsibility | Tech |
|---|---|---|
| **search_node** | Query web search API, return top 5 results | DuckDuckGo Search |
| **read_url_node** | Fetch HTML, strip tags, extract clean text (max 2000 chars) | httpx + regex |
| **should_search_more** | Conditional logic — loop if sources < 4 AND iterations < 4 | Python logic |
| **summarise_node** | LLM summarizes each source into 3 bullet points | Groq (llama-3.3-70b) |
| **synthesise_node** | LLM combines summaries into a final, coherent answer | Groq (llama-3.3-70b) |

---

## 🚀 Streamlit UI

Run the **interactive web UI**:

```bash
streamlit run app.py
```

Features:
- 🎨 Clean, centered interface
- 📝 Real-time progress tracking (shows each research phase)
- ✅ Final answer displayed in markdown with formatting
- ⚡ One-click research

**UI Flow:**
1. User enters question in text input
2. Clicks "Submit"
3. Status block shows: "Searching..." → "Reading URLs..." → "Summarizing..." → "Synthesizing..."
4. Final answer appears below

---

## 🛠️ Tech Stack

| Component | Purpose | Library |
|---|---|---|
| **Graph Orchestration** | Workflow automation & conditional logic | [LangGraph](https://github.com/langchain-ai/langgraph) |
| **LLM Inference** | Fast, accurate completions | [Groq](https://groq.com) (llama-3.3-70b-versatile) |
| **Web Search** | Source discovery | [DuckDuckGo Search](https://pypi.org/project/duckduckgo-search/) |
| **HTTP Client** | URL fetching with timeouts | [httpx](https://www.python-httpx.org/) |
| **Web UI** | Interactive interface | [Streamlit](https://streamlit.io/) |
| **Observability** | Distributed tracing & performance profiling | [LangSmith](https://smith.langchain.com) |

---

## 📊 Observability & Profiling

**LangSmith Integration:**
- Every run generates a full trace with per-node latency
- View traces at: https://smith.langchain.com/projects/mohit-research-agent

**Profiling Findings (Day 14):**
```
Bottleneck Analysis:
├─ read_url_node:  ~4–6s (sequential HTTP fetches)
├─ summarise_node: spikes on complex queries (sequential LLM calls)
└─ search_node:    ~1–2s (API call overhead)
```

**Future Optimization:** Parallelize HTTP fetches and LLM calls using `asyncio`.

---

## 🔧 Setup & Installation

### Prerequisites
- Python 3.10+
- API keys: Groq, LangSmith (optional)
- Internet connection (for web search)

### Install

```bash
git clone https://github.com/mohit746/mohit-research-agent.git
cd mohit-research-agent
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Environment Variables

Create `.env` file:

```bash
# Required
GROQ_API_KEY=your_groq_api_key

# Optional (for tracing)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_PROJECT=mohit-research-agent
```

### Run

**Interactive UI:**
```bash
streamlit run app.py
```

**CLI (Direct):**
```bash
python refined_graph_search.py
# Then enter your question at the prompt
```

---

## 📈 Project Timeline

| Day | Milestone |
|---|---|
| **11–12** | LangGraph foundation — `search_node` and `read_url_node` |
| **13** | Full pipeline — `summarise_node`, `synthesise_node`, conditional loop |
| **14** | Observability — LangSmith tracing, bottleneck profiling, optimization insights |
| **15** | UI & Deployment — Streamlit web app, README documentation, GitHub push |

---

## 🎓 Learning Outcomes

✅ Built a production-grade agentic AI system  
✅ Learned LangGraph for workflow orchestration  
✅ Integrated 3rd-party APIs (Groq, DuckDuckGo, LangSmith)  
✅ Profiled and identified bottlenecks  
✅ Shipped interactive web UI with Streamlit  
✅ Implemented observability with distributed tracing
