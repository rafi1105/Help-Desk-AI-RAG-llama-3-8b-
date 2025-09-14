# GreenBot: Chatbot‑Driven Assistance Platform for Students (LLM/LLaMA)

> A practical, step‑by‑step blueprint to design, build, evaluate, and deploy a student assistant using Meta LLaMA (local or cloud), Retrieval‑Augmented Generation (RAG), and modern MLOps.

---

## 0) Project Goals & Success Criteria

**Goals**
- 24/7 student Q&A (course info, schedules, deadlines, rules, advising, libraries, labs, fees)
- Personalized study help (summaries, practice problems, explanations)
- Campus services navigation (contacts, forms, locations)
- Safe, accurate, English‑only answers (lightweight setup)

**Success Metrics**
- ≥90% answer coverage on curated FAQ benchmark
- ≥80% factual accuracy (human eval) on university‑specific questions
- CSAT ≥4.2/5 from pilot students
- Response time p95 ≤2.5s (light hardware)
- Data privacy audit passed

---

## 1) System Architecture (High‑Level)

**Core Components**
1. **Frontend**: Web (Next.js/React + Tailwind) or Mobile (Flutter)
2. **Gateway/API**: FastAPI (Python)
3. **Orchestrator**: LangChain or LlamaIndex for RAG logic
4. **LLM Serving**: Ollama (CPU/GPU lightweight) or API endpoint
5. **Vector Store**: FAISS (local, RAM‑friendly)
6. **Document Ingestion**: PDF/HTML/Docx loaders + small chunks (150–200 tokens)
7. **Embeddings**: Lightweight models (e.g., `all‑MiniLM‑L6‑v2` or `e5‑small`)
8. **Cache**: SQLite + optional Redis (if available)
9. **Safety/Guardrails**: Simple regex/policy checks
10. **Storage**: SQLite or Postgres (cloud option)

**Data Flow**
User → Frontend → API → Orchestrator → (Retriever → Vector DB) → Small LLM → Safety → Response → Frontend

---

## 2) Model Choices (2GB GPU / 16GB RAM Friendly)

**Recommended**
- **Llama 3.2 1B** (works with CPU/GPU 2GB VRAM)
- **Llama 3.2 3B quantized (Q4)** if RAM allows (better answers)
- **Alternative lightweight**: Mistral‑7B Q4, Phi‑3 Mini, or GPT4All models

**Serving Options**
- **Local**: **Ollama** (`ollama run llama3.2:1b`) – CPU/GPU optimized
- **Cloud (optional)**: Free tier API like Together.ai or OpenRouter if better quality is needed

**Fine‑Tuning**
- Use **RAG only** at first; fine‑tune later with LoRA (small dataset)

---

## 3) Retrieval‑Augmented Generation (RAG) Design

**Content Sources**
- Academic calendar, course catalogs, syllabus PDFs
- Policies (exam, plagiarism, grading, fee, hostel)
- Notices, forms, FAQs, contact lists

**Ingestion Pipeline**
1. Convert: PDF → text, HTML → text
2. Clean: remove headers/footers
3. Chunk: 150–200 tokens, overlap 30–50
4. Embed: small embedding model → vectors
5. Store: FAISS (RAM‑friendly)

**Query Pipeline**
- Dense retrieval (top‑k=3)
- Context window: ~1–2k tokens
- **Citations** included in answers

**Prompt Template (English‑Only)**
```
System: You are GreenBot, a helpful university student assistant. Always provide accurate information.
If unsure, say "I am not sure" and suggest alternatives.

User question: {question}
Retrieved context (do not make up anything):
{context}

Assistant: Write a short, clear, accurate answer in English. Provide [sources] at the end.
```

---

## 4) Safety, Privacy & Compliance

- **Basic Filters**: block exam‑cheating, harmful/illegal content
- **Citation Required** for university claims
- **Light Logging**: store only minimal conversation history
- **Data Retention**: 30 days max

---

## 5) Data & Schema (SQLite Option)

**SQLite Tables**
```sql
users(id, email, role, dept, created_at)
conversations(id, user_id, started_at)
messages(id, conv_id, sender, text, created_at)
documents(id, title, source_url, updated_at)
chunks(id, doc_id, chunk_index, text, vector)
feedback(id, msg_id, rating, comment, created_at)
```

---

## 6) API Design (FastAPI example)

**Endpoints**
- `POST /chat` → chat with RAG
- `POST /ingest` → upload docs
- `POST /feedback` → thumbs up/down

---

## 7) Frontend (Lightweight)

**Web**: Simple React/Tailwind chat window
**Mobile**: Flutter optional, but keep minimal

---

## 8) Deployment Options

**Local (Best for You)**
- Use **Ollama** with small LLaMA/Mistral models
- SQLite + FAISS

**Cloud (Optional)**
- Host API on free tier (Railway, Render)
- Use managed vector DB (Pinecone free tier)

---

## 9) Evaluation & Benchmarking

- Build a **100‑question English benchmark**
- Evaluate accuracy, latency, source correctness

---

## 10) Step‑by‑Step Build Plan (MVP)

**Week 1**: Install Ollama, FastAPI, FAISS, embeddings
**Week 2**: Ingest 5 PDFs, build RAG pipeline
**Week 3**: Create simple web chat UI
**Week 4**: Add safety filters + feedback system
**Week 5**: Evaluate with 100 Qs
**Week 6**: Optimize, release MVP

---

## 11) Example Commands

**Ollama lightweight model**
```bash
ollama pull llama3.2:1b
ollama run llama3.2:1b
```

**Embeddings (MiniLM)**
```python
from sentence_transformers import SentenceTransformer
emb = SentenceTransformer('all-MiniLM-L6-v2')
v = emb.encode([text], normalize_embeddings=True)
```

**RAG Query (LangChain)**
```python
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.chains import RetrievalQA
from langchain.llms import Ollama

loader = PyPDFLoader('calendar.pdf')
docs = loader.load()
emb = HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')
vs = FAISS.from_documents(docs, emb)
llm = Ollama(model='llama3.2:1b')
qa = RetrievalQA.from_chain_type(llm=llm, retriever=vs.as_retriever())
print(qa.run('When is the midterm exam?'))
```

---

## 12) Hardware Planning

- **Your PC (2GB GPU, 16GB RAM)** → LLaMA 1B or Phi‑3 Mini with Ollama
- Expect ~2–3s response time for RAG
- Use CPU fallback if GPU is too small

---

## 13) Next Actions

1. Install **Ollama** and run `ollama run llama3.2:1b`
2. Set up **FAISS + MiniLM embeddings**
3. Ingest 2–3 university PDFs and test retrieval
4. Build a simple **React chat UI**
5. Gradually expand dataset and features

