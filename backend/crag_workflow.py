from typing import Dict, TypedDict
from langgraph.graph import StateGraph, END
from backend.retrieval import HybridRetriever
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field
from duckduckgo_search import DDGS

class GraphState(TypedDict):
    question: str
    generation: str
    documents: list
    web_fallback: bool

class GradeDocuments(BaseModel):
    """Binary score for relevance check on retrieved documents."""
    binary_score: str = Field(description="Documents are relevant to the question, 'yes' or 'no'")

def retrieve_node(state: GraphState):
    question = state["question"]
    retriever = HybridRetriever()
    documents = retriever.retrieve(question)
    return {"documents": documents, "question": question}

def grade_documents_node(state: GraphState):
    """
    Evaluates if the retrieved documents are relevant to the question.
    """
    print("---CHECK DOCUMENT RELEVANCE TO QUESTION---")
    question = state["question"]
    documents = state.get("documents", [])
    
    if not documents:
        return {"documents": [], "question": question, "web_fallback": True}

    llm = ChatOllama(model="llama3.1", temperature=0)
    structured_llm_grader = llm.with_structured_output(GradeDocuments)

    system = """You are a grader assessing relevance of a retrieved document to a user question. \n 
    It does not need to be a stringent test. The goal is to filter out erroneous retrievals. \n
    If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n
    Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question."""
    
    filtered_docs = []
    web_fallback = False
    for doc in documents:
        content = doc["content"] if isinstance(doc, dict) else str(doc)
        messages = [SystemMessage(content=system), HumanMessage(content=f"Retrieved document: \n\n {content} \n\n User question: {question}")]
        try:
            score = structured_llm_grader.invoke(messages)
            grade = score.binary_score if hasattr(score, "binary_score") else score.get("binary_score", "no")
            if grade.lower() == "yes":
                filtered_docs.append(doc)
        except Exception:
            # If grading fails, remain permissive
            filtered_docs.append(doc)
            
    if not filtered_docs:
        print("---ALL DOCUMENTS IRRELEVANT: TRIGGER WEB SEARCH---")
        web_fallback = True

    return {"documents": filtered_docs, "question": question, "web_fallback": web_fallback}

def web_search_node(state: GraphState):
    """
    Web search based on the re-phrased question.
    """
    print("---WEB SEARCH---")
    question = state["question"]
    documents = state.get("documents", [])

    try:
        results = DDGS().text(question, max_results=3)
        web_results = "\n".join([f"{d['title']}: {d['body']}" for d in results])
        documents.append({"content": f"Web Search Results:\n{web_results}", "score": 1.0})
    except Exception as e:
        print(f"Web search failed: {e}")

    return {"documents": documents, "question": question}

def generate_node(state: GraphState):
    """
    Generates the final answer using the retrieved context via local Ollama with strict grounding.
    """
    print("---GENERATE ANSWER---")
    documents = state.get("documents", [])
    
    context = "\n\n".join([doc["content"] if isinstance(doc, dict) else str(doc) for doc in documents])
    
    system_prompt = (
        "You are an expert software architect assistant.\n"
        "STRICT GROUNDING RULE: Answer the user's question about the codebase based ONLY on the provided context below.\n"
        "1. DO NOT invent, hallucinate, or write hypothetical python classes/functions.\n"
        "2. If the user asks how a class or function works (e.g., `HybridRetriever`), extract and display the EXACT verbatim code blocks found in the context.\n"
        "3. If the actual implementation code is not present in the context, explicitly reply: 'The exact source code for this component was not retrieved in the context.'"
    )
    
    try:
        llm = ChatOllama(model="llama3.1", temperature=0)
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Retrieved Codebase Context:\n{context}\n\nUser Question: {state['question']}")
        ]
        response = llm.invoke(messages)
        generation = response.content
    except Exception as e:
        generation = f"Error generating answer with Ollama (Is Ollama running and `ollama pull llama3.1` completed?): {e}"
    
    return {"documents": documents, "question": state["question"], "generation": generation}

def route_question(state: GraphState):
    """
    Route to web search or generation.
    """
    print("---ROUTE QUESTION---")
    if state.get("web_fallback"):
        print("---ROUTE QUESTION TO WEB SEARCH---")
        return "web_search"
    print("---ROUTE QUESTION TO GENERATE---")
    return "generate"

def build_crag_workflow():
    workflow = StateGraph(GraphState)
    
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("grade_documents", grade_documents_node)
    workflow.add_node("web_search", web_search_node)
    workflow.add_node("generate", generate_node)
    
    workflow.set_entry_point("retrieve")
    workflow.add_edge("retrieve", "grade_documents")
    workflow.add_conditional_edges(
        "grade_documents",
        route_question,
        {
            "web_search": "web_search",
            "generate": "generate",
        },
    )
    workflow.add_edge("web_search", "generate")
    workflow.add_edge("generate", END)
    
    return workflow.compile()

# Explicit export for app.py
app = build_crag_workflow()