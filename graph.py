from typing import TypedDict
from langgraph.graph import StateGraph, END

class AgentState(TypedDict):
    input: str
    output: str
    error: str


def llm_node(state: AgentState) -> AgentState:
    from groq import Groq
    import os
    from dotenv import load_dotenv

    load_dotenv()
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": state["input"]}]
    )
    text = response.choices[0].message.content
    return {**state, "output": text}


def process_node(state: AgentState) -> AgentState:
    summary = f"[PROCESSED]: {state['output'][:200]}"
    return {**state, "output": summary}


def error_node(state: AgentState) -> AgentState:
    return {**state, "output": f"Handled error: {state['error']}"}


def route(state: AgentState) -> str:
    if "ERROR" in state.get("output", ""):
        return "error"
    return "process"


graph = StateGraph(AgentState)
graph.add_node("llm", llm_node)
graph.add_node("process", process_node)
graph.add_node("error", error_node)
graph.set_entry_point("llm")
graph.add_conditional_edges("llm", route, {"process": "process", "error": "error"})
graph.add_edge("process", END)
graph.add_edge("error", END)
app = graph.compile()
result = app.invoke({"input": "What is RAG in AI?", "output": "", "error": ""})
# result = app.invoke({"input": "Please respond with the word ERROR in your response", "output": "", "error": ""})
# result = app.invoke({
#     "input": "Please respond with the word ERROR in your response", 
#     "output": "", 
#     "error": "API call failed due to rate limit"
# })
print(result["output"])