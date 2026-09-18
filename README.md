# CodeGraph-RAG 🔍

An autonomous, fully offline architectural reasoning and bug-localization engine. CodeGraph-RAG combines Abstract Syntax Tree (AST) code parsing, vector search, and Knowledge Graph representations to perform strictly grounded codebase analysis using local LLM inference.

---

## 🛠️ Key Features

* **Strict Code Grounding**: Eliminates LLM code hallucination by retrieving verbatim function and class AST source segments.
* **100% Free & Offline**: Uses local Llama 3.1 inference via Ollama and SentenceTransformers embeddings—no external paid APIs required[cite: 18].
* **AST-Driven Ingestion**: Custom Python AST parser extracts class definitions, function bodies, docstrings, and call-graph relationships (`CALLS`, `BELONGS_TO`)[cite: 19].
* **Corrective RAG Workflow**: Implements a self-grading RAG loop using LangGraph that evaluates document relevance and routes queries to web search fallback when necessary[cite: 15].
* **Interactive Frontend**: Built with Streamlit to display conversational answers alongside retrieved context blocks and graph visualizations[cite: 18, 20].

---

## 🏗️ Architecture Stack

* **Orchestration**: LangGraph, LangChain[cite: 10, 15]
* **Vector Store**: ChromaDB (`all-MiniLM-L6-v2` embeddings)
* **Knowledge Graph**: Neo4j[cite: 19]
* **Local Inference**: Ollama (`llama3.1`)[cite: 15, 18]
* **Frontend**: Streamlit, `streamlit-agraph`[cite: 18, 20]

---

## 🚀 Getting Started

### 1. Prerequisites

* Python 3.10+
* Docker Desktop (for Neo4j)
* Ollama installed locally

### 2. Installation & Setup

Clone the repository and set up your virtual environment:

```bash
git clone [https://github.com/your-username/CodeGraph-RAG.git](https://github.com/your-username/CodeGraph-RAG.git)
cd CodeGraph-RAG

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

## 🚀 Getting Started

### 1. Pull the Local LLM
Pull the local Llama 3.1 model using Ollama:

```bash
ollama pull llama3.1

### 2. Run Knowledge Graph Infrastructure
Start the local Neo4j graph database instance using Docker Compose:

```bash
docker-compose up -d

### 3. Codebase Ingestion
Run the ingestion pipeline to parse the codebase into ChromaDB and Neo4j:
```bash
python ingest.py

### 4. Launch the Application
Start the Streamlit interface:
```bash
streamlit run frontend/app.py

Open http://localhost:8502 in your browser