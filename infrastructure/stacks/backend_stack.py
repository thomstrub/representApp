"""
Backend infrastructure stack for Represent App
"""
from aws_cdk import (
    core,
    aws_dynamodb as ddb,
    aws_lambda,
    aws_apigatewayv2 as apigw2,
    aws_apigatewayv2_integrations as apigw2_int,
    aws_logs
)
import os


class BackendStack(core.Stack):
    """Infrastructure for Represent App Backend"""
    
    def __init__(self, scope: core.Construct, stack_id: str, env_name: str, **kwargs):
        super().__init__(scope, stack_id, **kwargs)
        
        # DynamoDB Table
        table = ddb.Table(
            self,
            f"{stack_id}-RepresentativesTable",
            partition_key=ddb.Attribute(
                name='id',
                type=ddb.AttributeType.STRING
            ),
            billing_mode=ddb.BillingMode.PAY_PER_REQUEST,
            removal_policy=core.RemovalPolicy.DESTROY if env_name == 'dev' else core.RemovalPolicy.RETAIN,
            stream=ddb.StreamViewType.NEW_AND_OLD_IMAGES  # Enable streams for future event handling
        )
        
        # Lambda Function with Tenant Isolation
        # Each state/county gets isolated execution environments
        api_lambda = aws_lambda.Function(
            self,
            f"{stack_id}-ApiHandler",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler="handlers.api.handler",
            code=aws_lambda.Code.from_asset("../backend/src"),
            timeout=core.Duration.seconds(30),
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
        
        # Enable tenant isolation mode for multi-tenant support
        # Note: This must be set at creation time and cannot be changed later
        cfn_function = api_lambda.node.default_child
        cfn_function.add_property_override(
            "TenancyConfig",
            {"TenantIsolationMode": "PER_TENANT"}
        )
        
        # Grant Lambda permissions to DynamoDB
        table.grant_read_write_data(api_lambda)
        
        # HTTP API Gateway
        http_api = apigw2.HttpApi(
            self,
            f"{stack_id}-HttpApi",
            create_default_stage=True,
            cors_preflight=apigw2.CorsPreflightOptions(
                allow_methods=[apigw2.CorsHttpMethod.ANY],
                allow_origins=["*"],  # TODO: Configure appropriately for production
                allow_headers=["*"]
            )
        )
        
        # Lambda Integration with Tenant ID header mapping
        # Maps x-tenant-id from client request to X-Amz-Tenant-Id for Lambda
        integration = apigw2_int.HttpLambdaIntegration(
            f"{stack_id}-Integration",
            api_lambda,
            parameter_mapping=apigw2.ParameterMapping().append_header(
                "X-Amz-Tenant-Id",
                apigw2.MappingValue.request_header("x-tenant-id")
            )
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
        core.CfnOutput(
            self,
            "ApiUrl",
            value=http_api.url,
            description="HTTP API Gateway URL"
        )
        
        core.CfnOutput(
            self,
            "TableName",
            value=table.table_name,
            description="DynamoDB Table Name"
        )
        
        core.CfnOutput(
            self,
            "LambdaArn",
            value=api_lambda.function_arn,
            description="Lambda Function ARN"
        )
