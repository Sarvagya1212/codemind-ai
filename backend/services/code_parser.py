# backend/services/code_parser.py
from tree_sitter import Language, Parser
import tree_sitter_python
import tree_sitter_javascript

class CodeParser:
    def __init__(self):
        self.parsers = {
            'python': self._create_parser(tree_sitter_python.language()),
            'javascript': self._create_parser(tree_sitter_javascript.language())
        }
    
    def _create_parser(self, language):
        parser = Parser()
        parser.set_language(language)
        return parser
    
    def parse_file(self, file_path, language):
        """Parse code file and extract structure"""
        with open(file_path, 'rb') as f:
            code = f.read()
        
        parser = self.parsers.get(language)
        if not parser:
            return None
        
        tree = parser.parse(code)
        
        return {
            "functions": self._extract_functions(tree.root_node),
            "classes": self._extract_classes(tree.root_node),
            "imports": self._extract_imports(tree.root_node),
            "complexity": self._calculate_complexity(tree.root_node)
        }
    
    def _extract_functions(self, node):
        """Extract all function definitions"""
        functions = []
        if node.type == 'function_definition':
            name_node = node.child_by_field_name('name')
            functions.append({
                "name": name_node.text.decode(),
                "line_start": node.start_point[0],
                "line_end": node.end_point[0]
            })
        
        for child in node.children:
            functions.extend(self._extract_functions(child))
        
        return functions
    
    def _calculate_complexity(self, node):
        """Calculate cyclomatic complexity"""
        complexity = 1  # Base complexity
        
        # Add complexity for control flow statements
        control_flow = ['if_statement', 'while_statement', 'for_statement', 
                       'try_statement', 'except_clause', 'and', 'or']
        
        if node.type in control_flow:
            complexity += 1
        
        for child in node.children:
            complexity += self._calculate_complexity(child)
        
        return complexity