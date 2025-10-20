# backend/services/test_analyzer.py
import coverage
import ast
import os

class TestAnalyzer:
    def __init__(self, repo_path):
        self.repo_path = repo_path
        self.cov = coverage.Coverage()
    
    def analyze_test_coverage(self):
        """Analyze test coverage for the repository"""
        # Find test files
        test_files = self._find_test_files()
        
        if not test_files:
            return {
                "coverage_percent": 0,
                "message": "No test files found",
                "untested_files": self._get_all_source_files()
            }
        
        # Run coverage analysis
        self.cov.start()
        
        # Execute tests (simplified - would use pytest in practice)
        for test_file in test_files:
            try:
                exec(open(test_file).read())
            except:
                pass
        
        self.cov.stop()
        self.cov.save()
        
        # Analyze results
        coverage_data = self.cov.get_data()
        
        return {
            "overall_coverage": self._calculate_overall_coverage(),
            "file_coverage": self._get_file_coverage(coverage_data),
            "untested_functions": self._find_untested_functions(),
            "high_risk_areas": self._identify_high_risk_areas(),
            "test_recommendations": self._generate_test_recommendations()
        }
    
    def _find_test_files(self):
        """Find all test files in repository"""
        test_files = []
        for root, dirs, files in os.walk(self.repo_path):
            for file in files:
                if file.startswith('test_') or file.endswith('_test.py'):
                    test_files.append(os.path.join(root, file))
        return test_files
    
    def _find_untested_functions(self):
        """Identify functions with 0% test coverage"""
        untested = []
        
        for root, dirs, files in os.walk(self.repo_path):
            for file in files:
                if file.endswith('.py') and not file.startswith('test_'):
                    file_path = os.path.join(root, file)
                    
                    with open(file_path, 'r') as f:
                        try:
                            tree = ast.parse(f.read())
                            for node in ast.walk(tree):
                                if isinstance(node, ast.FunctionDef):
                                    # Check if function is covered
                                    is_covered = self._is_function_covered(
                                        file_path, 
                                        node.lineno, 
                                        node.end_lineno
                                    )
                                    
                                    if not is_covered:
                                        untested.append({
                                            "function": node.name,
                                            "file": file_path,
                                            "line": node.lineno,
                                            "complexity": self._get_function_complexity(node)
                                        })
                        except:
                            pass
        
        return untested
    
    def _identify_high_risk_areas(self):
        """Find high-complexity, low-coverage code"""
        high_risk = []
        
        untested = self._find_untested_functions()
        
        for func in untested:
            if func['complexity'] > 10:  # High complexity
                high_risk.append({
                    "function": func['function'],
                    "file": func['file'],
                    "risk_score": func['complexity'] * 2,  # No coverage = 2x multiplier
                    "reason": f"High complexity ({func['complexity']}) with 0% coverage"
                })
        
        return sorted(high_risk, key=lambda x: x['risk_score'], reverse=True)
    
    def _generate_test_recommendations(self):
        """Generate prioritized test recommendations"""
        high_risk = self._identify_high_risk_areas()
        
        recommendations = []
        for item in high_risk[:10]:  # Top 10 priorities
            recommendations.append({
                "priority": "HIGH" if item['risk_score'] > 20 else "MEDIUM",
                "function": item['function'],
                "file": item['file'],
                "recommendation": f"Add unit tests for {item['function']} - {item['reason']}",
                "estimated_tests": max(3, item['risk_score'] // 5)
            })
        
        return recommendations