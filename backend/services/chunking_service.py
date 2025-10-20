# backend/services/chunking_service.py
class CodeChunker:
    def __init__(self, max_tokens=1000, overlap=200):
        self.max_tokens = max_tokens
        self.overlap = overlap
    
    def chunk_file(self, file_path, parsed_data):
        """Split code file into semantic chunks"""
        chunks = []
        
        with open(file_path, 'r') as f:
            code = f.read()
        
        # Strategy 1: Function-level chunks
        for function in parsed_data["functions"]:
            chunk_text = self._extract_lines(
                code, 
                function["line_start"], 
                function["line_end"]
            )
            
            chunks.append({
                "text": chunk_text,
                "type": "function",
                "name": function["name"],
                "file_path": file_path,
                "lines": (function["line_start"], function["line_end"])
            })
        
        # Strategy 2: Class-level chunks
        for cls in parsed_data["classes"]:
            chunk_text = self._extract_lines(
                code,
                cls["line_start"],
                cls["line_end"]
            )
            
            chunks.append({
                "text": chunk_text,
                "type": "class",
                "name": cls["name"],
                "file_path": file_path,
                "lines": (cls["line_start"], cls["line_end"])
            })
        
        return chunks
    
    def _extract_lines(self, code, start, end):
        """Extract specific line range from code"""
        lines = code.split('\n')
        return '\n'.join(lines[start:end+1])