"""
Unit tests for API handler
"""
import json
import pytest
import os
from moto import mock_aws
import boto3


# Set environment variables before importing handler
os.environ['DDB_TABLE_NAME'] = 'test-representatives'
os.environ['LOG_LEVEL'] = 'DEBUG'
os.environ['POWERTOOLS_SERVICE_NAME'] = 'test-represent-api'
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'


from src.handlers.api import handler
from src.models.domain import Representative


@mock_aws
def test_create_representative():
    """Test creating a representative"""
    # Setup mock DynamoDB
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.create_table(
        TableName='test-representatives',
        KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
        BillingMode='PAY_PER_REQUEST'
    )
    
    # Create test event
    event = {
        'version': '2.0',
        'routeKey': 'POST /api/representatives',
        'rawPath': '/api/representatives',
        'requestContext': {
            'http': {
                'method': 'POST'
            }
        },
        'body': json.dumps({
            'name': 'John Doe',
            'position': 'Senator',
            'state': 'CA',
            'party': 'Independent'
        })
    }
    
    # Mock context
    class MockContext:
        function_name = "test-function"
        memory_limit_in_mb = 128
        invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test"
        aws_request_id = "test-request-id"
    
    # Call handler
    response = handler(event, MockContext())
    
    # Assertions
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert 'data' in body
    assert len(body['data']) == 1
    assert body['data'][0]['name'] == 'John Doe'
    assert body['data'][0]['state'] == 'CA'


@mock_aws
def test_list_representatives():
    """Test listing all representatives"""
    # Setup mock DynamoDB
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.create_table(
        TableName='test-representatives',
        KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
        BillingMode='PAY_PER_REQUEST'
    )
    
    # Create test event
    event = {
        'version': '2.0',
        'routeKey': 'GET /api/representatives',
        'rawPath': '/api/representatives',
        'requestContext': {
            'http': {
                'method': 'GET'
            }
        }
    }
    
    class MockContext:
        function_name = "test-function"
        memory_limit_in_mb = 128
        invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test"
        aws_request_id = "test-request-id"
    
    # Call handler
    response = handler(event, MockContext())
    
    # Assertions
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert 'data' in body
    assert isinstance(body['data'], list)


@mock_aws
def test_get_nonexistent_representative():
    """Test getting a representative that doesn't exist"""
    # Setup mock DynamoDB
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.create_table(
        TableName='test-representatives',
        KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
        BillingMode='PAY_PER_REQUEST'
    )
    
    # Create test event
    event = {
        'version': '2.0',
        'routeKey': 'GET /api/representatives/123',
        'rawPath': '/api/representatives/123e4567-e89b-12d3-a456-426614174000',
        'requestContext': {
            'http': {
                'method': 'GET'
            }
        }
    }
    
    class MockContext:
        function_name = "test-function"
        memory_limit_in_mb = 128
        invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test"
        aws_request_id = "test-request-id"
    
    # Call handler
    response = handler(event, MockContext())
    
    # Assertions
    assert response['statusCode'] == 404
    body = json.loads(response['body'])
    assert 'errors' in body
    assert len(body['errors']) > 0
