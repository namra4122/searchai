"""
Database models for the SearchAI application.
Defines the schema for storing user queries and results.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
import enum
import uuid
from searchai.utils.logging_config import get_logger

logger = get_logger(__name__)

Base = declarative_base()

class OutputFormat(enum.Enum):
    MARKDOWN = "markdown"
    PDF = "pdf"
    PPT = "ppt"

class UserQuery(Base):
    """
    Represents a user query and its metadata.
    """
    __tablename__ = 'user_queries'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    query_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    output_format = Column(Enum(OutputFormat), nullable=False)
    status = Column(String, default="pending")  # pending, processing, completed, failed
    
    def __repr__(self):
        return f"<UserQuery(id='{self.id}', query='{self.query_text[:30]}...', status='{self.status}')>"

class SearchResult(Base):
    """
    Represents search results obtained from Crew AI.
    """
    __tablename__ = 'search_results'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    query_id = Column(String, ForeignKey('user_queries.id'), nullable=False)
    source_url = Column(String)
    title = Column(String)
    snippet = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<SearchResult(id='{self.id}', title='{self.title[:30]}...', source='{self.source_url}')>"

class GeneratedDocument(Base):
    """
    Represents a document generated from the search results.
    """
    __tablename__ = 'generated_documents'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    query_id = Column(String, ForeignKey('user_queries.id'), nullable=False)
    file_path = Column(String, nullable=False)
    format = Column(Enum(OutputFormat), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    file_size = Column(Integer)  # Size in bytes
    
    def __repr__(self):
        return f"<GeneratedDocument(id='{self.id}', format='{self.format}', path='{self.file_path}')>"