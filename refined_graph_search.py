from typing import TypedDict
from langgraph.graph import StateGraph, END

class AgentState(TypedDict):
    input: str
    output: str
    error: str
    search_results: list  
    url_contents: list
    summaries: list
    search_iteration: int


def search_node(state: AgentState) -> AgentState:
    from ddgs import DDGS

    iteration = state.get("search_iteration", 0) + 1
    print(f"\n[search_node] Iteration {iteration} — searching: '{state['input']}'")
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
        print(f"[search_node] ERROR: {e}")
        return {**state, "error": f"Search failed: {e}"}
    print(f"[search_node] Got {len(results)} results")
    return {**state, "search_results": results, "search_iteration": iteration}


def summarise_node(state: AgentState) -> AgentState:
    from groq import Groq
    import os
    from dotenv import load_dotenv

    load_dotenv()
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    result_list = []
    print(f"\n[summarise_node] Summarising {len(state.get('url_contents', []))} sources")
    if state.get("url_contents", []):
        for item in state["url_contents"]:
            print(f"[summarise_node] Calling LLM for {item['url'][:60]}")
            prompt = f"Summarise in 3 bullet points what this says about '{state['input']}':\n{item['content'][:500]}"
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            text = response.choices[0].message.content
            result_list.append({"url": item["url"], "summary": text})

    print(f"[summarise_node] Done — {len(result_list)} summaries ready")
    return {**state, "summaries": result_list}


def synthesise_node(state: AgentState) -> AgentState:
    from groq import Groq
    import os
    from dotenv import load_dotenv

    load_dotenv()
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    print(f"\n[synthesise_node] Synthesising {len(state.get('summaries', []))} summaries into final answer")
    context = "Search results:\n"
    if state.get("summaries"):
        for item in state["summaries"]:
            context += f"\nFrom {item['url']}:\n{item['summary']}\n"

    prompt = f"{context}\n\nQuestion: {state['input']}"

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    text = response.choices[0].message.content
    print(f"[synthesise_node] Done — final answer ready")
    return {**state, "output": text}


def should_search_more(state: AgentState) -> str:
    sources = len(state.get("url_contents", []))
    iterations = state.get("search_iteration", 0)
    print(f"\n[should_search_more] sources={sources}, iteration={iterations}")
    if sources < 4 and iterations < 4:
        print(f"[should_search_more] → looping back to search")
        return "search"
    print(f"[should_search_more] → enough sources, moving to summarise")
    return "summarise"


def read_url_node(state: AgentState) -> AgentState:
    import httpx
    import re

    print(f"\n[read_url_node] Fetching top {min(3, len(state.get('search_results', [])))} URLs")
    results = state.get("search_results", [])
    contents = []
    for r in results[:3]:
        try:
            resp = httpx.get(r["url"], timeout=5, follow_redirects=True,
                             headers={"User-Agent": "Mozilla/5.0"})
            text = re.sub(r"<[^>]+>", " ", resp.text)
            text = re.sub(r"\s+", " ", text).strip()[:2000]
            contents.append({"url": r["url"], "content": text})
            print(f"[read_url_node] ✓ fetched {r['url'][:60]}")
        except Exception as e:
            print(f"[read_url_node] ✗ skipped {r['url'][:60]} — {e}")
            continue
    print(f"[read_url_node] {len(contents)} URLs successfully fetched")
    return {**state, "url_contents": contents}


graph = StateGraph(AgentState)
graph.add_node("search", search_node)
graph.add_node("summarise", summarise_node)
graph.add_node("synthesise", synthesise_node)
graph.add_node("read_url", read_url_node)
graph.set_entry_point("search")
graph.add_conditional_edges("read_url", should_search_more, {"search": "search", "summarise": "summarise"})
graph.add_edge("search", "read_url")
graph.add_edge("summarise", "synthesise")
graph.add_edge("synthesise", END)
app = graph.compile()
# Test 1
result1 = app.invoke({"input": "How cobenfy is performing on patiences with oHCM", "output": "", "summaries":[], "search_iteration": 0, "error": "", "search_results": [], "url_contents": []})
print(result1["output"])