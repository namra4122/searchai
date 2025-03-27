"""
Database handler for the SearchAI application.
Manages connections and operations with PostgreSQL database.
"""

import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, update, text
from contextlib import asynccontextmanager

from searchai.config import POSTGRES_URI
from searchai.db.models import Base, UserQuery, SearchResult, GeneratedDocument, OutputFormat
from searchai.utils.logging_config import get_logger

# Get module logger
logger = get_logger(__name__)


# Global variables for engine and session factory
engine = None
async_session = None

def setup_db():
    """
    Set up the database engine and session factory.
    Should be called after the event loop is created.
    """
    
    global engine, async_session
    if engine is None:
        engine = create_async_engine(
            POSTGRES_URI.replace('postgresql://', 'postgresql+asyncpg://').split('?')[0],
            echo=True
        )
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    

@asynccontextmanager
async def get_session():
    """
    Async context manager for database sessions.
    Provides an async session and handles commit/rollback.
    """
    
    if async_session is None:
        setup_db()
    session = async_session()
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        
        await session.close()

async def verify_tables():
    """
    Verify that all required tables exist and are accessible.
    """
    logger.info("Verifying database tables...")
    async with get_session() as session:
        # Test query to check if tables exist
        result = await session.execute(
            text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
        )
        tables = [row[0] for row in result]
        logger.info(f"Found tables: {tables}")
        return tables

async def init_db():
    """
    Initialize the database, creating tables if they don't exist.
    """
    
    setup_db()
    
    try:
        logger.error(f"----------start try in init_db----------")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.error(f"----------enginer begin in init_db----------")
        
        # Verify tables
        tables = await verify_tables()
        logger.error(f"----------table verfied in init_db----------")
        expected_tables = {'user_queries', 'search_results', 'generated_documents'}
        missing_tables = expected_tables - set(tables)
        
        if missing_tables:
            logger.error(f"Missing tables: {missing_tables}")
            raise Exception(f"Failed to create tables: {missing_tables}")
            
        logger.info(f"Successfully verified tables: {tables}")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
        
    logger.info("Database initialized")
    

async def log_user_query(query_text: str, output_format: str) -> UserQuery:
    """
    Log a new user query to the database.
    
    Args:
        query_text (str): The user's query text
        output_format (str): The desired output format (markdown, pdf, ppt)
        
    Returns:
        UserQuery: The created user query object
    """
    
    
    # Convert output format to uppercase and ensure it's valid
    try:
        format_enum = OutputFormat[output_format.upper()]
    except KeyError:
        logger.error(f"Invalid output format: {output_format}")
        format_enum = OutputFormat.MARKDOWN  # Default to markdown
    
    try:
        async with get_session() as session:
            user_query = UserQuery(
                query_text=query_text,
                output_format=format_enum,
                status="pending"
            )
            session.add(user_query)
            await session.commit()
            await session.refresh(user_query)
            logger.info(f"Logged user query: {user_query.id}")
            return user_query
            
    except Exception as e:
        logger.error(f"Failed to log user query: {e}")
        raise
        

async def update_query_status(query_id, status):
    """
    Update the status of a user query.
    
    Args:
        query_id (str): The ID of the query to update
        status (str): The new status (pending, processing, completed, failed)
    """
    
    async with get_session() as session:
        stmt = update(UserQuery).where(UserQuery.id == query_id).values(status=status)
        await session.execute(stmt)
        logger.info(f"Updated query {query_id} status to {status}")
    

async def store_search_results(query_id, results):
    """
    Store search results in the database.
    
    Args:
        query_id (str): The ID of the associated user query
        results (list): List of search result dictionaries
    """
    
    async with get_session() as session:
        for result in results:
            search_result = SearchResult(
                query_id=query_id,
                source_url=result.get('url'),
                title=result.get('title'),
                snippet=result.get('snippet')
            )
            session.add(search_result)
        await session.commit()
        logger.info(f"Stored {len(results)} search results for query {query_id}")
    

async def log_generated_document(query_id, file_path, output_format, file_size=0):
    """
    Log a generated document in the database.
    
    Args:
        query_id (str): The ID of the associated user query
        file_path (str): Path to the generated document file
        output_format (str): Format of the generated document (markdown, pdf, ppt)
        file_size (int): Size of the file in bytes
    """
    
    format_enum = OutputFormat[output_format.upper()]
    
    async with get_session() as session:
        document = GeneratedDocument(
            query_id=query_id,
            file_path=file_path,
            format=format_enum,
            file_size=file_size
        )
        session.add(document)
        await session.commit()
        logger.info(f"Logged generated document: {file_path}")
    

async def get_query_history(limit=10):
    """
    Retrieve the most recent user queries.
    
    Args:
        limit (int): Maximum number of queries to return
        
    Returns:
        list: List of UserQuery objects
    """
    
    async with get_session() as session:
        result = await session.execute(
            select(UserQuery).order_by(UserQuery.created_at.desc()).limit(limit)
        )
        
        return result.scalars().all()