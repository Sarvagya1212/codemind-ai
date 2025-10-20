import chromadb
from chromadb.config import Settings
import os

class EmbeddingService:
    def __init__(self):
        # Use persistent directory in production
        persist_dir = os.getenv('CHROMA_PERSIST_DIRECTORY', './chroma_data')
        
        self.chroma_client = chromadb.PersistentClient(
            path=persist_dir,
            settings=Settings(
                anonymized_telemetry=False
            )
        )
        
        self.collection = self.chroma_client.get_or_create_collection(
            name="code_embeddings",
            metadata={"description": "Code chunk embeddings"}
        )
    
    def create_embeddings(self, code_chunks, repo_id):
        """Generate embeddings for code chunks"""
        embeddings = []
        documents = []
        metadatas = []
        ids = []
        
        for idx, chunk in enumerate(code_chunks):
            # Generate embedding using Ollama
            response = ollama.embeddings(
                model="nomic-embed-text",
                prompt=chunk["text"]
            )
            
            embeddings.append(response["embedding"])
            documents.append(chunk["text"])
            metadatas.append({
                "repo_id": repo_id,
                "file_path": chunk["file_path"],
                "chunk_type": chunk["type"]  # function, class, module
            })
            ids.append(f"{repo_id}_{chunk['file_path']}_{idx}")
        
        # Store in ChromaDB
        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        return len(embeddings)
    
    def search_similar_code(self, query, repo_id, n_results=5):
        """Semantic search for relevant code"""
        # Generate query embedding
        query_embedding = ollama.embeddings(
            model="nomic-embed-text",
            prompt=query
        )["embedding"]
        
        # Search ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            where={"repo_id": repo_id},
            n_results=n_results
        )
        
        return results