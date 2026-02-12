"""
Base models for API responses and errors
"""

from typing import List, Dict, Any, Optional
from aws_lambda_powertools.utilities.parser import BaseModel, Field
from botocore.exceptions import ClientError


class APIError(BaseModel):
    """RFC-compliant error structure"""

    type: str = ""
    title: str = ""
    status: int = 400
    detail: str = ""
    instance: str = ""


class ResponseBody(BaseModel):
    """HTTP response body structure"""

    errors: List[APIError] = Field(default_factory=list)
    data: Optional[Any] = None


class Response(BaseModel):
    """Complete HTTP response structure for Lambda"""

    statusCode: int = 200
    headers: dict = {"Content-Type": "application/json"}
    isBase64Encoded: bool = False
    body: ResponseBody = Field(default_factory=ResponseBody)

    def add_error(self, error: APIError):
        """Add an error to the response"""
        self.statusCode = error.status
        self.body.errors.append(error)

    def add_boto_error(self, error: ClientError):
        """Convert boto ClientError to APIError and add to response"""
        err = APIError(
            title=error.response["Error"]["Code"],
            detail=error.response["Error"]["Message"],
            status=error.response["ResponseMetadata"]["HTTPStatusCode"],
        )
        self.add_error(err)

    def dump(self) -> Dict:
        """Return properly formatted response for Lambda"""
        result = self.model_dump(exclude={"body"})
        result["body"] = self.body.model_dump_json() if self.body else ""
        return result


# ============================================================================
# Feature 003: Address Lookup API Models
# ============================================================================


class ErrorResponse(BaseModel):
    """
    Error response model for address lookup API
    Single error object with code, message, and optional details
    """

    code: str = Field(..., description="Machine-readable error code (uppercase snake_case)")
    message: str = Field(..., description="Human-readable error description")
    details: Optional[str] = Field(None, description="Additional debugging information")


class Division(BaseModel):
    """
    Political or administrative boundary defined by OCD identifier
    Represents hierarchical jurisdictions (country, state, county, city, districts)
    """

    ocd_id: str = Field(
        ..., description="OCD division identifier", pattern=r"^ocd-division/country:us/.*"
    )
    name: str = Field(..., max_length=200, description="Human-readable division name")
    government_level: str = Field(
        ...,
        description="Government level category",
        pattern=r"^(federal|state|county|city|congressional|state_legislative|local)$",
    )
    has_data: bool = Field(
        ..., description="Whether OpenStates returned representatives for this division"
    )


class Representative(BaseModel):
    """
    Elected official holding public office at federal, state, or local level
    Primary key: id (OpenStates person ID for deduplication)
    """

    id: str = Field(..., description="OpenStates person ID (primary key for deduplication)")
    name: str = Field(..., max_length=200, description="Full legal name")
    office: str = Field(
        ...,
        max_length=100,
        description="Position title (e.g., 'US Senator', 'State Senator - District 12')",
    )
    party: Optional[str] = Field(
        None, description="Party affiliation (Democratic, Republican, Independent, etc.)"
    )
    email: Optional[str] = Field(None, description="Email address or semicolon-separated emails")
    phone: Optional[str] = Field(
        None, pattern=r"^\d{3}-\d{3}-\d{4}$", description="Phone number in XXX-XXX-XXXX format"
    )
    address: Optional[str] = Field(None, max_length=500, description="Office mailing address")
    website: Optional[str] = Field(None, description="Official website URL")
    photo_url: Optional[str] = Field(
        None, description="Photo URL (passed through without validation)"
    )
    government_level: str = Field(
        ...,
        description="Government level: federal, state, or local",
        pattern=r"^(federal|state|local)$",
    )
    jurisdiction: str = Field(..., description="Which district/state they represent")


class Office(BaseModel):
    """
    Position of elected authority within government
    Examples: 'President of the United States', 'US Senator', 'State Senator - District 12'
    """

    title: str = Field(..., max_length=100, description="Official position title")
    government_level: str = Field(
        ..., description="Government level category", pattern=r"^(federal|state|local)$"
    )
    division: str = Field(..., description="OCD-ID of jurisdiction this office represents")


class AddressLookupRequest(BaseModel):
    """
    Input payload for address-based representative lookup
    Validated from query parameter: ?address={address}
    """

    address: str = Field(..., min_length=1, max_length=500, description="Full US street address")


class Metadata(BaseModel):
    """Metadata about the address lookup request and response"""

    address: str = Field(..., description="Echo of input address for user confirmation")
    government_levels: List[str] = Field(
        default_factory=list, description="Which government levels are included in response"
    )
    response_time_ms: Optional[int] = Field(
        None, description="End-to-end processing time in milliseconds"
    )


class AddressLookupResponse(BaseModel):
    """
    Successful response containing representatives for a given address
    Includes partial results with warnings when some divisions have no data
    """

    representatives: List[Representative] = Field(
        default_factory=list, description="Array of representatives (deduplicated by id)"
    )
    metadata: Metadata = Field(..., description="Request context and performance data")
    warnings: Optional[List[str]] = Field(
        None,
        description="Coverage gaps or missing divisions (e.g., 'No data available for: ocd-division/...')",
    )
