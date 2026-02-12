"""
Main API Lambda handler with routing
"""

import os
import json
from typing import Dict, Any
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEventV2
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.parser import parse

from src.models.domain import Representative
from src.models.store import RepresentativeStore
from src.models.base import Response, APIError

# Configuration
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
TABLE_NAME = os.environ.get("DDB_TABLE_NAME", "representatives")

logger = Logger(service="represent-api", level=LOG_LEVEL)
store = None


@logger.inject_lambda_context(log_event=True)
def handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    """
    Main Lambda handler for API Gateway events
    Routes requests to appropriate CRUD operations

    Multi-Tenant Support:
    - Tenant ID (state/county) is automatically available in context.tenant_id
    - Each tenant gets isolated execution environments
    - Tenant-specific data cached in memory is isolated per tenant
    """
    global store

    # Extract tenant ID from Lambda context (available with tenant isolation mode)
    tenant_id = getattr(context, "tenant_id", None)

    # Log tenant context for observability
    if tenant_id:
        logger.info(f"Processing request for tenant: {tenant_id}")

    # Initialize store connection (tenant-specific connection can be cached)
    if store is None:
        store = RepresentativeStore(TABLE_NAME)

    # Parse API Gateway event
    api_event: APIGatewayProxyEventV2 = APIGatewayProxyEventV2(event)
    http_method = api_event.request_context.http.method
    path = api_event.raw_path

    response = Response()

    try:
        # Route based on path and method
        if "/representatives" in path:
            response = route_representatives(api_event, http_method, store)
        else:
            error = APIError(status=404, title="Not Found", detail=f"Path {path} not found")
            response.add_error(error)

    except Exception as e:
        logger.exception("Unhandled error in handler")
        error = APIError(status=500, title="Internal Server Error", detail=str(e))
        response.add_error(error)

    return response.dump()


def route_representatives(
    event: APIGatewayProxyEventV2, method: str, store: RepresentativeStore
) -> Response:
    """Route requests for /representatives endpoint"""

    response = Response()

    # Extract ID from path if present
    path_parts = event.raw_path.strip("/").split("/")
    rep_id = path_parts[-1] if len(path_parts) > 1 and path_parts[-1] != "representatives" else None

    try:
        if method == "POST":
            # Create new representative
            body = json.loads(event.body) if event.body else {}
            representative = parse(event=body, model=Representative)
            response = store.create(representative)

        elif method == "GET":
            if rep_id:
                # Get single representative
                response = store.get(rep_id)
            else:
                # List all representatives
                response = store.list_all()

        elif method == "PUT" or method == "PATCH":
            # Update representative
            body = json.loads(event.body) if event.body else {}
            if rep_id:
                body["id"] = rep_id
            representative = parse(event=body, model=Representative)
            response = store.update(representative)

        elif method == "DELETE":
            if rep_id:
                # Delete representative
                response = store.delete(rep_id)
            else:
                error = APIError(
                    status=400, title="Bad Request", detail="ID required for DELETE operation"
                )
                response.add_error(error)
        else:
            error = APIError(
                status=405, title="Method Not Allowed", detail=f"Method {method} not supported"
            )
            response.add_error(error)

    except Exception as e:
        logger.exception(f"Error in route_representatives: {e}")
        error = APIError(status=500, title="Internal Server Error", detail=str(e))
        response.add_error(error)

    return response
