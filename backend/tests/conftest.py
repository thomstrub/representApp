"""
Test configuration and fixtures
"""
import pytest
import os

# Set test environment variables
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
os.environ['DDB_TABLE_NAME'] = 'test-representatives'
os.environ['LOG_LEVEL'] = 'DEBUG'
