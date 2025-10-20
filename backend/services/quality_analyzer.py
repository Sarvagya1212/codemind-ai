# backend/services/quality_analyzer.py
import ast
from radon.complexity import cc_visit
from radon.metrics import mi_visit

class QualityAnalyzer:
    def analyze_file(self, file_path):
        """Run comprehensive quality checks"""
        with open(file_path, 'r') as f:
            code = f.read()
        
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return {"error": "Syntax error in file"}
        
        return {
            "complexity": self._calculate_complexity(code),
            "maintainability": self._calculate_maintainability(code),
            "code_smells": self._detect_code_smells(tree, code),
            "security_issues": self._check_security(tree),
            "style_violations": self._check_style(code)
        }
    
    def _calculate_complexity(self, code):
        """Calculate cyclomatic complexity"""
        complexity_scores = cc_visit(code)
        
        return {
            "average": sum(c.complexity for c in complexity_scores) / len(complexity_scores) if complexity_scores else 0,
            "max": max(c.complexity for c in complexity_scores) if complexity_scores else 0,
            "high_complexity_functions": [
                {"name": c.name, "complexity": c.complexity, "line": c.lineno}
                for c in complexity_scores if c.complexity > 10
            ]
        }
    
    def _calculate_maintainability(self, code):
        """Calculate maintainability index"""
        mi_score = mi_visit(code, multi=True)
        return {
            "index": mi_score,
            "grade": self._get_mi_grade(mi_score)
        }
    
    def _detect_code_smells(self, tree, code):
        """Detect common code smells"""
        smells = []
        
        # Long functions (>50 lines)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_length = node.end_lineno - node.lineno
                if func_length > 50:
                    smells.append({
                        "type": "long_function",
                        "function": node.name,
                        "lines": func_length,
                        "severity": "medium"
                    })
        
        # Too many parameters
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                param_count = len(node.args.args)
                if param_count > 5:
                    smells.append({
                        "type": "too_many_parameters",
                        "function": node.name,
                        "count": param_count,
                        "severity": "low"
                    })
        
        # Duplicate code detection (simplified)
        lines = code.split('\n')
        duplicates = self._find_duplicate_blocks(lines)
        smells.extend(duplicates)
        
        return smells
    
    def _check_security(self, tree):
        """Check for security vulnerabilities"""
        issues = []
        
        for node in ast.walk(tree):
            # Detect eval() usage
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == 'eval':
                    issues.append({
                        "type": "dangerous_eval",
                        "line": node.lineno,
                        "severity": "high",
                        "message": "Using eval() is dangerous"
                    })
                
                # Detect SQL injection risks
                if isinstance(node.func, ast.Attribute) and node.func.attr == 'execute':
                    for arg in node.args:
                        if isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Add):
                            issues.append({
                                "type": "sql_injection_risk",
                                "line": node.lineno,
                                "severity": "high",
                                "message": "Potential SQL injection - use parameterized queries"
                            })
        
        return issues