# EchoChamber Studio

Simulation of discursive bubbles using political comments.
Each agent responds from the perspective of its own political community.

## Project Structure

```
echochamber/
├── notebooks/              # Weekly course notebooks (added during the semester)
├── collector/              # Scripts for collecting comments from YouTube / RSS
├── data/
│   ├── raw/                # Raw collected comments (CSV or JSONL)
│   ├── cleaned/            # Cleaned and standardized corpus
│   └── bubbles/            # One JSONL file per agent after annotation
├── assets/
│   └── roles/              # Agent role cards (roles.yaml) — written by students
├── scripts/
│   ├── clean_corpus.py     # Cleans and standardizes raw data
│   └── build_vectorstore.py # Builds FAISS vector index from data/bubbles/
├── core/                   # Core infrastructure — do not modify
│   ├── agent.py            # Agent class: reads roles.yaml + retrieves from corpus
│   ├── retriever.py        # Semantic search over FAISS index
│   ├── graph.py            # LangGraph agentic debate orchestration
│   └── metrics.py          # Dissimilarity, sentiment, and visualization
├── app/
│   └── app.py              # Gradio application (built incrementally during course)
└── reports/                # Final report and ethics checklist templates
```

## Setup

```bash
git clone <your-repo-url>
cd echochamber
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # then add your API key
```

## Team
## Student 2 – Osaci Cosmin (Course 1)

### Task: LLM Summary

Implemented a basic interaction with a Large Language Model (Gemini) using Python.

### What was done:
- configured API key using `.env`
- generated a neutral summary of a public-interest text
- tested the `temperature` parameter
- saved the result as JSON

### Notebook:
notebooks/student_2_osaci_cosmin/student_02_C1.ipynb

### Output:
notebooks/student_2_osaci_cosmin/outputs/c1_student_summary.json


- **Team name:**
- **Topic / bubble theme:**
- **Members and agents:**
  - Member 1 → Agent:
  - Member 2 → Agent:
  - Member 3 → Agent:
  - Member 4 → Agent:
  - Member 5 → Agent:

## C2 — Model Selection (Student 02)

**Recommended model:** Gemini 2.5 Flash Lite  
**Fallback model:** Gemini 2.5 Flash  
**Recommended temperature:** 0.7  

**Reason:**  
Gemini 2.5 Flash Lite produces concise and consistent responses, follows instructions accurately, and performs well for structured annotation tasks. Compared to OpenRouter Free, it generates higher-quality outputs with fewer errors. It is stable across different temperatures and suitable for political text annotation.