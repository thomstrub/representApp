"""
DynamoDB persistence layer
"""
import boto3
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError
from aws_lambda_powertools import Logger
from typing import List, Optional
from .domain import Representative
from .base import Response, APIError


class RepresentativeStore:
    """DynamoDB operations for Representatives"""
    
    def __init__(self, table_name: str, region: str = "us-east-1"):
        self.table_name = table_name
        self.region = region
        self.conn = boto3.resource('dynamodb', region_name=region)
        self.table = self.conn.Table(table_name)
        self.logger = Logger(child=True)

    def create(self, representative: Representative) -> Response:
        """Create a new representative"""
        response = Response()
        item = representative.dict()
        
        try:
            self.table.put_item(
                Item=item,
                ConditionExpression=Attr('id').not_exists()
            )
            response.body.data = [representative.dict()]
        except ClientError as e:
            self.logger.error(f"Error creating representative: {e}")
            response.add_boto_error(e)
        
        return response

    def get(self, rep_id: str) -> Response:
        """Get a representative by ID"""
        response = Response()
        
        try:
            result = self.table.get_item(Key={"id": rep_id})
            item = result.get('Item')
            
            if item:
                response.body.data = [Representative(**item).dict()]
            else:
                error = APIError(
                    status=404,
                    title="Not Found",
                    detail=f"Representative with ID {rep_id} not found"
                )
                response.add_error(error)
        except ClientError as e:
            self.logger.error(f"Error getting representative: {e}")
            response.add_boto_error(e)
        
        return response

    def list_all(self) -> Response:
        """Get all representatives"""
        response = Response()
        items = []
        
        try:
            result = self.table.scan()
            items.extend(result.get('Items', []))
            
            # Handle pagination
            while 'LastEvaluatedKey' in result:
                result = self.table.scan(
                    ExclusiveStartKey=result['LastEvaluatedKey']
                )
                items.extend(result.get('Items', []))
            
            representatives = [Representative(**item).dict() for item in items]
            response.body.data = representatives
            
        except ClientError as e:
            self.logger.error(f"Error listing representatives: {e}")
            response.add_boto_error(e)
        
        return response

    def update(self, representative: Representative) -> Response:
        """Update an existing representative"""
        response = Response()
        item = representative.dict()
        
        try:
            self.table.put_item(
                Item=item,
                ConditionExpression=Attr("id").eq(representative.id)
            )
            response.body.data = [representative.dict()]
        except ClientError as e:
            self.logger.error(f"Error updating representative: {e}")
            response.add_boto_error(e)
        
        return response

    def delete(self, rep_id: str) -> Response:
        """Delete a representative"""
        response = Response()
        
        try:
            result = self.table.delete_item(
                Key={'id': rep_id},
                ConditionExpression=Attr("id").eq(rep_id),
                ReturnValues="ALL_OLD"
            )
            
            attr = result.get("Attributes")
            if attr:
                response.body.data = [Representative(**attr).dict()]
            
        except ClientError as e:
            self.logger.error(f"Error deleting representative: {e}")
            response.add_boto_error(e)
        
        return response
