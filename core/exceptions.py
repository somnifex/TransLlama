class TransLlamaException(Exception):
    """Base exception for TransLlama"""
    pass


class ModelNotFoundException(TransLlamaException):
    """Raised when a requested model is not found"""
    pass


class ModelLoadException(TransLlamaException):
    """Raised when a model fails to load"""
    pass


class InvalidLanguageException(TransLlamaException):
    """Raised when an unsupported language is requested"""
    pass


class AuthenticationException(TransLlamaException):
    """Raised when authentication fails"""
    pass


class RateLimitException(TransLlamaException):
    """Raised when rate limit is exceeded"""
    pass


class TranslationException(TransLlamaException):
    """Raised when translation fails"""
    pass
