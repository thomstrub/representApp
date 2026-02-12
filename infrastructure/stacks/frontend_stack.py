"""Frontend Stack for Represent App - S3 + CloudFront deployment."""
from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_s3_deployment as s3deploy,
    RemovalPolicy,
    CfnOutput,
    Duration,
)
from constructs import Construct
import os


class FrontendStack(Stack):
    """CDK Stack for frontend hosting using S3 and CloudFront."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        """Initialize the FrontendStack.
        
        Args:
            scope: CDK app scope
            construct_id: Unique identifier for this stack
            **kwargs: Additional stack properties
        """
        super().__init__(scope, construct_id, **kwargs)

        # S3 bucket for frontend hosting
        frontend_bucket = s3.Bucket(
            self,
            "FrontendBucket",
            website_index_document="index.html",
            website_error_document="index.html",  # SPA routing support
            public_read_access=True,
            block_public_access=s3.BlockPublicAccess(
                block_public_policy=False,
                block_public_acls=False,
                ignore_public_acls=False,
                restrict_public_buckets=False,
            ),
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        # CloudFront distribution
        distribution = cloudfront.Distribution(
            self,
            "FrontendDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3StaticWebsiteOrigin(frontend_bucket),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED,
            ),
            default_root_object="index.html",
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path="/index.html",
                    ttl=Duration.seconds(0),
                )
            ],
        )

        # Deploy frontend build to S3
        frontend_build_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "frontend", "dist"
        )

        s3deploy.BucketDeployment(
            self,
            "DeployFrontend",
            sources=[s3deploy.Source.asset(frontend_build_path)],
            destination_bucket=frontend_bucket,
            distribution=distribution,
            distribution_paths=["/*"],
        )

        # Stack outputs
        CfnOutput(
            self,
            "CloudFrontUrl",
            value=f"https://{distribution.distribution_domain_name}",
            description="Frontend CloudFront URL",
        )

        CfnOutput(
            self,
            "S3BucketName",
            value=frontend_bucket.bucket_name,
            description="Frontend S3 bucket name",
        )
