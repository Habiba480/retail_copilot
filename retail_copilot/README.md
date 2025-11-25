

# Retail Copilot

Retail Copilot is a hybrid agent for retail analytics that combines **retrieval-augmented generation (RAG)** over company documents with **SQL execution** on a local Northwind database. The agent can answer business questions using both textual documentation and structured data.

## Project Structure
```
retail_copilot/
├─ agent/
│   ├─ graph_hybrid.py          # Main hybrid agent logic with repair loop
│   ├─ dspy_signatures.py       # Node signatures (Router, Planner, NL2SQL, Synthesizer)
│   ├─ run_agent_hybrid.py      # Interactive agent runner
│   ├─ rag/
│   │   └─ retrieval.py         # BM25-based document retriever
│   └─ tools/
│       └─ sqlite_tool.py       # SQLite helper for Northwind DB
├─ data/
│   └─ northwind.sqlite         # Sample retail database
├─ docs/
│   ├─ catalog.md
│   ├─ kpi_definitions.md
│   ├─ marketing_calendar.md
│   └─ product_policy.md
├─ sample_questions_hybrid_eval.jsonl
└─ requirements.txt
```


## Setup

1. Create a virtual environment:

```bash
conda create -n tf-metal python=3.11
conda activate tf-metal


2. Install dependencies:

```bash
pip install -r requirements.txt
```

Dependencies include:

* `rank_bm25` – BM25 document retrieval

3. Ensure `docs/` and `data/` directories are present with the required files.

## Usage

### Interactive Mode

Run the agent interactively:

```bash
python -m agent.run_agent_hybrid
```

Example:

```
Enter a question: What are the top 3 products by revenue?
```

The agent will output a JSON containing the final answer, SQL used, and citations.

### Batch Evaluation

Run multiple questions from a JSONL file:

```bash
python -m agent.graph_hybrid sample_questions_hybrid_eval.jsonl outputs_hybrid.jsonl
```

* `sample_questions_hybrid_eval.jsonl` – input questions with optional `format` hints
* `outputs_hybrid.jsonl` – generated results

Sample question format:

```json
{"question": "What are the top 3 products by revenue?", "format": "list"}
{"question": "What is the average order value for summer beverages 1997?", "format": "float"}
{"question": "What is the return policy for Beverages?", "format": "str"}
```

## How It Works

1. **RAG Retrieval**
   BM25-based retrieval over local `docs/` to find relevant text chunks.

2. **Planner & NL2SQL**
   Generates SQL queries for questions requiring structured data from the Northwind database.

3. **SQL Execution**
   Executes SQL safely using `SQLiteTool`, handling errors or empty results.

4. **Synthesizer**
   Combines RAG text results, SQL results, and citations to produce the final answer.
   Ensures non-empty output even if SQL returns no rows.

## Notes

* Always run commands from the project root (`retail_copilot`) to avoid module errors.
* Outputs are reproducible if `docs/` and `data/northwind.sqlite` are intact.
* The agent handles empty queries or missing data gracefully and provides default values per question format.

