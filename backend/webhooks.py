# backend/webhooks.py
from fastapi import Request, HTTPException
import hmac
import hashlib

@app.post("/api/webhooks/github")
async def github_webhook(request: Request):
    """Handle GitHub webhook events"""
    # Verify webhook signature
    signature = request.headers.get('X-Hub-Signature-256')
    if not verify_signature(await request.body(), signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    payload = await request.json()
    event_type = request.headers.get('X-GitHub-Event')
    
    if event_type == 'push':
        await handle_push_event(payload)
    elif event_type == 'pull_request':
        await handle_pr_event(payload)
    
    return {"status": "processed"}

async def handle_push_event(payload):
    """Handle repository push events"""
    repo_url = payload['repository']['html_url']
    commits = payload['commits']
    
    # Find repo in database
    repo = get_repo_by_url(repo_url)
    if not repo:
        return
    
    # Extract changed files
    changed_files = set()
    for commit in commits:
        changed_files.update(commit['added'])
        changed_files.update(commit['modified'])
        changed_files.update(commit['removed'])
    
    # Queue incremental update
    await queue_incremental_update(repo.id, list(changed_files))
    
    # Post summary comment if configured
    if repo.settings.get('post_comments'):
        await post_update_summary(repo.id, commits)

async def handle_pr_event(payload):
    """Handle pull request events"""
    action = payload['action']
    pr = payload['pull_request']
    repo_url = payload['repository']['html_url']
    
    repo = get_repo_by_url(repo_url)
    if not repo:
        return
    
    if action == 'opened' or action == 'synchronize':
        # Run AI code review
        await run_pr_review(repo.id, pr)

async def run_pr_review(repo_id, pr_data):
    """Run automated code review on PR"""
    reviewer = AICodeReviewer()
    
    # Get PR diff
    diff = fetch_pr_diff(pr_data['diff_url'])
    
    # Analyze changes
    review_comments = []
    for file_diff in parse_diff(diff):
        context = {
            "file_path": file_diff['filename'],
            "description": pr_data['title']
        }
        
        review = reviewer.review_code_changes(file_diff['diff'], context)
        
        if review['issues']:
            review_comments.append({
                "path": file_diff['filename'],
                "position": file_diff['line_number'],
                "body": format_review_comment(review)
            })
    
    # Post review comments
    if review_comments:
        post_pr_review_comments(pr_data['url'], review_comments)