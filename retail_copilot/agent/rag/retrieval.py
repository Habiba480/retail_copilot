import os
from typing import List, Dict, Any
from rank_bm25 import BM25Okapi


class DocumentChunk:
    """
    Holds a single chunk of text along with metadata needed for retrieval
    and later citations.
    """

    def __init__(self, chunk_id: str, source: str, text: str):
        self.chunk_id = chunk_id          # e.g., "marketing_calendar::chunk0"
        self.source = source              # filename, useful for citations
        self.text = text                  # the actual text content
        self.tokens = text.lower().split()  # simple tokenization


class BM25Retriever:
    """
    Simple BM25-based retriever over the local docs/ directory.
    Designed to stay lightweight and offline.
    """

    def __init__(self, docs_path: str, chunk_size: int = 80):
        self.docs_path = docs_path
        self.chunk_size = chunk_size
        self.chunks: List[DocumentChunk] = []

        # Build index at initialization
        self._load_documents()
        self._build_index()

    # --------------------------------------------
    # LOADING DOCUMENTS + CHUNKING
    # --------------------------------------------
    def _load_documents(self):
        """
        Read all .md documents in the docs folder
        and split them into fixed-size chunks.
        """
        for filename in os.listdir(self.docs_path):
            if not filename.endswith(".md"):
                continue

            full_path = os.path.join(self.docs_path, filename)
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Basic splitting: paragraph-by-paragraph
            paragraphs = [p.strip() for p in content.split("\n") if p.strip()]

            # Convert paragraphs into chunked windows
            chunk_counter = 0
            for para in paragraphs:
                # Long paragraphs may be split further based on token count
                tokens = para.split()
                for i in range(0, len(tokens), self.chunk_size):
                    window = tokens[i : i + self.chunk_size]
                    text_chunk = " ".join(window)

                    chunk_id = f"{filename.replace('.md','')}::chunk{chunk_counter}"
                    self.chunks.append(DocumentChunk(chunk_id, filename, text_chunk))
                    chunk_counter += 1

    # --------------------------------------------
    # BUILD BM25 INDEX
    # --------------------------------------------
    def _build_index(self):
        """
        Build the BM25 index using the tokenized text from each chunk.
        """
        corpus = [chunk.tokens for chunk in self.chunks]
        self.bm25 = BM25Okapi(corpus)

    # --------------------------------------------
    # RETRIEVAL FUNCTION
    # --------------------------------------------
    def retrieve(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Return the top-k most relevant document chunks for a given query.

        Output format (per chunk):
        {
            "chunk_id": "...",
            "source": "filename.md",
            "text": "...",
            "score": <float>
        }
        """
        tokens = query.lower().split()
        scores = self.bm25.get_scores(tokens)

        # Sort chunk indices by score
        top_indices = sorted(
            range(len(scores)), key=lambda i: scores[i], reverse=True
        )[:k]

        results = []
        for idx in top_indices:
            chunk = self.chunks[idx]
            results.append({
                "chunk_id": chunk.chunk_id,
                "source": chunk.source,
                "text": chunk.text,
                "score": float(scores[idx]),
            })

        return results
# Initialize a global retriever (only once)
global_retriever = BM25Retriever(docs_path="docs", chunk_size=80)

def retrieve_docs(query: str, top_k: int = 3) -> list[dict]:
    """
    Wrapper function to return top-k BM25 results for a query.
    Returns list of dicts with chunk_id, source, text, score.
    """
    return global_retriever.retrieve(query, k=top_k)
