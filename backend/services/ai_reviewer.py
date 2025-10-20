# backend/services/ai_reviewer.py
import ollama

class AICodeReviewer:
    def __init__(self):
        self.model = "qwen2.5-coder:7b"
    
    def review_code_changes(self, diff, context):
        """AI-powered code review for PR"""
        prompt = f"""You are an experienced code reviewer. Analyze this code change:

File: {context['file_path']}
Context: {context['description']}

Code Diff:
{diff}

Provide feedback on:
1. Potential bugs or logic errors
2. Performance concerns
3. Security vulnerabilities
4. Code style and readability
5. Missing edge cases or error handling
6. Suggestions for improvement

Format your response as:
ISSUES:
- [severity] Issue description
SUGGESTIONS:
- Suggestion description"""

        response = ollama.generate(
            model=self.model,
            prompt=prompt
        )
        
        return self._parse_review(response['response'])
    
    def suggest_tests(self, function_code, function_name):
        """Generate test case suggestions"""
        prompt = f"""Generate test cases for this function:

Function Name: {function_name}
Code:
{function_code}

Suggest:
1. Happy path test cases
2. Edge cases to test
3. Error conditions to handle
4. Example test code (pytest format)"""

        response = ollama.generate(
            model=self.model,
            prompt=prompt
        )
        
        return response['response']