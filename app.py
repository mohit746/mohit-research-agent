import streamlit as st
from refined_graph_search import app

st.set_page_config(page_title="Mohit Research Agent", layout="wide")

st.title("🔍 Mohit Research Agent")
st.markdown('<h3 style="text-align: center;">Ask any question and get AI-powered research insights</h3>', unsafe_allow_html=True)

st.divider()

user_question = st.text_input("Enter your question:", placeholder="e.g., What are the latest trends in AI in 2026?")

if st.button("🚀 Submit", use_container_width=True):
    if not user_question.strip():
        st.error("Please enter a question!")
    else:
        with st.status("🔍 Researching...", expanded=True) as status:
            st.write("📊 Searching the web...")
            st.write("📖 Reading URLs...")
            st.write("✍️ Summarizing content...")
            st.write("🧠 Synthesizing answer...")

            result = app.invoke({
                "input": user_question,
                "output": "",
                "summaries": [],
                "search_iteration": 0,
                "error": "",
                "search_results": [],
                "url_contents": []
            })

            status.update(label="✅ Research Complete!", state="complete")

        st.divider()
        st.subheading("📝 Final Answer")
        st.markdown(result['output'])
