# backend/services/notification_service.py
import requests

class NotificationService:
    def __init__(self):
        self.slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
        self.discord_webhook = os.getenv('DISCORD_WEBHOOK_URL')
    
    def notify_analysis_complete(self, repo_id, stats):
        """Send notification when repo analysis completes"""
        message = f"""
✅ CodeMind AI Analysis Complete

Repository: {stats['repo_name']}
- Files Analyzed: {stats['total_files']}
- Functions Found: {stats['total_functions']}
- Test Coverage: {stats['coverage_percent']}%
- Tech Debt Score: {stats['debt_score']}/100

View Dashboard: https://your-app.com/repos/{repo_id}
"""
        
        if self.slack_webhook:
            self._send_slack(message)
        
        if self.discord_webhook:
            self._send_discord(message)
    
    def notify_high_risk_pr(self, pr_url, issues):
        """Alert team about high-risk PR"""
        message = f"""
⚠️ High Risk Pull Request Detected

PR: {pr_url}

Critical Issues Found:
{self._format_issues(issues)}

Please review carefully before merging.
"""
        
        self._send_slack(message)
    
    def _send_slack(self, message):
        """Send Slack notification"""
        requests.post(self.slack_webhook, json={"text": message})
    
    def _send_discord(self, message):
        """Send Discord notification"""
        requests.post(self.discord_webhook, json={"content": message})