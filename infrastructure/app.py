#!/usr/bin/env python3
"""
CDK App for Represent App Infrastructure
"""
import os
from aws_cdk import core
from stacks.backend_stack import BackendStack

app = core.App()

# Get environment configuration
env_name = os.getenv('ENVIRONMENT', 'dev')
aws_account = os.getenv('CDK_DEFAULT_ACCOUNT')
aws_region = os.getenv('CDK_DEFAULT_REGION', 'us-east-1')

# Create stack
BackendStack(
    app,
    f"RepresentApp-{env_name}",
    env=core.Environment(account=aws_account, region=aws_region),
    env_name=env_name
)

app.synth()
