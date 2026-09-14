class Week6Error(Exception):
    """
    Base exception for the Week 6 project.
    """


class ConfigurationError(Week6Error):
    """
    Raised when application configuration is invalid.
    """


class EmbeddingError(Week6Error):
    """
    Raised when an embedding operation fails.
    """


class VectorDatabaseError(Week6Error):
    """
    Raised when a vector database operation fails.
    """


class DocumentProcessingError(Week6Error):
    """
    Raised when document processing fails.
    """


class SearchError(Week6Error):
    """
    Raised when a search operation fails.
    """