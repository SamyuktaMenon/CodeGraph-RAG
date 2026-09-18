import streamlit as st
import sys
import os
from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from streamlit_agraph import agraph, Node, Edge, Config

from backend.crag_workflow import build_crag_workflow

crag_app = build_crag_workflow()

st.set_page_config(page_title="CodeGraph-RAG", page_icon="🔍", layout="wide")

st.title("CodeGraph-RAG 🔍")
st.markdown("Autonomous Architectural Reasoning & Bug-Localization Engine")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "graph" in message and message["graph"]:
            nodes = [Node(id=n["id"], label=n["label"], size=25, color="#00bcd4") for n in message["graph"]["nodes"]]
            edges = [Edge(source=e["source"], target=e["target"], label=e["label"]) for e in message["graph"]["edges"]]
            config = Config(width=500, height=300, directed=True, physics=True, hierarchical=False)
            agraph(nodes=nodes, edges=edges, config=config)

# React to user input
if prompt := st.chat_input("Ask a question about the codebase..."):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Analyzing Knowledge Graph and Vector Database..."):
            try:
                response_state = crag_app.invoke({"question": prompt})
                # Extract answer and sources from the workflow state
                result = {
                    "answer": response_state.get("generation", ""),
                    "sources": response_state.get("documents", [])
                }
                
                answer = result.get("answer", "")
                sources = result.get("sources", [])
                
                st.markdown(answer)
                
                # Extract graph relationships for visualization
                graph_nodes = set()
                graph_edges = []
                
                with st.expander("View Context & Sources"):
                    for source in sources:
                        content = source.get("content", "") if isinstance(source, dict) else str(source)
                        st.text(content)
                        if "has relationship" in content:
                            parts = content.split(" has relationship ")
                            if len(parts) == 2:
                                left = parts[0].split("Graph Info: ")[-1].split(" in ")[0]
                                right_parts = parts[1].split(" with ")
                                rel = right_parts[0]
                                right = right_parts[1]
                                graph_nodes.add(left)
                                graph_nodes.add(right)
                                graph_edges.append({"source": left, "target": right, "label": rel})
                
                # Render Graph
                nodes_data = [{"id": n, "label": n} for n in graph_nodes]
                if nodes_data:
                    st.markdown("### Structural Context")
                    nodes = [Node(id=n["id"], label=n["label"], size=25, color="#00bcd4") for n in nodes_data]
                    edges = [Edge(source=e["source"], target=e["target"], label=e["label"]) for e in graph_edges]
                    config = Config(width=700, height=400, directed=True, physics=True, hierarchical=False)
                    agraph(nodes=nodes, edges=edges, config=config)
                
                # Add assistant response to chat history
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": answer,
                    "graph": {"nodes": nodes_data, "edges": graph_edges} if nodes_data else None
                })
            except Exception as e:
                st.error(f"Error executing pipeline locally: {e}")