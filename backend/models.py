from sqlalchemy import (
    Column, Integer, String, DateTime, JSON, ForeignKey, Text, Float, Index, func
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Repository(Base):
    __tablename__ = "repositories"
    id = Column(Integer, primary_key=True, autoincrement=True)
    github_url = Column(String(500), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    owner = Column(String(255))
    description = Column(Text)
    status = Column(String(50), default="pending", nullable=False)
    total_files = Column(Integer, default=0)
    total_commits = Column(Integer, default=0)
    total_lines = Column(Integer, default=0)
    contributors_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    last_synced = Column(DateTime, onupdate=func.now())
    repo_metadata = Column(JSON)

    code_files = relationship("CodeFile", back_populates="repository", cascade="all, delete-orphan")
    commits = relationship("Commit", back_populates="repository", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_repo_status', 'status'),
        Index('idx_repo_name', 'name'),
        Index('idx_repo_created_at', 'created_at'),
    )


class CodeFile(Base):
    __tablename__ = "code_files"
    id = Column(Integer, primary_key=True, autoincrement=True)
    repo_id = Column(Integer, ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_name = Column(String(255), nullable=False)
    language = Column(String(50))
    file_extension = Column(String(20))
    total_lines = Column(Integer, default=0)
    code_lines = Column(Integer, default=0)
    comment_lines = Column(Integer, default=0)
    blank_lines = Column(Integer, default=0)
    functions_count = Column(Integer, default=0)
    classes_count = Column(Integer, default=0)
    complexity_score = Column(Float)
    maintainability_index = Column(Float)
    last_modified = Column(DateTime)
    author = Column(String(255))
    file_size = Column(Integer)
    content_hash = Column(String(64))
    embedding_id = Column(String(100))

    repository = relationship("Repository", back_populates="code_files")

    __table_args__ = (
        Index('idx_file_repo_language', 'repo_id', 'language'),
        Index('idx_file_path', 'file_path'),
        Index('idx_file_extension', 'file_extension'),
        Index('idx_file_language', 'language'),
        Index('idx_file_complexity', 'complexity_score'),
        Index('idx_file_last_modified', 'last_modified'),
        Index('idx_repo_lang_complexity', 'repo_id', 'language', 'complexity_score'),
    )


class Commit(Base):
    __tablename__ = "commits"
    id = Column(Integer, primary_key=True, autoincrement=True)
    repo_id = Column(Integer, ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False)
    commit_hash = Column(String(40), unique=True, nullable=False)
    author = Column(String(255), nullable=False)
    author_email = Column(String(255))
    committer = Column(String(255))
    message = Column(Text, nullable=False)
    message_summary = Column(String(500))
    timestamp = Column(DateTime, nullable=False)
    committed_date = Column(DateTime)
    files_changed = Column(JSON)
    insertions = Column(Integer, default=0)
    deletions = Column(Integer, default=0)
    total_changes = Column(Integer, default=0)
    branch = Column(String(255))
    tags = Column(JSON)
    is_merge = Column(Integer, default=0)
    parent_commits = Column(JSON)

    repository = relationship("Repository", back_populates="commits")

    __table_args__ = (
        Index('idx_commit_hash', 'commit_hash'),
        Index('idx_commit_repo_id', 'repo_id'),
        Index('idx_commit_author', 'author'),
        Index('idx_commit_timestamp', 'timestamp'),
        Index('idx_commit_repo_timestamp', 'repo_id', 'timestamp'),
        Index('idx_commit_repo_author', 'repo_id', 'author'),
    )
