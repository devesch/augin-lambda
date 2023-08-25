import boto3
import os

lambda_routes = []
html_source_path = os.getcwd().replace("\\", "/") + "/src/html"
for sub_dirs in os.listdir(html_source_path):
    if sub_dirs[0] != ".":
        lambda_routes.append(sub_dirs)

waf_client = boto3.client("wafv2", region_name="us-east-1")  # Create a WAF client

# Call WAF client to list web ACLs
list_web_acls_response = waf_client.list_web_acls(Scope="CLOUDFRONT")  # Change to CLOUDFRONT if you're working with CloudFront web ACLs
get_web_acl_response = waf_client.get_web_acl(Name=list_web_acls_response["WebACLs"][1]["Name"], Scope="CLOUDFRONT", Id=list_web_acls_response["WebACLs"][1]["Id"])
# list_available_managed_rule_groups_response = waf_client.list_available_managed_rule_groups(Scope="CLOUDFRONT")

# list_rule_groups_response = waf_client.list_rule_groups(Scope="CLOUDFRONT")


default_route = get_web_acl_response["WebACL"]["Rules"][0]["Statement"]["OrStatement"]["Statements"][1]


for route in lambda_routes:
    import copy

    new_route = copy.deepcopy(default_route)
    new_route["ByteMatchStatement"]["SearchString"] = ("/" + route).encode()
    get_web_acl_response["WebACL"]["Rules"][0]["Statement"]["OrStatement"]["Statements"].append(new_route)


update_web_acl_response = waf_client.update_web_acl(
    Name=get_web_acl_response["WebACL"]["Name"],
    Scope="CLOUDFRONT",
    Id=get_web_acl_response["WebACL"]["Id"],
    DefaultAction=get_web_acl_response["WebACL"]["DefaultAction"],
    Description="augin",
    Rules=get_web_acl_response["WebACL"]["Rules"],
    VisibilityConfig=get_web_acl_response["WebACL"]["VisibilityConfig"],
    LockToken=get_web_acl_response["LockToken"],
)


print("end")
