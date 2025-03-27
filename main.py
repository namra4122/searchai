"""
Main entry point for the SearchAI application.
Handles initialization and setup of application components.
"""
import sys
import logging
import asyncio
from pathlib import Path

from searchai.cli.interface import app as cli_app
from searchai.db import db_handler
from searchai.config import (
    validate_config,
    SERPER_API_KEY,
    GEMINI_API_KEY,
    POSTGRES_URI
)

from searchai.utils.logging_config import setup_logging, get_logger

# Initialize logging
def silence_all_loggers():
    """Force silence all loggers to prevent console output"""
    # First set up your file handler
    setup_logging()
    
    # Then aggressively silence everything else
    for logger_name in logging.root.manager.loggerDict:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)  # Highest level, almost nothing gets through
        
        # Remove any console handlers
        for handler in logger.handlers[:]:
            if isinstance(handler, logging.StreamHandler) and handler.stream in (sys.stdout, sys.stderr):
                logger.removeHandler(handler)

# Replace your setup_logging() call with this
silence_all_loggers()
logger = get_logger(__name__)

async def initialize_application():
    """
    Initialize all necessary components of the application.
    """
    try:
        # Validate configuration
        logger.info("Validating configuration...")
        validate_config()
        
        # Initialize database
        logger.info("Initializing database...")
        await db_handler.init_db()
        
        # Log successful initialization
        logger.info("Application initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {str(e)}")
        return False

def check_environment():
    """
    Check if all required environment variables and dependencies are set up.
    """
    missing_vars = []
    
    if not SERPER_API_KEY:
        missing_vars.append("SERPER_API_KEY")
    if not GEMINI_API_KEY:
        missing_vars.append("GEMINI_API_KEY")
    if not POSTGRES_URI:
        missing_vars.append("POSTGRES_URI")
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set these variables in your .env file")
        return False
    return True

def main():
    """
    Main entry point of the application.
    """
    try:
        # Check environment setup
        if not check_environment():
            sys.exit(1)
        
        # Initialize database
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            if not loop.run_until_complete(initialize_application()):
                sys.exit(1)
        finally:
            loop.close()
        
        # Start the CLI application
        cli_app()
        
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
