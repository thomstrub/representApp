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
            title=error.response['Error']['Code'],
            detail=error.response['Error']['Message'],
            status=error.response['ResponseMetadata']['HTTPStatusCode']
        )
        self.add_error(err)

    def dump(self) -> Dict:
        """Return properly formatted response for Lambda"""
        result = self.dict(exclude={'body'})
        result['body'] = self.body.json() if self.body else ''
        return result
