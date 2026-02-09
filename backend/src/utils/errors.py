"""
Error handling framework for address lookup API

Provides error codes and custom exception class for consistent error responses
per feature 003-address-lookup specification.
"""
from enum import Enum
from typing import Optional


class ErrorCode(str, Enum):
    """Standard error codes for address lookup API"""
    MISSING_PARAMETER = "MISSING_PARAMETER"
    INVALID_ADDRESS = "INVALID_ADDRESS"
    ADDRESS_NOT_FOUND = "ADDRESS_NOT_FOUND"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class ApiException(Exception):
    """Custom exception for API errors with structured error information"""
    
    def __init__(
        self,
        code: ErrorCode,
        message: str,
        status_code: int,
        details: Optional[str] = None
    ):
        """
        Create API exception
        
        Args:
            code: Machine-readable error code from ErrorCode enum
            message: Human-readable error message
            status_code: HTTP status code (400, 404, 500, 503)
            details: Optional additional debugging information
        """
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(message)
    
    def to_dict(self) -> dict:
        """Convert exception to dictionary for JSON response"""
        result = {
            "code": self.code.value,
            "message": self.message
        }
        if self.details:
            result["details"] = self.details
        return result


# HTTP status code mappings for error codes
ERROR_STATUS_CODES = {
    ErrorCode.MISSING_PARAMETER: 400,
    ErrorCode.INVALID_ADDRESS: 400,
    ErrorCode.ADDRESS_NOT_FOUND: 404,
    ErrorCode.EXTERNAL_SERVICE_ERROR: 503,
    ErrorCode.RATE_LIMIT_EXCEEDED: 503,
    ErrorCode.INTERNAL_ERROR: 500,
}
