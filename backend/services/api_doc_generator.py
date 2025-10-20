# backend/services/api_doc_generator.py
class APIDocGenerator:
    def __init__(self):
        self.llm_model = "qwen2.5-coder:7b"
    
    def generate_api_documentation(self, repo_id):
        """Generate comprehensive API documentation"""
        # Extract all public APIs
        functions = get_public_functions(repo_id)
        classes = get_public_classes(repo_id)
        
        # Group by module
        modules = self._group_by_module(functions + classes)
        
        api_docs = {
            "title": f"API Documentation",
            "modules": []
        }
        
        for module_name, items in modules.items():
            module_doc = {
                "name": module_name,
                "description": self._generate_module_description(items),
                "endpoints": []
            }
            
            for item in items:
                endpoint_doc = self._generate_endpoint_doc(item)
                module_doc["endpoints"].append(endpoint_doc)
            
            api_docs["modules"].append(module_doc)
        
        return api_docs
    
    def _generate_endpoint_doc(self, item):
        """Generate detailed documentation for API endpoint"""
        prompt = f"""Generate API documentation for this function:

Name: {item['name']}
Parameters: {item['parameters']}
Return Type: {item.get('return_type', 'Unknown')}
Source Code:
{item['code']}

Generate documentation in this format:

## {item['name']}

**Description:** [Brief description of what this function does]

**Parameters:**
- param1 (type): Description
- param2 (type): Description

**Returns:**
- return_type: Description of return value

**Example Usage:**
```python
# Example code
```

**Errors:**
- List potential errors/exceptions
"""

        response = ollama.generate(
            model=self.llm_model,
            prompt=prompt
        )
        
        return {
            "name": item['name'],
            "documentation": response['response'],
            "file": item['file_path'],
            "line": item['line_number']
        }
    
    def export_to_markdown(self, api_docs):
        """Export API documentation to Markdown format"""
        md = f"# {api_docs['title']}\n\n"
        
        for module in api_docs['modules']:
            md += f"## Module: {module['name']}\n\n"
            md += f"{module['description']}\n\n"
            
            for endpoint in module['endpoints']:
                md += endpoint['documentation'] + "\n\n---\n\n"
        
        return md
    
    def export_to_html(self, api_docs):
        """Export API documentation to HTML format"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{api_docs['title']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
        pre {{ background: #f5f5f5; padding: 15px; border-radius: 5px; }}
        code {{ background: #f0f0f0; padding: 2px 5px; border-radius: 3px; }}
    </style>
</head>
<body>
    <h1>{api_docs['title']}</h1>
"""
        
        for module in api_docs['modules']:
            html += f"<h2>{module['name']}</h2>"
            html += f"<p>{module['description']}</p>"
            
            for endpoint in module['endpoints']:
                # Convert markdown to HTML (simplified)
                html += f"<div class='endpoint'>{self._md_to_html(endpoint['documentation'])}</div>"
        
        html += "</body></html>"
        return html  