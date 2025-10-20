# backend/test_db.py
"""
Database testing script - Run this to test your database setup
"""
import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

# FIXED: Use absolute imports instead of relative imports
from database import SessionLocal, init_db, check_db_connection
from models import Repository, CodeFile, Commit

def test_database_operations():
    """Test basic CRUD operations"""
    
    print("🧪 Testing Database Operations...")
    
    # Check connection
    if not check_db_connection():
        print("❌ Database connection failed!")
        return False
    
    print("✅ Database connection successful!")
    
    # Initialize tables
    if not init_db():
        print("❌ Failed to initialize database!")
        return False
    
    # Test CRUD operations
    db = SessionLocal()
    
    try:
        # CREATE: Add a test repository
        test_repo = Repository(
            github_url="https://github.com/test/repo",
            name="test-repo",
            owner="test-user",
            description="A test repository",
            status="pending"
        )
        db.add(test_repo)
        db.commit()
        db.refresh(test_repo)
        print(f"✅ Created repository: {test_repo.name} (ID: {test_repo.id})")
        
        # CREATE: Add a test code file
        test_file = CodeFile(
            repo_id=test_repo.id,
            file_path="/src/main.py",
            file_name="main.py",
            language="python",
            file_extension=".py",
            total_lines=100,
            functions_count=5,
            classes_count=2
        )
        db.add(test_file)
        db.commit()
        db.refresh(test_file)
        print(f"✅ Created code file: {test_file.file_name} (ID: {test_file.id})")
        
        # CREATE: Add a test commit
        test_commit = Commit(
            repo_id=test_repo.id,
            commit_hash="abc123def456",
            author="test-author",
            author_email="test@example.com",
            message="Initial commit",
            timestamp=datetime.now()
        )
        db.add(test_commit)
        db.commit()
        db.refresh(test_commit)
        print(f"✅ Created commit: {test_commit.commit_hash[:7]} (ID: {test_commit.id})")
        
        # READ: Query operations
        repos = db.query(Repository).all()
        files = db.query(CodeFile).all()
        commits = db.query(Commit).all()
        
        print(f"📊 Database contents:")
        print(f"   - Repositories: {len(repos)}")
        print(f"   - Code Files: {len(files)}")
        print(f"   - Commits: {len(commits)}")
        
        # TEST: Relationships
        repo_with_files = db.query(Repository).filter_by(id=test_repo.id).first()
        print(f"🔗 Repository '{repo_with_files.name}' has {len(repo_with_files.code_files)} files")
        print(f"🔗 Repository '{repo_with_files.name}' has {len(repo_with_files.commits)} commits")
        
        # UPDATE: Modify repository status
        test_repo.status = "completed"
        db.commit()
        print(f"✅ Updated repository status to: {test_repo.status}")
        
        # DELETE: Clean up test data
        db.delete(test_commit)
        db.delete(test_file)
        db.delete(test_repo)
        db.commit()
        print("🧹 Cleaned up test data")
        
        print("🎉 All database tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        db.rollback()
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    test_database_operations()
