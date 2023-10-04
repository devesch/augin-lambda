from utils.AWS.Dynamo import Dynamo

all_devices = Dynamo().query_entity("device")

for item in all_devices:
    Dynamo().delete_entity(item)
