"""
Crew AI search integration module for the SearchAI application.
Handles web searches using Crew AI tools.
"""

import asyncio
from tabnanny import verbose
import time
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor

from crewai import Agent, Crew, Task, Process
from crewai_tools import SerperDevTool

from searchai.config import (
    SERPER_API_KEY,
    SEARCH_TIMEOUT,
    CREWAI_GEMINI_MODEL
)
from searchai.db import db_handler

# Configure logging
from searchai.utils.logging_config import get_logger
from searchai.utils.exceptions import SearchError, DatabaseError, ConfigurationError
from searchai.utils.validation import validate_query

logger = get_logger(__name__)

class CrewSearchEngine:
    """
    Handles web searches using Crew AI framework and tools.
    """
    
    def __init__(self):
        """
        Initialize the CrewSearchEngine with necessary configurations.
        """
        try:
            if not SERPER_API_KEY:
                raise ConfigurationError("SERPER_API_KEY is not configured")
                
            # Initialize the Serper search tool
            self.search_tool = SerperDevTool(api_key=SERPER_API_KEY)
            logger.info("Serper API connection successful")
            
            self.executor = ThreadPoolExecutor(max_workers=4)
            
        except Exception as e:
            raise ConfigurationError(f"Failed to initialize search engine: {str(e)}")
    
    def _run_crew(self, query: str) -> str:
        """
        Run the crew in a separate thread.
        """
        try:
            logger.error(f"-------------------query = {query}-------------------")
            logger.error("-------------------_run_crew start-------------------")
            # Create a researcher agent with specific configuration
            logger.error("-------------------researcher init _run_crew-------------------")
            researcher = Agent(
                role="Web Researcher",
                goal="Find accurate and relevant information from credible sources",
                backstory="You are an expert web researcher specializing in finding and analyzing information from reliable sources.",
                llm=CREWAI_GEMINI_MODEL,
                verbose=True,
                allow_delegation=False
            )
            logger.error("-------------------researcher init done _run_crew-------------------")
            
            # Create a search task with clear expectations
            logger.error("-------------------search_task init _run_crew-------------------")
            search_task = Task(
                description=f"""Use the SerperDevTool to search for: {query}
                Instructions:
                1. Use the search tool to find relevant results
                2. For each result found, format it as follows:
                   - URL on first line
                   - Title on second line
                   - Brief summary on following lines
                3. Separate each result with a blank line
                4. Return only the formatted results, no additional commentary""",
                expected_output="A list of search results formatted with URL, title and summary, separated by blank lines",
                agent=researcher
            )
            logger.error("-------------------search_task init done _run_crew-------------------")
            
            # Configure and execute the crew
            logger.error("-------------------crew init _run_crew-------------------")
            crew = Crew(
                agents=[researcher],
                tasks=[search_task],
                verbose=True
            )
            logger.error("-------------------crew init done _run_crew-------------------")
            
            # Execute with timeout
            logger.error("-------------------crew start _run_crew-------------------")
            result = crew.kickoff()
            logger.error("-------------------crew done _run_crew-------------------")
            return result
            
        except Exception as e:
            logger.error(f"Crew execution failed: {str(e)}")
            raise RuntimeError(f"Search operation failed: {str(e)}")
    
    async def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Perform an asynchronous web search using Crew AI.
        """
        try:
            # Validate query
            logger.error(f"----------validate_query start in search----------")
            validated_query = validate_query(query)
            logger.error(f"----------validate_query end in search, string : {validated_query}----------")
            
            start_time = time.time()
            logger.info(f"Starting web search for query: {validated_query}")
            
            # Get the current event loop
            loop = asyncio.get_running_loop()
            
            # Run the crew with timeout
            try:
                logger.error(f"----------search start in search----------")
                results = await asyncio.wait_for(
                    loop.run_in_executor(self.executor, self._run_crew, validated_query),
                    timeout=SEARCH_TIMEOUT
                )
                logger.error(f"----------search end in search----------")
            except asyncio.TimeoutError:
                raise SearchError(f"Search timed out after {SEARCH_TIMEOUT} seconds")
            
            # Process and validate results
            search_results = self._parse_results(results)
            if not search_results:
                raise SearchError("No valid search results found")
            
            duration = time.time() - start_time
            logger.info(f"Search completed in {duration:.2f} seconds. Found {len(search_results)} results.")
            
            return search_results
            
        except SearchError:
            raise
        except Exception as e:
            raise SearchError(f"Search operation failed: {str(e)}")
    
    def _parse_results(self, raw_results: str) -> List[Dict[str, Any]]:
        """
        Parse the raw results from Crew AI into a structured format.
        """
        try:
            # Convert CrewOutput to string if needed
            result_text = str(raw_results)
            
            # Log the raw result for debugging
            logger.debug(f"Raw results: {result_text}")
            
            # Check if the result indicates no internet access
            if "do not have direct access to the internet" in result_text:
                return [{
                    'title': 'Error: No Internet Access',
                    'url': 'N/A',
                    'summary': 'The search agent does not have internet access. Please check your Serper API key configuration.'
                }]
            
            # Split the results into sections based on URLs
            sections = result_text.split('http')
            results = []
            
            for section in sections[1:]:  # Skip the first empty section
                try:
                    # Reconstruct the URL
                    url = 'http' + section.split('\n')[0].strip()
                    
                    # Get the lines after the URL
                    lines = [line.strip() for line in section.split('\n')[1:] if line.strip()]
                    
                    if not lines:
                        continue
                    
                    # Extract title and summary
                    title = lines[0]
                    summary = ' '.join(lines[1:]) if len(lines) > 1 else 'No summary available'
                    
                    results.append({
                        'title': title,
                        'url': url,
                        'summary': summary
                    })
                except Exception as e:
                    logger.warning(f"Failed to parse section: {e}")
                    continue
            
            # If no valid results were parsed, return the raw results
            if not results:
                logger.warning("No structured results found, returning raw results")
                return [{
                    'title': 'Search Results',
                    'url': 'N/A',
                    'summary': result_text
                }]
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to parse results: {e}")
            return [{
                'title': 'Raw Search Results',
                'url': 'N/A',
                'summary': str(raw_results)
            }]

# Create a singleton instance
search_engine = CrewSearchEngine()

async def perform_web_search(query: str) -> List[Dict[str, Any]]:
    """
    Perform a web search using the CrewSearchEngine.
    """
    try:
        # Initialize database
        try:
            await db_handler.init_db()
        except Exception as e:
            raise DatabaseError(f"Database initialization failed: {str(e)}")
        
        # Log the query
        try:
            user_query = await db_handler.log_user_query(
                query_text=query,
                output_format="markdown"
            )
        except Exception as e:
            raise DatabaseError(f"Failed to log query: {str(e)}")
        
        # Update status to processing
        await db_handler.update_query_status(user_query.id, "processing")
        
        try:
            # Perform search
            logger.error(f"----------search start in perform_web_search----------")
            results = await search_engine.search(query)
            logger.error(f"----------search end in perform_web_search----------")
            
            # Store results
            logger.error(f"----------store searcn start in perform_web_search----------")
            await db_handler.store_search_results(user_query.id, results)
            logger.error(f"----------store searcn end in perform_web_search----------")
            
            # Update status to completed
            await db_handler.update_query_status(user_query.id, "completed")
            
            return results
            
        except Exception as e:
            # Update status to failed
            await db_handler.update_query_status(user_query.id, "failed")
            raise SearchError(str(e))
            
    except (SearchError, DatabaseError):
        raise
    except Exception as e:
        raise SearchError(f"Unexpected error during search: {str(e)}")