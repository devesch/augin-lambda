from boto3 import client
import uuid

cloudfront_client = client("cloudfront")

# def get_invalidation(distribution_id):
#     response = cloudfront_client.get_invalidation(
#         DistributionId=distribution_id,
#         Id='I601OHI9JSC9560RCQIP5A3OE0'
#     )
#     return response


def create_invalidation(distribution_id):
    response = cloudfront_client.create_invalidation(
        DistributionId=distribution_id,
        InvalidationBatch={
            "Paths": {
                "Quantity": 1,
                "Items": [
                    "/*",
                ],
            },
            "CallerReference": str(uuid.uuid4()),
        },
    )
    return


list_distributions_response = cloudfront_client.list_distributions()
for distribution in list_distributions_response["DistributionList"]["Items"]:
    if "AliasICPRecordals" in distribution:
        if "integratebim" in distribution["AliasICPRecordals"][0]["CNAME"]:
            if "cdn.augin" in distribution["AliasICPRecordals"][0]["CNAME"] or "upload.augin" in distribution["AliasICPRecordals"][0]["CNAME"]:
                print("Invalidating " + distribution["AliasICPRecordals"][0]["CNAME"])
                create_invalidation(distribution["Id"])

print("Invalidations completed")
