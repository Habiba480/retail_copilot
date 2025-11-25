import os
from typing import Any, Dict, List
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # project root

from .dspy_signatures import Router, Planner, NL2SQL, Synthesizer
from .rag.retrieval import BM25Retriever
from .tools.sqlite_tool import SQLiteTool

# ---------------------------
# Initialize tools
# ---------------------------
docs_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs")
global_retriever = BM25Retriever(docs_path=docs_path, chunk_size=80)
sqlite_tool = SQLiteTool(os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "northwind.sqlite"))
synthesizer = Synthesizer()

# ---------------------------
# RAG retrieval function
# ---------------------------
def retrieve_docs(question: str, top_k: int = 3) -> List[Dict[str, Any]]:
    return global_retriever.retrieve(question, k=top_k)

# ---------------------------
# Hybrid repair loop
# ---------------------------
def repair_loop(question: str, format_hint: str = "str", max_retries: int = 2) -> dict:
    retries = 0
    final_answer = None
    last_sql = ""
    citations: List[str] = []

    while retries <= max_retries:
        # -----------------------
        # 1. Retrieve docs
        # -----------------------
        doc_results = retrieve_docs(question, top_k=3)
        doc_citations = [chunk['chunk_id'] for chunk in doc_results]

        # -----------------------
        # 2. Generate SQL
        # -----------------------
        sql_query = NL2SQL()(question)
        last_sql = sql_query

        columns, rows, error = [], [], ""
        if sql_query.strip():
            columns, rows, error = sqlite_tool.execute(sql_query)

        # -----------------------
        # 3. Synthesize answer
        # -----------------------
        if rows:
            raw_answer = rows
        else:
            raw_answer = None  # triggers default in synthesizer

        final_answer = synthesizer(raw_answer, format_hint=format_hint, citations=doc_citations)

        # Merge citations: docs + DB tables used
        table_citations = ["Orders", "Order Details", "Products", "Customers"]
        citations = doc_citations + table_citations

        # -----------------------
        # 4. Validate / retry
        # -----------------------
        if final_answer is not None:
            break
        else:
            retries += 1

    return {
        "question": question,
        "final_answer": final_answer,
        "sql": last_sql,
        "citations": citations
    }

# ---------------------------
# Batch execution from JSONL
# ---------------------------
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python -m agent.graph_hybrid sample_questions_hybrid_eval.jsonl outputs_hybrid.jsonl")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    results = []
    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            q = json.loads(line)
            result = repair_loop(q["question"], format_hint=q.get("format", "str"))
            results.append(result)

    with open(output_file, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")

    print(f"Results saved to {output_file}")
