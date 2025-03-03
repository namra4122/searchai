"""
Custom exceptions for the SearchAI application.
"""

class SearchAIError(Exception):
    """Base exception for SearchAI application"""
    pass

class APIError(SearchAIError):
    """Error when interacting with external APIs"""
    pass

class SearchError(SearchAIError):
    """Error during web search operations"""
    pass

class LLMError(SearchAIError):
    """Error during LLM operations"""
    pass

class DocumentGenerationError(SearchAIError):
    """Error during document generation"""
    
    def __init__(self, message: str, format: str = None, details: str = None):
        self.format = format
        self.details = details
        super().__init__(f"Document generation failed ({format}): {message}" if format else message)

class DatabaseError(SearchAIError):
    """Error during database operations"""
    pass

class ValidationError(SearchAIError):
    """Error during input validation"""
    pass

class ConfigurationError(SearchAIError):
    """Error in application configuration"""
    pass

class FileSystemError(SearchAIError):
    """Error during file system operations"""
    pass

class FormatError(SearchAIError):
    """Error related to document formatting"""
    pass 