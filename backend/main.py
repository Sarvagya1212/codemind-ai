# backend/main.py

# ==============================================================================
# IMPORTS
# ==============================================================================
import os
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from services.github_service import GitHubService
from services.code_parser import CodeParser
from services.git_analyzer import GitAnalyzer


# ==============================================================================
# APP INITIALIZATION
# ==============================================================================
app = FastAPI(title="CodeMind AI API")


# ==============================================================================
# PYDANTIC MODELS
# ==============================================================================
class RepoIngestRequest(BaseModel):
    github_url: str

class RepoStatusResponse(BaseModel):
    id: int
    status: str
    progress: int
    message: str


# ==============================================================================
# BACKGROUND TASKS
# ==============================================================================
async def process_repository(repo_id: int, github_url: str):
    """Background task to process repository"""
    try:
        # Step 1: Clone
        update_status(repo_id, "cloning", 10)
        github = GitHubService(os.getenv("GITHUB_TOKEN"))
        result = github.clone_repository(github_url, f"./repos/{repo_id}")

        # Step 2: Parse code
        update_status(repo_id, "parsing", 30)
        parser = CodeParser()
        # Parse all files...

        # Step 3: Analyze Git history
        update_status(repo_id, "analyzing_history", 60)
        analyzer = GitAnalyzer()
        history = analyzer.analyze_repository(f"./repos/{repo_id}")

        # Step 4: Complete
        update_status(repo_id, "completed", 100)

    except Exception as e:
        update_status(repo_id, "failed", 0, str(e))


# ==============================================================================
# API ROUTES
# ==============================================================================

# ------------------------------------------------------------------------------
# REPOSITORY INGESTION AND STATUS
# ------------------------------------------------------------------------------
@app.post("/api/repos/ingest")
async def ingest_repository(request: RepoIngestRequest, background_tasks: BackgroundTasks):
    """Start repository analysis"""
    # Create database entry
    repo_id = create_repo_record(request.github_url)

    # Start background processing
    background_tasks.add_task(process_repository, repo_id, request.github_url)

    return {"repo_id": repo_id, "status": "processing"}

@app.get("/api/repos/{repo_id}/status")
async def get_repo_status(repo_id: int):
    """Check repository analysis status"""
    repo = get_repo_from_db(repo_id)
    return {
        "id": repo.id,
        "status": repo.status,
        "progress": calculate_progress(repo),
        "message": get_status_message(repo)
    }

# ------------------------------------------------------------------------------
# CHAT FUNCTIONALITY
# ------------------------------------------------------------------------------
@app.post("/api/repos/{repo_id}/chat")
async def chat_with_codebase(repo_id: int, question: str):
    """Interactive Q&A with codebase"""
    rag_service = RAGService(chroma_client)

    result = rag_service.answer_question(question, repo_id)

    # Save conversation history
    save_chat_message(repo_id, question, result["answer"])

    return {
        "question": question,
        "answer": result["answer"],
        "sources": result["sources"],
        "timestamp": datetime.utcnow()
    }

@app.get("/api/repos/{repo_id}/chat/history")
async def get_chat_history(repo_id: int):
    """Retrieve conversation history"""
    messages = get_chat_messages_from_db(repo_id)
    return {"messages": messages}

# ------------------------------------------------------------------------------
# DOCUMENTATION GENERATION AND RETRIEVAL
# ------------------------------------------------------------------------------
@app.post("/api/repos/{repo_id}/docs/generate")
async def generate_documentation(repo_id: int, doc_type: str):
    """Generate different types of documentation"""
    doc_gen = DocumentationGenerator()

    repo_data = get_repo_from_db(repo_id)
    code_structure = get_code_structure(repo_id)

    if doc_type == "readme":
        content = doc_gen.generate_readme(repo_data, code_structure)
    elif doc_type == "api":
        functions = get_all_functions(repo_id)
        content = doc_gen.generate_api_docs(functions)
    elif doc_type == "architecture":
        graph = build_dependency_graph(repo_id)
        content = doc_gen.generate_architecture_overview(graph, code_structure['modules'])
    else:
        return {"error": "Invalid doc_type"}

    # Save generated docs
    save_documentation(repo_id, doc_type, content)

    return {
        "doc_type": doc_type,
        "content": content,
        "generated_at": datetime.utcnow()
    }

@app.get("/api/repos/{repo_id}/docs/{doc_type}")
async def get_documentation(repo_id: int, doc_type: str):
    """Retrieve generated documentation"""
    doc = get_documentation_from_db(repo_id, doc_type)
    return doc

@app.get("/api/repos/{repo_id}/test-coverage")
async def get_test_coverage(repo_id: int):
    """Get comprehensive test coverage report"""
    repo = get_repo_from_db(repo_id)
    
    analyzer = TestAnalyzer(f"./repos/{repo_id}")
    coverage_report = analyzer.analyze_test_coverage()
    
    return {
        "repo_id": repo_id,
        "coverage": coverage_report,
        "generated_at": datetime.utcnow()
    }

@app.get("/api/repos/{repo_id}/technical-debt")
async def get_technical_debt(repo_id: int):
    """Get technical debt analysis"""
    debt_analyzer = TechnicalDebtAnalyzer(repo_id)
    debt_report = debt_analyzer.analyze_technical_debt()
    
    return {
        "repo_id": repo_id,
        "debt_analysis": debt_report,
        "recommendations": generate_debt_recommendations(debt_report),
        "generated_at": datetime.utcnow()
    }

@app.get("/api/repos/{repo_id}/code-quality")
async def get_code_quality_dashboard(repo_id: int):
    """Combined quality metrics dashboard"""
    quality_analyzer = QualityAnalyzer()
    
    files = get_all_files_from_db(repo_id)
    quality_reports = []
    
    for file_data in files:
        report = quality_analyzer.analyze_file(file_data['path'])
        quality_reports.append({
            "file": file_data['path'],
            "quality": report
        })
    
    # Aggregate metrics
    return {
        "repo_id": repo_id,
        "overall_quality": calculate_overall_quality(quality_reports),
        "files": quality_reports,
        "summary": {
            "high_severity_issues": count_high_severity(quality_reports),
            "medium_severity_issues": count_medium_severity(quality_reports),
            "total_code_smells": count_code_smells(quality_reports)
        }
    }