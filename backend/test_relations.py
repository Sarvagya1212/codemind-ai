import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from database import SessionLocal, init_db
from models import Repository, CodeFile, Commit

def run_test():
    init_db()
    db = SessionLocal()
    try:
        repo = Repository(
            github_url="https://github.com/testuser/testrepo",
            name="testrepo",
            owner="testuser",
            status="pending"
        )
        db.add(repo)
        db.commit()
        db.refresh(repo)

        code_file = CodeFile(
            repo_id=repo.id,
            file_path="src/main.py",
            file_name="main.py",
            language="python"
        )
        commit = Commit(
            repo_id=repo.id,
            commit_hash="1234567890abcdef",
            author="coder",
            message="Initial commit",
            timestamp=datetime.now(),
        )
        db.add(code_file)
        db.add(commit)
        db.commit()

        found_repo = db.query(Repository).filter_by(id=repo.id).first()
        db.refresh(found_repo)
        if found_repo.code_files:
            print(f"Found {len(found_repo.code_files)} related code files: {[f.file_name for f in found_repo.code_files]}")
        else:
            print("Did not find any relation (code_files).")

        if found_repo.commits:
            print(f"Found {len(found_repo.commits)} related commits: {[c.commit_hash for c in found_repo.commits]}")
        else:
            print("Did not find any relation (commits).")

        db.delete(commit)
        db.delete(code_file)
        db.delete(repo)
        db.commit()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    run_test()
