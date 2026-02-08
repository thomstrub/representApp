"""
Test configuration and fixtures
"""
import pytest
import os
import sys
from pathlib import Path

# Add src directory to Python path
backend_dir = Path(__file__).parent.parent
src_dir = backend_dir / 'src'
sys.path.insert(0, str(src_dir))

# Set test environment variables
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
os.environ['DDB_TABLE_NAME'] = 'test-representatives'
os.environ['LOG_LEVEL'] = 'DEBUG'
