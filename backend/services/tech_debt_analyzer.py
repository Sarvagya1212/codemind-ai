# backend/services/tech_debt_analyzer.py
import networkx as nx
from collections import defaultdict

class TechnicalDebtAnalyzer:
    def __init__(self, repo_id):
        self.repo_id = repo_id
        self.dependency_graph = nx.DiGraph()
    
    def analyze_technical_debt(self):
        """Comprehensive technical debt analysis"""
        return {
            "circular_dependencies": self._find_circular_dependencies(),
            "code_duplication": self._detect_code_duplication(),
            "dead_code": self._find_dead_code(),
            "outdated_dependencies": self._check_outdated_dependencies(),
            "complexity_hotspots": self._find_complexity_hotspots(),
            "debt_score": self._calculate_debt_score()
        }
    
    def _find_circular_dependencies(self):
        """Detect circular import dependencies"""
        # Build dependency graph from parsed imports
        files_data = get_all_files_from_db(self.repo_id)
        
        for file_data in files_data:
            for import_path in file_data['imports']:
                self.dependency_graph.add_edge(file_data['path'], import_path)
        
        # Find cycles
        try:
            cycles = list(nx.simple_cycles(self.dependency_graph))
            
            circular_deps = []
            for cycle in cycles:
                if len(cycle) > 1:
                    circular_deps.append({
                        "files": cycle,
                        "severity": "HIGH" if len(cycle) > 3 else "MEDIUM",
                        "impact": f"{len(cycle)} files in circular dependency"
                    })
            
            return circular_deps
        except:
            return []
    
    def _detect_code_duplication(self):
        """Find duplicate code blocks"""
        files_data = get_all_files_from_db(self.repo_id)
        
        duplicates = []
        code_blocks = {}
        
        for file_data in files_data:
            with open(file_data['path'], 'r') as f:
                lines = f.readlines()
            
            # Check for duplicate blocks (10+ consecutive lines)
            for i in range(len(lines) - 10):
                block = ''.join(lines[i:i+10]).strip()
                block_hash = hash(block)
                
                if block_hash in code_blocks:
                    duplicates.append({
                        "file1": code_blocks[block_hash]['file'],
                        "line1": code_blocks[block_hash]['line'],
                        "file2": file_data['path'],
                        "line2": i + 1,
                        "lines": 10,
                        "similarity": 100
                    })
                else:
                    code_blocks[block_hash] = {
                        "file": file_data['path'],
                        "line": i + 1
                    }
        
        return duplicates
    
    def _find_dead_code(self):
        """Identify unused functions and imports"""
        dead_code = []
        
        # Find all function definitions
        all_functions = get_all_functions_from_db(self.repo_id)
        function_calls = self._extract_all_function_calls()
        
        for func in all_functions:
            # Check if function is never called
            if func['name'] not in function_calls and not func['name'].startswith('_'):
                dead_code.append({
                    "type": "unused_function",
                    "name": func['name'],
                    "file": func['file_path'],
                    "line": func['line_number']
                })
        
        return dead_code
    
    def _check_outdated_dependencies(self):
        """Check for outdated package versions"""
        # Parse requirements.txt or package.json
        outdated = []
        
        requirements_path = f"./repos/{self.repo_id}/requirements.txt"
        if os.path.exists(requirements_path):
            with open(requirements_path, 'r') as f:
                for line in f:
                    if '==' in line:
                        package, version = line.strip().split('==')
                        # In production, would check PyPI for latest version
                        outdated.append({
                            "package": package,
                            "current_version": version,
                            "latest_version": "unknown",  # Would fetch from PyPI
                            "severity": "MEDIUM"
                        })
        
        return outdated
    
    def _find_complexity_hotspots(self):
        """Find most complex modules"""
        files_data = get_all_files_from_db(self.repo_id)
        
        hotspots = []
        for file_data in files_data:
            if file_data['complexity_score'] > 50:
                hotspots.append({
                    "file": file_data['path'],
                    "complexity": file_data['complexity_score'],
                    "functions": file_data['functions_count'],
                    "lines": file_data['total_lines']
                })
        
        return sorted(hotspots, key=lambda x: x['complexity'], reverse=True)
    
    def _calculate_debt_score(self):
        """Calculate overall technical debt score (0-100)"""
        debt_analysis = self.analyze_technical_debt()
        
        score = 0
        # Circular dependencies (max 30 points)
        score += min(len(debt_analysis['circular_dependencies']) * 10, 30)
        
        # Code duplication (max 25 points)
        score += min(len(debt_analysis['code_duplication']) * 5, 25)
        
        # Dead code (max 20 points)
        score += min(len(debt_analysis['dead_code']) * 2, 20)
        
        # Complexity hotspots (max 25 points)
        score += min(len(debt_analysis['complexity_hotspots']) * 5, 25)
        
        return min(score, 100)