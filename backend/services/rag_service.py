# backend/services/rag_service.py
from langchain.chains import RetrievalQA
from langchain.llms import Ollama
from langchain.embeddings import OllamaEmbeddings
from langchain.vectorstores import Chroma
from langchain.prompts import PromptTemplate

class RAGService:
    def __init__(self, chroma_client):
        self.llm = Ollama(model="qwen2.5-coder:7b")
        self.embeddings = OllamaEmbeddings(model="nomic-embed-text")
        self.vectorstore = Chroma(client=chroma_client, embedding_function=self.embeddings)
        
        # Custom prompt template
        self.prompt_template = PromptTemplate(
            template="""You are an AI assistant analyzing a codebase. Use the following code snippets to answer the question.

Code Context:
{context}

Question: {question}

Provide a clear, technical answer with code references. If the code doesn't contain the answer, say so.

Answer:""",
            input_variables=["context", "question"]
        )
    
    def answer_question(self, question, repo_id):
        """Answer question using RAG"""
        # Retrieve relevant code chunks
        retriever = self.vectorstore.as_retriever(
            search_kwargs={
                "k": 5,
                "filter": {"repo_id": repo_id}
            }
        )
        
        # Create QA chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            retriever=retriever,
            chain_type_kwargs={"prompt": self.prompt_template}
        )
        
        # Get answer
        result = qa_chain({"query": question})
        
        # Extract source references
        sources = self._extract_sources(result["source_documents"])
        
        return {
            "answer": result["result"],
            "sources": sources,
            "confidence": self._calculate_confidence(result)
        }
    
    def _extract_sources(self, documents):
        """Extract file paths and line numbers from sources"""
        sources = []
        for doc in documents:
            sources.append({
                "file_path": doc.metadata["file_path"],
                "chunk_type": doc.metadata["chunk_type"],
                "excerpt": doc.page_content[:200] + "..."
            })
        return sources