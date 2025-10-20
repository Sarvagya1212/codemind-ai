# backend/services/incremental_updater.py
class IncrementalUpdater:
    def __init__(self, repo_id):
        self.repo_id = repo_id
        self.embedding_service = EmbeddingService()
    
    async def update_changed_files(self, changed_files):
        """Update only changed files instead of full re-analysis"""
        for file_path in changed_files:
            # Re-parse file
            parser = CodeParser()
            parsed_data = parser.parse_file(file_path, detect_language(file_path))
            
            # Update database
            update_file_in_db(self.repo_id, file_path, parsed_data)
            
            # Re-generate embeddings
            chunker = CodeChunker()
            chunks = chunker.chunk_file(file_path, parsed_data)
            
            # Delete old embeddings
            self.embedding_service.delete_embeddings(self.repo_id, file_path)
            
            # Create new embeddings
            self.embedding_service.create_embeddings(chunks, self.repo_id)
        
        # Update affected documentation
        await self.update_documentation(changed_files)
    
    async def update_documentation(self, changed_files):
        """Regenerate documentation for affected modules"""
        doc_gen = DocumentationGenerator()
        
        # Determine which docs need updating
        affected_modules = self._find_affected_modules(changed_files)
        
        for module in affected_modules:
            # Regenerate module documentation
            new_docs = doc_gen.generate_module_docs(module)
            update_docs_in_db(self.repo_id, module, new_docs)