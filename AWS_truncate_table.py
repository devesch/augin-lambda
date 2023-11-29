import boto3
import concurrent.futures


def delete_item(table, item):
    table.delete_item(Key={"pk": item["pk"], "sk": item["sk"]})


def truncate_table(table_name):
    # Initialize a DynamoDB client
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    table = dynamodb.Table(table_name)

    # Initialize the scan
    response = table.scan()
    items = response["Items"]

    while "LastEvaluatedKey" in response:
        response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        items.extend(response["Items"])

    print("Scan completed")
    # Use ThreadPoolExecutor to delete items in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(delete_item, table, item) for item in items]
        concurrent.futures.wait(futures)


truncate_table("device_manager")
