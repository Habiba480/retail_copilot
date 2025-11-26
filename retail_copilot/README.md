

```
README.md
```



# **Retail Analytics Copilot – Hybrid RAG + SQL Agent**

This project implements an **analytics copilot** capable of answering both **RAG (document-based)** and **SQL (database-based)** questions. The system follows a hybrid architecture using **BM25 retrieval**, **SQLite**, **DSPy signatures**, and a **LangGraph-based agent pipeline**.

The copilot is able to:

* Query a SQLite Northwind dataset using automatically generated SQL
* Retrieve company policy, catalog, KPI definitions, and marketing calendar information from internal markdown docs
* Combine RAG + SQL signals into a unified hybrid answer
* Produce structured answers with citations and confidence scores
* Run in batch mode over evaluation files

All logic follows the exact specifications required in the assignment.

---

## **1. Project Structure**

```
retail_copilot/
│
├── agent/
│   ├── graph_hybrid.py          # Full hybrid agent pipeline
│   ├── rag/
│   │   ├── retrieval.py         # BM25 document retriever
│   │   └── __init__.py
│   ├── sql/
│   │   ├── sqlite_tool.py       # SQLite access and safe execution
│   │   └── __init__.py
│   ├── signatures.py            # DSPy signatures (Planner, Router, NL→SQL, Synthesizer)
│   ├── utils.py                 # Shared helper methods
│   └── __init__.py
│
├── docs/                        # Internal company markdown documents
│   ├── marketing_calendar.md
│   ├── kpi_definitions.md
│   ├── catalog.md
│   └── product_policy.md
│
├── data/
│   └── northwind.sqlite         # Database after creating views
│
├── sample_questions_hybrid_eval.jsonl
├── outputs_hybrid.jsonl
│
├── run_agent_hybrid.py          # Batch evaluation script
└── README.md
```

---

## **2. Environment Setup**

### **Step 1 — Create Python environment**

```bash
conda create -n retail_copilot python=3.11 -y
conda activate retail_copilot
```

### **Step 2 — Install dependencies**

```
pip install -r requirements.txt
```

### **Step 3 — Download the database**

```bash
mkdir -p data
curl -L -o data/northwind.sqlite \
https://raw.githubusercontent.com/jpwhite3/northwind-SQLite3/main/dist/northwind.db
```

### **Step 4 — Create required SQL views**

```bash
sqlite3 data/northwind.sqlite <<'SQL'
CREATE VIEW IF NOT EXISTS orders AS SELECT * FROM Orders;
CREATE VIEW IF NOT EXISTS order_items AS SELECT * FROM "Order Details";
CREATE VIEW IF NOT EXISTS products AS SELECT * FROM Products;
CREATE VIEW IF NOT EXISTS customers AS SELECT * FROM Customers;
SQL
```

---

## **3. Running the Hybrid Agent**

To run the full system on the evaluation batch:

```bash
python run_agent_hybrid.py --batch sample_questions_hybrid_eval.jsonl \
                           --out outputs_hybrid.jsonl
```

This will:

* Load the SQLite database
* Load and index the markdown documents
* Initialize the hybrid agent (router → planner → SQL → RAG → synthesizer)
* Produce output for each evaluation question
* Save everything into `outputs_hybrid.jsonl`

You should see:

```
Wrote 6 outputs to outputs_hybrid.jsonl
```

---

## **4. Output Format**

Each output contains:

```json
{
  "id": "hybrid_aov_winter_1997",
  "final_answer": 125.54,
  "sql": "SELECT ...",
  "confidence": 0.92,
  "explanation": "Computed using SQL and KPI definitions.",
  "citations": [
    "Orders",
    "Order Details",
    "kpi_definitions::chunk1",
    "marketing_calendar::chunk3"
  ]
}
```

* **final_answer** → the final hybrid answer
* **sql** → SQL query used (if any)
* **citations** → doc chunks + tables used
* **confidence** → model-based confidence score
* **explanation** → short deterministic explanation

---

## **5. Document Retrieval (RAG)**

The RAG system uses:

* **BM25Okapi** for efficient offline ranking
* Markdown files split into ~80-token chunks
* Retrieval returns chunk text + scores + citations

Located in:

```
agent/rag/retrieval.py
```

---

## **6. SQL Query Execution**

All SQL is executed through a safe wrapper:

```
agent/sql/sqlite_tool.py
```

The tool:

* Validates SQL
* Runs the query
* Converts rows to Python dicts
* Handles empty results
* Prevents injections
* Returns errors in a structured format

---

## **7. DSPy Signatures**

Located in:

```
agent/signatures.py
```

This includes:

* Router signature
* Planner signature
* Natural-language → SQL signature
* Synthesizer signature

These signatures declare the model IO shape without describing implementation.

---

## **8. Hybrid Agent Logic**

The main pipeline lives at:

```
agent/graph_hybrid.py
```

This file contains:

* Router
* Semantic RAG
* SQL executor
* Hybrid synthesizer
* Conflict resolution
* Confidence scoring
* Citation merging

All logic follows the project requirements exactly.

---

## **9. Submitting the Project (as required in the PDF)**

Your submission must include:

### **Files to upload**

✔ Entire `retail_copilot/` project folder
✔ `requirements.txt`
✔ `README.md` (this file)
✔ `outputs_hybrid.jsonl` (generated output)
✔ The evaluation script `run_agent_hybrid.py`
✔ All markdown documents in `/docs`
✔ SQLite DB in `/data`

### **Format**

* Submit as a **GitHub repository** *or* a **single zip file**
* Must run with:

```bash
pip install -r requirements.txt
python run_agent_hybrid.py --batch sample_questions_hybrid_eval.jsonl --out outputs.jsonl
```

No extra setup should be required beyond installing dependencies and placing the DB.

---

## **10. Contact & Notes**

This implementation was built to satisfy:

* Hybrid RAG + SQL agent architecture
* Deterministic evaluation pipeline
* Clear explanations + citations
* Offline operation (no external APIs required)
* Fully reproducible results

