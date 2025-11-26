import os
from typing import List, Dict, Any
from rank_bm25 import BM25Okapi


class DocumentChunk:
    def __init__(self, chunk_id: str, source: str, text: str):
        self.chunk_id = chunk_id
        self.source = source
        self.text = text
        self.tokens = text.lower().split()


class BM25Retriever:
    """
    BM25 retriever over docs/ directory. Builds chunks of each md file.
    """

    def __init__(self, docs_path: str, chunk_size: int = 80):
        self.docs_path = docs_path
        self.chunk_size = chunk_size
        self.chunks: List[DocumentChunk] = []
        self._load_documents()
        self._build_index()

    def _load_documents(self):
        for filename in sorted(os.listdir(self.docs_path)):
            if not filename.endswith(".md"):
                continue
            full_path = os.path.join(self.docs_path, filename)
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
            paragraphs = [p.strip() for p in content.split("\n") if p.strip()]
            chunk_counter = 0
            for para in paragraphs:
                tokens = para.split()
                for i in range(0, len(tokens), self.chunk_size):
                    window = tokens[i : i + self.chunk_size]
                    text_chunk = " ".join(window)
                    chunk_id = f"{filename.replace('.md','')}::chunk{chunk_counter}"
                    self.chunks.append(DocumentChunk(chunk_id, filename, text_chunk))
                    chunk_counter += 1

    def _build_index(self):
        corpus = [chunk.tokens for chunk in self.chunks]
        if len(corpus) == 0:
            self.bm25 = None
        else:
            self.bm25 = BM25Okapi(corpus)

    def retrieve(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        if not self.bm25:
            return []
        tokens = query.lower().split()
        scores = self.bm25.get_scores(tokens)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
        results = []
        for idx in top_indices:
            chunk = self.chunks[idx]
            results.append({
                "chunk_id": chunk.chunk_id,
                "source": chunk.source,
                "text": chunk.text,
                "score": float(scores[idx])
            })
        return results
