# CodeGraph-RAG 🔍

An autonomous, fully offline architectural reasoning and bug-localization engine. CodeGraph-RAG combines Abstract Syntax Tree (AST) code parsing, vector search, and Knowledge Graph representations to perform strictly grounded codebase analysis using local LLM inference.

---

## 🛠️ Key Features

* **Strict Code Grounding**: Eliminates LLM code hallucination by retrieving verbatim function and class AST source segments.
* **100% Free & Offline**: Uses local Llama 3.1 inference via Ollama and SentenceTransformers embeddings—no external paid APIs required.
* **AST-Driven Ingestion**: Custom Python AST parser extracts class definitions, function bodies, docstrings, and call-graph relationships (`CALLS`, `BELONGS_TO`).
* **Corrective RAG Workflow**: Implements a self-grading RAG loop using LangGraph that evaluates document relevance and routes queries to web search fallback when necessary.
* **Interactive Frontend**: Built with Streamlit to display conversational answers alongside retrieved context blocks and graph visualizations.

---

## 🏗️ Architecture Stack

* **Orchestration**: LangGraph, LangChain
* **Vector Store**: ChromaDB (`all-MiniLM-L6-v2` embeddings)
* **Knowledge Graph**: Neo4j
* **Local Inference**: Ollama (`llama3.1`)
* **Frontend**: Streamlit, `streamlit-agraph`

---

## 🚀 Getting Started

### 1. Prerequisites

Make sure the following are installed:

- Python 3.10+
- Git
- Docker Desktop
- Ollama

### 2. Clone the Repository

```bash
git clone https://github.com/SamyuktaMenon/CodeGraph-RAG.git
cd CodeGraph-RAG
```

### 3. Create a Virtual Environment

#### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Pull the Local LLM

CodeGraph-RAG uses Llama 3.1 through Ollama.

```bash
ollama pull llama3.1
```

Verify the model is installed:

```bash
ollama list
```

### 6. Start Neo4j

Start the Neo4j knowledge graph database using Docker Compose:

```bash
docker-compose up -d
```

Verify that the container is running:

```bash
docker ps
```

### 7. Ingest the Codebase

Run the ingestion pipeline to parse the codebase and populate ChromaDB and Neo4j:

```bash
python ingest.py
```

### 8. Launch the Application

Start the Streamlit frontend:

```bash
streamlit run frontend/app.py --server.port 8502
```

Open the application in your browser:

```text
http://localhost:8502
```
