# backend/services/doc_generator.py
import ollama

class DocumentationGenerator:
    def __init__(self):
        self.llm_model = "qwen2.5-coder:7b"
    
    def generate_readme(self, repo_metadata, code_structure):
        """Generate comprehensive README"""
        prompt = f"""Generate a professional README.md for this codebase:

Repository: {repo_metadata['name']}
Description: {repo_metadata.get('description', 'No description')}
Primary Language: {repo_metadata['language']}

Code Structure:
- Total Files: {code_structure['total_files']}
- Total Functions: {code_structure['total_functions']}
- Total Classes: {code_structure['total_classes']}
- Main Modules: {', '.join(code_structure['main_modules'][:5])}

Key Entry Points:
{self._format_entry_points(code_structure['entry_points'])}

Generate a README with these sections:
1. Project Title and Description
2. Features
3. Installation
4. Quick Start
5. Project Structure
6. API Documentation
7. Contributing
8. License

Make it professional, clear, and actionable."""

        response = ollama.generate(
            model=self.llm_model,
            prompt=prompt
        )
        
        return response['response']
    
    def generate_api_docs(self, functions_data):
        """Generate API documentation from parsed functions"""
        docs = []
        
        for func in functions_data:
            prompt = f"""Document this function:

Function Name: {func['name']}
File: {func['file_path']}
Parameters: {func.get('parameters', [])}
Code:
{func['code']}

Generate documentation with:
- Brief description
- Parameters explanation
- Return value
- Usage example"""

            response = ollama.generate(
                model=self.llm_model,
                prompt=prompt
            )
            
            docs.append({
                "function": func['name'],
                "documentation": response['response']
            })
        
        return docs
    
    def generate_architecture_overview(self, dependency_graph, modules):
        """Generate high-level architecture explanation"""
        prompt = f"""Analyze this codebase architecture:

Modules: {len(modules)} total
Key Components: {', '.join([m['name'] for m in modules[:10]])}

Dependency Relationships:
{self._format_dependencies(dependency_graph)}

Generate an architecture overview explaining:
1. Main architectural pattern (MVC, microservices, etc.)
2. Core components and their responsibilities
3. Data flow between components
4. Key design decisions
5. Potential improvement areas"""

        response = ollama.generate(
            model=self.llm_model,
            prompt=prompt
        )
        
        return response['response']