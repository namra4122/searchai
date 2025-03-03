"""
Main entry point for the SearchAI application.
Handles initialization and setup of application components.
"""

import os
import sys
import logging
import asyncio
from pathlib import Path

from searchai.cli.interface import app as cli_app
from searchai.db import db_handler
from searchai.config import (
    validate_config,
    OUTPUT_DIR,
    SERPER_API_KEY,
    GEMINI_API_KEY,
    POSTGRES_URI
)

def setup_logging():
    """
    Set up logging configuration for the entire application.
    """
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Remove any existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Configure logging format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(log_format)
    
    # Add console handler
    # console_handler = logging.StreamHandler(sys.stdout)
    # console_handler.setFormatter(formatter)
    # root_logger.addHandler(console_handler)
    
    # Add file handler
    log_file = os.path.join(OUTPUT_DIR, 'searchai.log')
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Set logging level
    root_logger.setLevel(logging.DEBUG)
    
    return root_logger

# Initialize logger
logger = setup_logging()

async def initialize_application():
    """
    Initialize all necessary components of the application.
    """
    try:
        #debugging_logs
        logger.debug("---------- main.py - initialize_application() - start ----------")
        
        # Validate configuration
        logger.info("Validating configuration...")
        validate_config()
        
        # Initialize database
        logger.info("Initializing database...")
        await db_handler.init_db()
        
        # Log successful initialization
        logger.info("Application initialized successfully")
        #debugging_logs
        logger.debug("---------- main.py - initialize_application() - end ----------")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {str(e)}")
        #debugging_logs
        logger.debug("---------- main.py - initialize_application() - end ----------")
        return False

def check_environment():
    """
    Check if all required environment variables and dependencies are set up.
    """
    #debugging_logs
    logger.debug("---------- main.py - check_environment() - start ----------")
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
        #debugging_logs
        logger.debug("---------- main.py - check_environment() - end ----------")
        return False
    #debugging_logs
    logger.debug("---------- main.py - check_environment() - end ----------")
    return True

def main():
    """
    Main entry point of the application.
    """
    try:
        #debugging_logs
        logger.debug("---------- main.py - main() - start ----------")
        # Check environment setup
        if not check_environment():
            sys.exit(1)
        
        # Initialize database
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            #debugging_logs
            logger.debug("---------- main.py - main() - new_event_loop() - started ----------")
            if not loop.run_until_complete(initialize_application()):
                #debugging_logs
                logger.debug("---------- main.py - main() - new_event_loop() - crashed ----------")
                sys.exit(1)
        finally:
            #debugging_logs
            logger.debug("---------- main.py - main() - new_event_loop() - ended ----------")
            loop.close()
        
        # Start the CLI application
        cli_app()
        #debugging_logs
        logger.debug("---------- main.py - main() - ended ----------")
        
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
