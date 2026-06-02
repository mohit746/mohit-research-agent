from typing import TypedDict
from langgraph.graph import StateGraph, END

class AgentState(TypedDict):
    input: str
    output: str
    error: str
    search_results: list  # NEW field to hold search results
    url_contents: list # NEW field to hold URL contents


def search_node(state: AgentState) -> AgentState:
    from duckduckgo_search import DDGS
    
    query = state["input"]
    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=5):
                results.append({
                    "title": r["title"],
                    "url": r["href"],
                    "snippet": r["body"]
                })
    except Exception as e:
        return {**state, "error": f"Search failed: {e}"}
    return {**state, "search_results": results}


def read_url_node(state: AgentState) -> AgentState:
    import httpx
    import re
    
    results = state.get("search_results", [])
    contents = []
    for r in results[:2]:  # only top 2 URLs
        try:
            resp = httpx.get(r["url"], timeout=5, follow_redirects=True)
            text = re.sub(r"<[^>]+>", " ", resp.text)  # strip HTML
            text = re.sub(r"\s+", " ", text).strip()[:2000]  # clean + limit
            contents.append({"url": r["url"], "content": text})
        except Exception:
            continue  # bad URL — skip
    return {**state, "url_contents": contents}



def llm_node(state: AgentState) -> AgentState:
    from groq import Groq
    import os
    from dotenv import load_dotenv

    load_dotenv()
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    # Build context from URLs
    context = ""
    if state.get("url_contents"):
        context = "Web content found:\n"
        for item in state["url_contents"]:
            context += f"\nFrom {item['url']}:\n{item['content'][:500]}...\n"
    
    prompt = f"{context}\n\nQuestion: {state['input']}"
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    text = response.choices[0].message.content
    return {**state, "output": text}

def process_node(state: AgentState) -> AgentState:
    summary = f"[PROCESSED]: {state['output'][:200]}"
    return {**state, "output": summary}

graph = StateGraph(AgentState)
graph.add_node("search", search_node)
graph.add_node("read_url", read_url_node)
graph.add_node("llm", llm_node)
graph.add_node("process", process_node)
graph.set_entry_point("search")
graph.add_edge("search", "read_url")
graph.add_edge("read_url", "llm")
graph.add_edge("llm", "process")
graph.add_edge("process", END)
app = graph.compile()
# Test 1
result1 = app.invoke({"input": "GLP-1 drugs diabetes 2025 clinical trials", "output": "", "error": "", "search_results": [], "url_contents": []})
print("\n=== Query 1 ===")
print(result1["output"])

# Test 2
result2 = app.invoke({"input": "Stripe AI products 2025", "output": "", "error": "", "search_results": [], "url_contents": []})
print("\n=== Query 2 ===")
print(result2["output"])