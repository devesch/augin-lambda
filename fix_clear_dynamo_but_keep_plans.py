from utils.AWS.Dynamo import Dynamo

all_items = Dynamo().execute_scan()

for item in all_items:
    if not item.get("entity"):
        Dynamo().delete_entity(item)
    elif item.get("entity") != "plan":
        Dynamo().delete_entity(item)
