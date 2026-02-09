"""
Test configuration and fixtures
"""
import pytest
import os
import sys
from pathlib import Path

# Add backend directory to Python path so 'src' module can be imported
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Set test environment variables
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
os.environ['DDB_TABLE_NAME'] = 'test-representatives'
os.environ['LOG_LEVEL'] = 'DEBUG'
