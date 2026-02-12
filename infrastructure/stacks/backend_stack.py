"""
Backend infrastructure stack for Represent App
"""
import aws_cdk as cdk
from aws_cdk import (
    aws_dynamodb as ddb,
    aws_lambda,
    aws_apigatewayv2 as apigw2,
    aws_apigatewayv2_integrations as apigw2_int,
    aws_logs,
    aws_ssm as ssm,
    aws_iam as iam
)
import os


class BackendStack(cdk.Stack):
    """Infrastructure for Represent App Backend"""
    
    def __init__(self, scope: cdk.App, stack_id: str, env_name: str, **kwargs):
        super().__init__(scope, stack_id, **kwargs)
        
        # Parameter Store API Keys Configuration
        # Note: Parameters must be created manually before deployment:
        # aws ssm put-parameter --name "/represent-app/google-maps-api-key" \
        #     --value "YOUR_KEY" --type "SecureString" --overwrite
        # aws ssm put-parameter --name "/represent-app/openstates-api-key" \
        #     --value "YOUR_KEY" --type "SecureString" --overwrite
        
        # DynamoDB Table
        table = ddb.Table(
            self,
            f"{stack_id}-RepresentativesTable",
            partition_key=ddb.Attribute(
                name='id',
                type=ddb.AttributeType.STRING
            ),
            billing_mode=ddb.BillingMode.PAY_PER_REQUEST,
            removal_policy=cdk.RemovalPolicy.DESTROY if env_name == 'dev' else cdk.RemovalPolicy.RETAIN,
            stream=ddb.StreamViewType.NEW_AND_OLD_IMAGES  # Enable streams for future event handling
        )
        
        # Lambda Layer with dependencies
        dependencies_layer = aws_lambda.LayerVersion(
            self,
            f"{stack_id}-DependenciesLayer",
            code=aws_lambda.Code.from_asset("../backend/layers"),
            compatible_runtimes=[aws_lambda.Runtime.PYTHON_3_9],
            description="Python dependencies for Represent App API"
        )
        
        # Lambda Function with Tenant Isolation
        # Each state/county gets isolated execution environments
        api_lambda = aws_lambda.Function(
            self,
            f"{stack_id}-ApiHandler",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler="src.handlers.address_lookup.lambda_handler",
            code=aws_lambda.Code.from_asset("../backend"),
            layers=[dependencies_layer],
            timeout=cdk.Duration.seconds(30),
            memory_size=512,
            environment={
                "DDB_TABLE_NAME": table.table_name,
                "LOG_LEVEL": "INFO",
                "POWERTOOLS_SERVICE_NAME": "represent-api",
                "POWERTOOLS_METRICS_NAMESPACE": "RepresentApp",
                "POWERTOOLS_LOG_LEVEL": "INFO"
            },
            tracing=aws_lambda.Tracing.ACTIVE  # Enable X-Ray tracing
        )
        
        # Grant Lambda permissions to DynamoDB
        table.grant_read_write_data(api_lambda)
        
        # Grant Lambda permissions to Parameter Store for API keys
        api_lambda.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "ssm:GetParameter",
                    "ssm:GetParameters"
                ],
                resources=[
                    f"arn:aws:ssm:{self.region}:{self.account}:parameter/represent-app/google-maps-api-key",
                    f"arn:aws:ssm:{self.region}:{self.account}:parameter/represent-app/openstates-api-key"
                ]
            )
        )
        
        # Additional IAM permissions for Parameter Store operations
        api_lambda.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "ssm:DescribeParameters"
                ],
                resources=["*"]  # DescribeParameters requires wildcard
            )
        )
        
        # HTTP API Gateway
        http_api = apigw2.HttpApi(
            self,
            f"{stack_id}-HttpApi",
            create_default_stage=True,
            cors_preflight=apigw2.CorsPreflightOptions(
                allow_methods=[apigw2.CorsHttpMethod.ANY],
                allow_origins=[
                    "http://localhost:5173",  # Local development
                    "http://localhost:4173",  # Vite preview
                    "https://d2x31oul4x7uo0.cloudfront.net"  # Production CloudFront
                ],
                allow_headers=["Content-Type", "X-Amz-Date", "Authorization", "X-Api-Key", "X-Amz-Security-Token"],
                allow_credentials=False,
                max_age=cdk.Duration.hours(1)
            )
        )
        
        # Lambda Integration
        integration = apigw2_int.HttpLambdaIntegration(
            f"{stack_id}-Integration",
            api_lambda
        )
        
        # Add routes
        http_api.add_routes(
            path="/api/{proxy+}",
            methods=[
                apigw2.HttpMethod.GET,
                apigw2.HttpMethod.POST,
                apigw2.HttpMethod.PUT,
                apigw2.HttpMethod.PATCH,
                apigw2.HttpMethod.DELETE
            ],
            integration=integration
        )
        
        # CloudWatch Log Group for API logs
        log_group = aws_logs.LogGroup(
            self,
            f"{stack_id}-ApiLogs",
            log_group_name=f"/aws/lambda/{api_lambda.function_name}",
            retention=aws_logs.RetentionDays.ONE_WEEK if env_name == 'dev' else aws_logs.RetentionDays.ONE_MONTH
        )
        
        # Outputs
        cdk.CfnOutput(
            self,
            "ApiUrl",
            value=http_api.url,
            description="HTTP API Gateway URL"
        )
        
        cdk.CfnOutput(
            self,
            "TableName",
            value=table.table_name,
            description="DynamoDB Table Name"
        )
        
        cdk.CfnOutput(
            self,
            "LambdaArn",
            value=api_lambda.function_arn,
            description="Lambda Function ARN"
        )
