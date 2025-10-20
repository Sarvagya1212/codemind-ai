# backend/services/github_service.py
import git
from github import Github
import os

class GitHubService:
    def __init__(self, github_token):
        self.github = Github(github_token)
    
    def clone_repository(self, repo_url, local_path):
        """Clone GitHub repository locally"""
        try:
            repo = git.Repo.clone_from(repo_url, local_path)
            return {
                "success": True,
                "path": local_path,
                "total_commits": len(list(repo.iter_commits()))
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_repo_metadata(self, repo_url):
        """Fetch repository metadata from GitHub API"""
        repo_name = repo_url.split("github.com/")[-1]
        repo = self.github.get_repo(repo_name)
        
        return {
            "name": repo.name,
            "description": repo.description,
            "language": repo.language,
            "stars": repo.stargazers_count,
            "forks": repo.forks_count,
            "open_issues": repo.open_issues_count
        }
    
    def get_pull_requests(self, repo_url, limit=50):
        """Fetch recent pull requests with comments"""
        repo_name = repo_url.split("github.com/")[-1]
        repo = self.github.get_repo(repo_name)
        
        prs = []
        for pr in repo.get_pulls(state='all')[:limit]:
            comments = [c.body for c in pr.get_issue_comments()]
            prs.append({
                "number": pr.number,
                "title": pr.title,
                "body": pr.body,
                "comments": comments,
                "merged": pr.merged,
                "created_at": pr.created_at
            })
        return prs