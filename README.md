# 🛡️ Samsung Fire & Marine Insurance AI Assistant

An AI-powered insurance consultation system built for Samsung Fire & Marine Insurance.
This multi-agent RAG system provides personalized insurance Q&A, claim guidance, and complaint management.

---

## 🚀 Live Demo

🔗 [Launch App]([https://your-app.streamlit.app](https://225insuranceagenteng-zzak2847fvyx7n2hixgzbk.streamlit.app/))

### Test Accounts
| Role | ID | Password |
|------|----|----------|
| Customer | CUST-0001 ~ CUST-0050 | 1234 |
| Admin | admin | 1234 |

---

## ✨ Key Features

### 👤 Customer Mode
- **Policy Q&A** — Ask about your coverage, riders, and policy details based on actual insurance documents
- **Personalized Answers** — Responses tailored to each customer's enrolled products and riders
- **Multi-product Support** — Handles Auto, Cancer, and Dental insurance simultaneously
- **File a Claim** — Step-by-step claim guidance with document checklist
- **Document Upload** — AI-powered document classification using Gemini Vision
- **Context Continuity** — Maintains conversation history for natural follow-up questions

### 🔐 Admin Mode
- **Overview Dashboard** — Real-time stats on total chats, complaints, handoffs, and claims
- **Conversation Log** — Full audit trail with intent/domain filtering and CSV export
- **Complaint Management** — Sentiment-scored complaint tracking
- **Handoff Status** — Monitor cases escalated to human agents
- **Customer Overview** — Enrollment statistics by product

---

## 🤖 AI Agent Architecture

```
User Query
    │
    ▼
Intent Router (Gemini 2.5 Flash)
    │
    ├── policy_inquiry      → Customer DB lookup
    ├── coverage_inquiry    → RAG Agent (Vector DB search)
    ├── non_enrolled_inquiry→ RAG Agent + enrollment guidance
    ├── claim               → RAG Agent + Claim Agent
    ├── general_inquiry     → RAG Agent
    └── out_of_scope        → Redirect message
    │
    ▼
RAG Agent
    ├── Query translation (EN → KR for vector search)
    ├── Per-rider individual search
    ├── Precedent/dispute case search
    └── LLM answer generation (English)
    │
    ▼
Complaint Agent (runs on every response)
    ├── Sentiment scoring
    ├── Complaint detection & logging
    └── Human Handoff (if score ≤ 3 or legal keywords detected)
```

---

## 🗂️ Insurance Coverage

| Product | Domain | Description |
|---------|--------|-------------|
| Auto Insurance | `auto` | Accident coverage, riders for rental, legal fees, etc. |
| Cancer Insurance | `cancer` | Cancer diagnosis, treatment, hospitalization benefits |
| Dental Insurance | `teeth` | Implants, crowns, nerve treatments, prosthetics |

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| LLM | Gemini 2.5 Flash |
| Embeddings | BAAI/bge-m3 |
| Vector DB | ChromaDB (MMR retrieval) |
| UI | Streamlit |
| Image Analysis | Gemini Vision |
| Language | Python 3.12 |

---

## 📁 Project Structure

```
insurance_agent/
├── app.py                    # Main Streamlit dashboard
├── customers.csv             # Customer database (50 customers)
├── requirements.txt
├── agents/
│   ├── customer_agent.py     # Customer DB lookup & login
│   ├── rag_agent.py          # Vector search + LLM answer generation
│   ├── claim_agent.py        # Document validation & claim processing
│   └── complaint_agent.py    # Complaint detection & human handoff
├── utils/
│   └── llm_setup.py          # LLM, embeddings, vector DB initialization
├── insurance_chroma_db_last/ # Auto insurance vector DB
├── cancer_chroma_db_last/    # Cancer insurance vector DB
├── teeth_chroma_db_last/     # Dental insurance vector DB
└── precedent_chroma_db/      # Legal precedents vector DB
```

---

## ⚙️ Setup (Local)

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set up environment variables
Create a `.env` file in the project root:
```
GOOGLE_API_KEY=your_google_api_key_here
```

### 3. Run the app
```bash
streamlit run app.py
```

---

## 🔐 Environment Variables

| Variable | Description |
|----------|-------------|
| `GOOGLE_API_KEY` | Google AI Studio API key (Gemini) |

For Streamlit Cloud deployment, add this in **Settings → Secrets**.

---

## 📊 How It Works

1. Customer logs in with their ID and password
2. The intent router classifies the question into one of 6 categories
3. The RAG agent searches the relevant insurance policy vector DB
4. Queries are automatically translated to Korean for accurate document retrieval
5. Gemini generates a personalized English response based on retrieved policy chunks
6. Every response is analyzed for complaints and logged to the audit trail
7. If strong dissatisfaction or legal keywords are detected, the case is escalated to a human agent

---

## 📝 License

This project was developed for the **Samsung Fire & Marine Insurance AI Competition**.
