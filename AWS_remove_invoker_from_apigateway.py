import boto3
import os


import boto3

kms_client = boto3.client("kms")

if not os.environ.get("AWS_EXECUTION_ENV") is None:
    domain_name = os.environ["domain_name"]
    prefix_name = os.environ["prefix_name"]
    sufix_name = os.environ["sufix_name"]
    region = os.environ["region"]


apigateway_client = boto3.client("apigatewayv2")
get_apis_response = apigateway_client.get_apis()
for api in get_apis_response["Items"]:
    get_integrations_response = apigateway_client.get_integrations(ApiId=api["ApiId"])
    for integration in get_integrations_response["Items"]:
        if not "invoker" in integration["IntegrationUri"]:
            project_integration_id = integration["IntegrationId"]

    get_routes_response = apigateway_client.get_routes(ApiId=api["ApiId"])
    for route in get_routes_response["Items"]:
        delete_route_response = apigateway_client.delete_route(ApiId=api["ApiId"], RouteId=route["RouteId"])

    create_route_response = apigateway_client.create_route(ApiId=api["ApiId"], RouteKey="ANY /{page}/{action}/{params}", Target="integrations/" + project_integration_id)
    create_route_response = apigateway_client.create_route(ApiId=api["ApiId"], RouteKey="ANY /{page}/{action}", Target="integrations/" + project_integration_id)
    create_route_response = apigateway_client.create_route(ApiId=api["ApiId"], RouteKey="ANY /{page}", Target="integrations/" + project_integration_id)
    create_route_response = apigateway_client.create_route(ApiId=api["ApiId"], RouteKey="ANY /", Target="integrations/" + project_integration_id)

print("Routes Changed!")
