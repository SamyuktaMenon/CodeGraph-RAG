from fastapi import FastAPI
from pydantic import BaseModel
from backend.crag_workflow import build_crag_workflow

app = FastAPI(title="CodeGraph-RAG API", description="API for architectural reasoning and bug localization", version="0.1.0")

@app.get("/")
def read_root():
    return {"message": "Welcome to the CodeGraph-RAG API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

class QueryRequest(BaseModel):
    question: str

@app.post("/query")
def run_query(request: QueryRequest):
    workflow = build_crag_workflow()
    initial_state = {"question": request.question}
    result = workflow.invoke(initial_state)
    
    docs = result.get("documents", [])
    formatted_docs = []
    for d in docs:
        if isinstance(d, dict):
            formatted_docs.append(d)
        else:
            formatted_docs.append({"content": str(d)})
            
    return {
        "answer": result.get("generation", "No answer generated."),
        "sources": formatted_docs
    }
