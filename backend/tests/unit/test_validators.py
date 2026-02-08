"""
Unit tests for address validation (US3 - T042-T045)

Tests for validating user-provided street addresses.

TDD: These tests should FAIL until backend/src/utils/validators.py is implemented.
"""
import pytest


def test_validate_address_valid():
    """Test validation passes for valid addresses (T042)"""
    from src.utils.validators import validate_address
    
    # Valid addresses should not raise exceptions
    valid_addresses = [
        "1600 Pennsylvania Ave NW, Washington, DC 20500",
        "1 Main Street, Seattle, WA 98101",
        "742 Evergreen Terrace, Springfield, OR 97477",
        "123 Elm St, Apt 4B, New York, NY 10001",
        "P.O. Box 123, Anchorage, AK 99501"
    ]
    
    for address in valid_addresses:
        try:
            validate_address(address)
        except Exception as e:
            pytest.fail(f"Valid address '{address}' raised exception: {e}")


def test_validate_address_missing():
    """Test validation fails for missing address (T043)"""
    from src.utils.validators import validate_address
    from src.utils.errors import ApiException, ErrorCode
    
    # None should raise exception
    with pytest.raises(ApiException) as exc_info:
        validate_address(None)
    
    assert exc_info.value.code == ErrorCode.MISSING_PARAMETER
    assert exc_info.value.status_code == 400
    assert "address" in exc_info.value.message.lower()


def test_validate_address_empty():
    """Test validation fails for empty address (T044)"""
    from src.utils.validators import validate_address
    from src.utils.errors import ApiException, ErrorCode
    
    # Empty string should raise exception
    with pytest.raises(ApiException) as exc_info:
        validate_address("")
    
    assert exc_info.value.code == ErrorCode.INVALID_ADDRESS
    assert exc_info.value.status_code == 400
    
    # Whitespace-only should also raise exception
    with pytest.raises(ApiException) as exc_info:
        validate_address("   ")
    
    assert exc_info.value.code == ErrorCode.INVALID_ADDRESS
    assert exc_info.value.status_code == 400


def test_validate_address_exceeds_max_length():
    """Test validation fails for addresses exceeding 500 characters (T045)"""
    from src.utils.validators import validate_address
    from src.utils.errors import ApiException, ErrorCode
    
    # Create address longer than 500 characters
    long_address = "A" * 501
    
    with pytest.raises(ApiException) as exc_info:
        validate_address(long_address)
    
    assert exc_info.value.code == ErrorCode.INVALID_ADDRESS
    assert exc_info.value.status_code == 400
    assert "500" in exc_info.value.message


def test_validate_address_exactly_500_chars():
    """Test validation passes for address exactly at 500 character limit"""
    from src.utils.validators import validate_address
    
    # Exactly 500 characters should be valid
    address_500 = "A" * 500
    
    # Should not raise exception
    try:
        validate_address(address_500)
    except Exception as e:
        pytest.fail(f"Address at 500 char limit raised exception: {e}")


def test_validate_address_with_special_characters():
    """Test validation handles addresses with special characters"""
    from src.utils.validators import validate_address
    
    # Addresses with various special characters
    special_addresses = [
        "123 O'Brien St, Boston, MA 02101",
        "456 Saint-Laurent Blvd, Montréal, QC H2X 1Y2",
        "789 Main St. #200, Los Angeles, CA 90001"
    ]
    
    for address in special_addresses:
        try:
            validate_address(address)
        except Exception as e:
            pytest.fail(f"Address with special chars '{address}' raised exception: {e}")
