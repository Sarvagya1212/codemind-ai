# backend/services/breaking_changes_detector.py
import ast
import difflib

class BreakingChangesDetector:
    def detect_breaking_changes(self, old_code, new_code, file_path):
        """Detect API breaking changes between versions"""
        breaking_changes = []
        
        try:
            old_tree = ast.parse(old_code)
            new_tree = ast.parse(new_code)
        except SyntaxError:
            return []
        
        # Extract API signatures
        old_api = self._extract_api_signatures(old_tree)
        new_api = self._extract_api_signatures(new_tree)
        
        # Check for removed functions/classes
        for name, sig in old_api.items():
            if name not in new_api:
                breaking_changes.append({
                    "type": "REMOVED",
                    "severity": "HIGH",
                    "element": name,
                    "message": f"Function/Class '{name}' was removed",
                    "file": file_path,
                    "migration_hint": f"Replace usages of {name} with alternative"
                })
            else:
                # Check for signature changes
                changes = self._compare_signatures(sig, new_api[name])
                if changes:
                    breaking_changes.append({
                        "type": "SIGNATURE_CHANGE",
                        "severity": "HIGH",
                        "element": name,
                        "changes": changes,
                        "file": file_path,
                        "old_signature": sig,
                        "new_signature": new_api[name],
                        "migration_hint": self._generate_migration_hint(sig, new_api[name])
                    })
        
        # Check for renamed public APIs
        renamed = self._detect_renames(old_api, new_api)
        breaking_changes.extend(renamed)
        
        return breaking_changes
    
    def _extract_api_signatures(self, tree):
        """Extract all public function/class signatures"""
        signatures = {}
        
        for node in ast.walk(tree):
            # Functions
            if isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                signatures[node.name] = {
                    "type": "function",
                    "params": [arg.arg for arg in node.args.args],
                    "defaults": len(node.args.defaults),
                    "returns": ast.unparse(node.returns) if node.returns else None
                }
            
            # Classes
            elif isinstance(node, ast.ClassDef) and not node.name.startswith('_'):
                methods = []
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and not item.name.startswith('_'):
                        methods.append({
                            "name": item.name,
                            "params": [arg.arg for arg in item.args.args]
                        })
                
                signatures[node.name] = {
                    "type": "class",
                    "methods": methods,
                    "bases": [ast.unparse(base) for base in node.bases]
                }
        
        return signatures
    
    def _compare_signatures(self, old_sig, new_sig):
        """Compare two signatures for breaking changes"""
        changes = []
        
        if old_sig["type"] == "function":
            # Parameter count changed
            if len(old_sig["params"]) > len(new_sig["params"]):
                changes.append("Parameters removed")
            
            # Parameter order changed
            common_params = min(len(old_sig["params"]), len(new_sig["params"]))
            for i in range(common_params):
                if old_sig["params"][i] != new_sig["params"][i]:
                    changes.append(f"Parameter order changed: {old_sig['params'][i]} -> {new_sig['params'][i]}")
            
            # Return type changed
            if old_sig["returns"] != new_sig["returns"]:
                changes.append(f"Return type changed: {old_sig['returns']} -> {new_sig['returns']}")
        
        elif old_sig["type"] == "class":
            # Public methods removed
            old_methods = {m["name"] for m in old_sig["methods"]}
            new_methods = {m["name"] for m in new_sig["methods"]}
            
            removed = old_methods - new_methods
            if removed:
                changes.append(f"Methods removed: {', '.join(removed)}")
        
        return changes
    
    def _generate_migration_hint(self, old_sig, new_sig):
        """Generate migration guide for breaking change"""
        if old_sig["type"] == "function":
            old_params = ", ".join(old_sig["params"])
            new_params = ", ".join(new_sig["params"])
            
            return f"""
Migration Guide:
Old: function_name({old_params})
New: function_name({new_params})

Update all calls to match new signature.
"""
        return "Please review the changes and update usage accordingly."
    
    def _detect_renames(self, old_api, new_api):
        """Detect potential renames using similarity matching"""
        renamed = []
        
        old_names = set(old_api.keys())
        new_names = set(new_api.keys())
        
        removed = old_names - new_names
        added = new_names - old_names
        
        for old_name in removed:
            for new_name in added:
                # Check signature similarity
                similarity = difflib.SequenceMatcher(None, old_name, new_name).ratio()
                
                if similarity > 0.7:  # Likely a rename
                    renamed.append({
                        "type": "RENAMED",
                        "severity": "MEDIUM",
                        "old_name": old_name,
                        "new_name": new_name,
                        "confidence": similarity,
                        "migration_hint": f"Replace all usages of '{old_name}' with '{new_name}'"
                    })
        
        return renamed

# Add to webhook handler
async def handle_push_event(payload):
    """Enhanced push handler with breaking changes detection"""
    repo_url = payload['repository']['html_url']
    commits = payload['commits']
    
    repo = get_repo_by_url(repo_url)
    if not repo:
        return
    
    detector = BreakingChangesDetector()
    all_breaking_changes = []
    
    for commit in commits:
        # Get file diffs
        for file in commit['modified']:
            if file.endswith('.py'):  # Check Python files
                old_content = get_file_content_at_commit(repo.id, file, commit['id'] + '^')
                new_content = get_file_content_at_commit(repo.id, file, commit['id'])
                
                breaking_changes = detector.detect_breaking_changes(
                    old_content, 
                    new_content, 
                    file
                )
                
                all_breaking_changes.extend(breaking_changes)
    
    # If breaking changes found, notify
    if all_breaking_changes:
        await notify_breaking_changes(repo.id, all_breaking_changes, payload['head_commit']['url'])