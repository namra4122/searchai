"""
Validation utilities for the SearchAI application.
"""

import os
from pathlib import Path
from typing import Optional
from searchai.utils.exceptions import ValidationError  # Import ValidationError

from searchai.utils.logging_config import get_logger

logger = get_logger(__name__)

def validate_output_directory(output_dir: Optional[Path]) -> Path:
    """
    Validate and prepare the output directory.
    
    Args:
        output_dir (Optional[Path]): User-specified output directory or None
        
    Returns:
        Path: Validated output directory path
        
    Raises:
        ValidationError: If directory is invalid or not writable
    """
    from searchai.config import OUTPUT_DIR
    
    try:
        # If no custom directory specified, use default
        if output_dir is None:
            dir_path = Path(OUTPUT_DIR)
        else:
            dir_path = Path(output_dir)
            
        # Convert to absolute path
        dir_path = dir_path.resolve()
        
        # Check if parent directory exists and is writable
        parent_dir = dir_path.parent
        if not parent_dir.exists():
            raise ValidationError(f"Parent directory does not exist: {parent_dir}")
            
        # Try to create a test file to verify write permissions
        test_file = parent_dir / ".write_test"
        try:
            test_file.touch()
            test_file.unlink()
        except (OSError, PermissionError) as e:
            raise ValidationError(f"Directory not writable: {parent_dir}") from e
            
        # Create the output directory if it doesn't exist
        os.makedirs(dir_path, exist_ok=True)
        
        return dir_path
        
    except Exception as e:
        logger.error(f"Output directory validation failed: {str(e)}")
        raise ValidationError(f"Invalid output directory: {str(e)}")

def validate_format(format: str) -> str:
    """
    Validate the output format.
    
    Args:
        format (str): The output format to validate
        
    Returns:
        str: Validated format in lowercase
        
    Raises:
        ValidationError: If format is invalid
    """
    valid_formats = {"markdown", "pdf", "ppt"}
    format_lower = format.lower()
    
    if format_lower not in valid_formats:
        raise ValidationError(
            f"Invalid format '{format}'. Valid formats are: {', '.join(valid_formats)}"
        )
    
    return format_lower

def validate_query(query: str) -> str:
    """
    Validate the search query.
    
    Args:
        query (str): The search query to validate
        
    Returns:
        str: Validated query
        
    Raises:
        ValidationError: If query is invalid
    """
    if not query or not query.strip():
        raise ValidationError("Search query cannot be empty")
        
    if len(query) > 500:
        raise ValidationError("Search query too long (max 500 characters)")
        
    return query.strip()