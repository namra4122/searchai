import os
import logging
import warnings
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler

from searchai.config import BASE_DIR

# Create logs directory
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

for logger_name in logging.root.manager.loggerDict:
    logging.getLogger(logger_name).setLevel(logging.INFO)


def setup_logging():
    """
    Configure logging for the application.
    Sets up file logging only (no console output).
    """
    # Disable all warnings
    warnings.filterwarnings('ignore')
    
    # Filter out specific Pydantic warnings
    warnings.filterwarnings('ignore', category=DeprecationWarning, module='pydantic')
    
    # Generate log filename with timestamp
    current_date = datetime.now().strftime('%Y%m%d')
    log_filename = f'search_{current_date}.log'
    log_filepath = os.path.join(LOGS_DIR, log_filename)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(levelname)s - %(message)s'  # Simplified format
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)  # Set to WARNING to reduce verbosity
    
    # Clear any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_filepath,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Add handlers
    root_logger.addHandler(file_handler)
    
    # Disable SQLAlchemy logging completely (this is critical)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    logging.getLogger('sqlalchemy').setLevel(logging.INFO)
    
    # Disable Pydantic warnings
    logging.getLogger('pydantic').setLevel(logging.INFO)  # More severe than ERROR
    
    # Disable asyncio debug logs
    logging.getLogger('asyncio').setLevel(logging.INFO)
    
    # Disable CrewAI verbose logs
    logging.getLogger('crewai').setLevel(logging.INFO)
    
    # Disable LiteLLM logs
    logging.getLogger('litellm').setLevel(logging.INFO)
    
    # Log startup information (to file only)
    logging.getLogger('searchai').info(f"Logging initialized. Log file: {log_filepath}")

def get_logger(name):
    """
    Get a logger with the specified name.
    
    Args:
        name (str): Logger name, typically __name__ of the module
        
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.WARNING)  # Set individual loggers to WARNING level
    return logger