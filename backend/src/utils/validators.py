"""
Address validation utilities for address lookup API

Provides validation functions for user-provided street addresses.

Feature: 003-address-lookup (User Story 3 - T055)
"""

from src.utils.errors import ApiException, ErrorCode


def validate_address(address: str) -> None:
    """
    Validate user-provided street address

    Args:
        address: Street address to validate

    Raises:
        ApiException:
            - MISSING_PARAMETER (400) if address is None
            - INVALID_ADDRESS (400) if address is empty or exceeds 500 characters

    Validation Rules:
        - Address cannot be None
        - Address cannot be empty string or whitespace-only
        - Address cannot exceed 500 characters
        - Special characters are allowed (apostrophes, hyphens, accents, etc.)

    Examples:
        >>> validate_address("1600 Pennsylvania Ave NW, Washington, DC 20500")
        None  # No exception means valid

        >>> validate_address(None)
        Raises ApiException with MISSING_PARAMETER

        >>> validate_address("")
        Raises ApiException with INVALID_ADDRESS
    """
    # Check for None (missing parameter)
    if address is None:
        raise ApiException(
            code=ErrorCode.MISSING_PARAMETER,
            message="Address parameter is required",
            status_code=400,
            details="The 'address' query parameter must be provided",
        )

    # Check for empty or whitespace-only
    if not address or not address.strip():
        raise ApiException(
            code=ErrorCode.INVALID_ADDRESS,
            message="Address cannot be empty",
            status_code=400,
            details="The address must contain at least one non-whitespace character",
        )

    # Check maximum length (500 characters)
    if len(address) > 500:
        raise ApiException(
            code=ErrorCode.INVALID_ADDRESS,
            message=f"Address exceeds maximum length of 500 characters (provided: {len(address)})",
            status_code=400,
            details="Please provide a shorter address",
        )

    # If all checks pass, address is valid (no exception)
