# backend/services/language_detector.py
LANGUAGE_EXTENSIONS = {
    '.py': 'python',
    '.js': 'javascript',
    '.ts': 'typescript',
    '.java': 'java',
    '.go': 'go',
    '.rb': 'ruby',
    '.php': 'php',
    '.rs': 'rust'
}

class MultiLanguageParser:
    def __init__(self):
        self.parsers = {
            'python': self._setup_python_parser(),
            'javascript': self._setup_javascript_parser(),
            'typescript': self._setup_typescript_parser(),
            'java': self._setup_java_parser(),
            'go': self._setup_go_parser()
        }
    
    def parse_file(self, file_path):
        """Parse file in any supported language"""
        language = self._detect_language(file_path)
        
        if language not in self.parsers:
            return None
        
        parser = self.parsers[language]
        return self._parse_with_parser(file_path, parser, language)
    
    def _detect_language(self, file_path):
        """Detect programming language from file extension"""
        ext = os.path.splitext(file_path)[1]
        return LANGUAGE_EXTENSIONS.get(ext)
    
    def _setup_python_parser(self):
        """Setup Tree-sitter parser for Python"""
        import tree_sitter_python
        parser = Parser()
        parser.set_language(tree_sitter_python.language())
        return parser
    
    def _setup_javascript_parser(self):
        """Setup Tree-sitter parser for JavaScript"""
        import tree_sitter_javascript
        parser = Parser()
        parser.set_language(tree_sitter_javascript.language())
        return parser
    
    def _parse_with_parser(self, file_path, parser, language):
        """Parse file and extract language-agnostic structure"""
        with open(file_path, 'rb') as f:
            code = f.read()
        
        tree = parser.parse(code)
        
        return {
            "language": language,
            "functions": self._extract_functions_generic(tree.root_node, language),
            "classes": self._extract_classes_generic(tree.root_node, language),
            "imports": self._extract_imports_generic(tree.root_node, language),
            "complexity": self._calculate_complexity(tree.root_node)
        }
    
    def _extract_functions_generic(self, node, language):
        """Extract functions across different languages"""
        function_types = {
            'python': 'function_definition',
            'javascript': 'function_declaration',
            'typescript': 'function_declaration',
            'java': 'method_declaration',
            'go': 'function_declaration'
        }
        
        target_type = function_types.get(language)
        functions = []
        
        for child in node.children:
            if child.type == target_type:
                name = self._get_function_name(child, language)
                functions.append({
                    "name": name,
                    "line_start": child.start_point[0],
                    "line_end": child.end_point[0],
                    "language": language
                })
            
            functions.extend(self._extract_functions_generic(child, language))
        
        return functions