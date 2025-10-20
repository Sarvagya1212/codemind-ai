# backend/services/git_analyzer.py
import git
from datetime import datetime

class GitAnalyzer:
    def analyze_repository(self, repo_path):
        """Analyze Git history for insights"""
        repo = git.Repo(repo_path)
        
        commits = []
        for commit in repo.iter_commits():
            commits.append({
                "hash": commit.hexsha,
                "author": commit.author.name,
                "email": commit.author.email,
                "message": commit.message.strip(),
                "timestamp": datetime.fromtimestamp(commit.committed_date),
                "files_changed": [item.a_path for item in commit.diff(commit.parents[0])] if commit.parents else []
            })
        
        return {
            "total_commits": len(commits),
            "commits": commits,
            "contributors": self._get_contributors(commits),
            "most_changed_files": self._get_hotspots(commits)
        }
    
    def _get_contributors(self, commits):
        """Get contributor statistics"""
        contributors = {}
        for commit in commits:
            author = commit["author"]
            if author not in contributors:
                contributors[author] = {"commits": 0, "files_touched": set()}
            
            contributors[author]["commits"] += 1
            contributors[author]["files_touched"].update(commit["files_changed"])
        
        # Convert sets to counts
        for author in contributors:
            contributors[author]["files_touched"] = len(contributors[author]["files_touched"])
        
        return contributors
    
    def _get_hotspots(self, commits):
        """Find most frequently changed files"""
        file_changes = {}
        for commit in commits:
            for file_path in commit["files_changed"]:
                file_changes[file_path] = file_changes.get(file_path, 0) + 1
        
        # Sort by change frequency
        return sorted(file_changes.items(), key=lambda x: x[1], reverse=True)[:20]