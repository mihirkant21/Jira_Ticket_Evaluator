import numpy as np
from typing import List, Dict, Any
from bedrock_client import bedrock_client

# Stage 6 - Code Retrieval Layer (Amazon Titan Embeddings)

class SemanticSearchEngine:
    def __init__(self):
        # In a real app, this vector store would be a service like Pinecone, PgVector, or OpenSearch.
        # For this hackathon scope, we'll use an in-memory numpy array for lightning fast cosine similarity.
        self.chunk_vectors = []
        self.chunk_metadata = []

    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        vec1 = np.array(v1)
        vec2 = np.array(v2)
        return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))

    def _chunk_code(self, source_code: str, file_name: str, lines_per_chunk: int = 30) -> List[Dict[str, Any]]:
        """
        Step 6a - Chunking: Splits code into ~30 line chunks.
        """
        lines = source_code.split('\n')
        chunks = []
        
        for i in range(0, len(lines), lines_per_chunk):
            chunk_lines = lines[i:i+lines_per_chunk]
            chunk_text = '\n'.join(chunk_lines)
            
            # Skip empty chunks
            if not chunk_text.strip():
                continue
                
            chunks.append({
                "file": file_name,
                "lines": f"{i+1}-{min(i+lines_per_chunk, len(lines))}",
                "code": chunk_text
            })
            
        return chunks

    def process_pr_files_and_requirements(self, pr_files_dict: Dict[str, str], requirements: List[Dict[str, Any]], external_context: List[Dict[str, Any]] = []) -> Dict[str, List[Dict[str, Any]]]:
        """
        Executes Stages 6a -> 6e.
        pr_files_dict: { "auth/token.js": "const jwt = ...", ... }
        requirements: [ { "id": 1, "statement": "...", "classification": "...", "search_hints": [...] } ]
        external_context: [ { "reference": "...", "code": "..." } ]
        """
        self.chunk_vectors = []
        self.chunk_metadata = []
        
        # Step 6c - Embedding Code Chunks (from PR Diff)
        for file_name, code in pr_files_dict.items():
            chunks = self._chunk_code(code, file_name)
            for chunk in chunks:
                vector = bedrock_client.generate_embeddings(chunk["code"])
                if vector:
                    self.chunk_vectors.append(vector)
                    self.chunk_metadata.append(chunk)

        # Include External Codebase Context (Stage 5.5 upgrade)
        for ctx in external_context:
            chunks = self._chunk_code(ctx["code"], f"EXTERNAL:{ctx['reference']}")
            for chunk in chunks:
                vector = bedrock_client.generate_embeddings(chunk["code"])
                if vector:
                    self.chunk_vectors.append(vector)
                    self.chunk_metadata.append(chunk)

        if not self.chunk_vectors:
            return {f"req_{req['id']}": [] for req in requirements}

        # Step 6d - Semantic Search + Upgrade 2: Keyword Search Hints
        retrieved_evidence = {}
        
        for req in requirements:
            # Step 6b - Embedding Requirements
            req_vector = bedrock_client.generate_embeddings(req["statement"])
            if not req_vector:
                retrieved_evidence[f"req_{req['id']}"] = []
                continue
                
            # Calculate similarities for this requirement against all code chunks
            matches = []
            for i, chunk_vec in enumerate(self.chunk_vectors):
                sim = self._cosine_similarity(req_vector, chunk_vec)
                chunk_data = self.chunk_metadata[i]
                
                # Hybrid Search: Upgrade with Keyword Hints
                hints = req.get("search_hints", [])
                keyword_bonus = 0.0
                if hints:
                    for hint in hints:
                        if hint.lower() in chunk_data["code"].lower():
                            keyword_bonus += 0.05 # Add a small boost for keyword match
                
                final_score = sim + keyword_bonus
                matches.append((final_score, chunk_data))
            
            # Sort by highest score
            matches.sort(key=lambda x: x[0], reverse=True)
            
            # Top 3 chunks
            top_chunks = [item[1] for item in matches[:3]]
            retrieved_evidence[f"req_{req['id']}"] = top_chunks
            
        # Step 6e - Output mapping
        return retrieved_evidence

semantic_search = SemanticSearchEngine()
