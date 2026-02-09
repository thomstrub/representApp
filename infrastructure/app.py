#!/usr/bin/env python3
"""
CDK App for Represent App Infrastructure
"""
import os
import aws_cdk as cdk
from stacks.backend_stack import BackendStack

app = cdk.App()

# Get environment configuration
env_name = os.getenv('ENVIRONMENT', 'dev')
aws_account = os.getenv('CDK_DEFAULT_ACCOUNT')
aws_region = os.getenv('CDK_DEFAULT_REGION', 'us-east-1')

# Create stack
BackendStack(
    app,
    f"RepresentApp-{env_name}",
    env=cdk.Environment(account=aws_account, region=aws_region),
    env_name=env_name
)

app.synth()
