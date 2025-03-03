"""
Logging configuration for the SearchAI application.
"""

import os
import logging
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler

from searchai.config import BASE_DIR

# Create logs directory
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

def setup_logging():
    """
    Configure logging for the application.
    Sets up both file and console logging.
    """
    # Generate log filename with timestamp
    current_date = datetime.now().strftime('%Y%m%d')
    log_filename = f'search_{current_date}.log'
    log_filepath = os.path.join(LOGS_DIR, log_filename)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)  # Set to INFO to reduce verbosity
    
    # Clear any existing handlers
    root_logger.handlers = []
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_filepath,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.WARNING)  # Show warnings and above in console
    
    # Add handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Disable SQLAlchemy logging
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)  # Suppress SQLAlchemy debug logs
    logging.getLogger('sqlalchemy.orm').setLevel(logging.WARNING)  # Suppress ORM debug logs
    
    # Disable Pydantic warnings
    logging.getLogger('pydantic').setLevel(logging.ERROR)  # Suppress Pydantic warnings
    
    # Disable asyncio debug logs
    logging.getLogger('asyncio').setLevel(logging.WARNING)  # Suppress asyncio debug logs
    
    # Log startup information
    root_logger.info(f"Logging initialized. Log file: {log_filepath}")

def get_logger(name):
    """
    Get a logger with the specified name.
    
    Args:
        name (str): Logger name, typically __name__ of the module
        
    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name) 