# app.py
import streamlit as st
from graph import build_graph

st.set_page_config(page_title="Agentic Supervisor Assistant", layout="wide")
st.title("🛡️ Agentic Supervisor Assistant (Local IAM Automation)")

user_input = st.text_area("Enter your IAM request:", height=100)

if "history" not in st.session_state:
    st.session_state["history"] = []

if st.button("Run Assistant"):
    workflow = build_graph()
    state = {
        "memory": {"query": user_input},
        "logs": []
    }

    st.write("▶️ Running workflow...")          # Debug info
    try:
        result = workflow.invoke(state)
        final_msg = result["memory"].get("result", "[No result]")
        logs = "\n".join(result["logs"])
        st.write("✅ Workflow completed.")
        st.write("Result:", final_msg)           # Debug: show final message

        st.session_state["history"].append((user_input, final_msg, logs))
    except Exception as e:
        st.error(f"❌ Error during workflow execution: {e}")

# Display past queries and their results
for idx, (q, r, l) in enumerate(st.session_state["history"]):
    st.markdown(f"### Query {idx+1}: {q}")
    st.success(f"Result: {r}")
    with st.expander("Agent Logs"):
        st.text(l)
