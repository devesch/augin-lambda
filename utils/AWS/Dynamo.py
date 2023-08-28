from utils.Config import lambda_constants

from boto3 import client, resource
from botocore.config import Config
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer


my_config = Config(retries={"max_attempts": 50, "mode": "adaptive"})

dynamodb_client = client("dynamodb", region_name=lambda_constants["region"])
table = resource("dynamodb", region_name=lambda_constants["region"], config=my_config).Table(lambda_constants["table_project"])


class Dynamo:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Dynamo, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    # def update_dynamo_constants(self):
    #     from utils.Config import lambda_constants

    #     global table
    #     global dynamodb_client

    #     dynamodb_client = client("dynamodb", region_name=lambda_constants["region"])
    #     table = resource("dynamodb", region_name=lambda_constants["region"], config=my_config).Table(lambda_constants["table_project"])

    ### USER ###
    def get_user(self, user_email):
        return self.execute_get_item({"TableName": lambda_constants["table_project"], "Key": {"pk": {"S": "user#" + user_email}, "sk": {"S": "user#" + user_email}}})

    def query_paginated_all_last_login_users(self, last_evaluated_key=None, limit=20):
        key_schema = {"entity": {"S": "user"}, "sk": {"S": ""}, "user_last_login_at": {"S": ""}, "pk": {"S": ""}}
        query, last_evaluated_key = self.execute_paginated_query({"TableName": lambda_constants["table_project"], "IndexName": "entity-user_last_login_at-index", "KeyConditionExpression": "#bef90 = :bef90", "ExpressionAttributeNames": {"#bef90": "entity"}, "ExpressionAttributeValues": {":bef90": {"S": "user"}}}, limit, last_evaluated_key, key_schema)
        return self.execute_batch_get_item(query), last_evaluated_key

    def get_auth_token(self, user_auth_token):
        return self.execute_get_item({"TableName": lambda_constants["table_project"], "Key": {"pk": {"S": "auth#" + str(user_auth_token)}, "sk": {"S": "auth#" + str(user_auth_token)}}})

    def query_users_auth_token(self, user_email):
        return self.execute_query({"TableName": lambda_constants["table_project"], "IndexName": "auth_user_email-created_at-index", "KeyConditionExpression": "#bef90 = :bef90", "ExpressionAttributeNames": {"#bef90": "auth_user_email"}, "ExpressionAttributeValues": {":bef90": {"S": user_email}}})

    def get_verify_email(self, user_email, verify_email_code):
        return self.execute_get_item({"TableName": lambda_constants["table_project"], "Key": {"pk": {"S": "user#" + user_email}, "sk": {"S": "verify_email#" + verify_email_code}}})

    def query_users_verify_email(self, user_email):
        return self.execute_query({"TableName": lambda_constants["table_project"], "KeyConditionExpression": "#bef90 = :bef90 And begins_with(#bef91, :bef91)", "ExpressionAttributeNames": {"#bef90": "pk", "#bef91": "sk"}, "ExpressionAttributeValues": {":bef90": {"S": "user#" + user_email}, ":bef91": {"S": "verify_email#"}}})

    ### BACKOFFICE ###
    def get_backoffice_data(self):
        return self.execute_get_item({"TableName": lambda_constants["table_project"], "Key": {"pk": {"S": "backoffice#"}, "sk": {"S": "backoffice#"}}})

    ### MODEL ###
    def get_model(self, user_email, model_id):
        return self.execute_get_item({"TableName": lambda_constants["table_project"], "Key": {"pk": {"S": "user#" + user_email}, "sk": {"S": "model#" + model_id}}})

    def get_model_by_id(self, model_id):
        query = self.execute_query({"TableName": lambda_constants["table_project"], "IndexName": "sk-pk-index", "KeyConditionExpression": "#0b430 = :0b430", "ExpressionAttributeNames": {"#0b430": "sk"}, "ExpressionAttributeValues": {":0b430": {"S": "model#" + model_id}}})
        if query:
            return self.get_entity(query[0]["pk"], query[0]["sk"])
        return None

    def query_user_models_from_state(self, user, model_state):
        query = []
        query.extend(self.execute_query({"TableName": lambda_constants["table_project"], "KeyConditionExpression": "#d8ac1 = :d8ac1", "ExpressionAttributeNames": {"#d8ac1": "pk"}, "ExpressionAttributeValues": {":d8ac1": {"S": "user#" + user.user_email + "#model_state#" + model_state}}}))
        if user.user_is_tqs:
            if user.user_tqs_customers:
                for customer in user.user_tqs_customers:
                    query.extend(self.execute_query({"TableName": lambda_constants["table_project"], "KeyConditionExpression": "#d8ac1 = :d8ac1", "ExpressionAttributeNames": {"#d8ac1": "pk"}, "ExpressionAttributeValues": {":d8ac1": {"S": "user#" + customer["id"] + "#model_state#" + model_state}}}))
        return query

    def query_user_last_created_models(self, user, limit=10000):
        query = []
        new_items, last_evaluated_key = self.query_paginated_user_models_by_created_at(user.user_email, "completed", last_evaluated_key=None, limit=limit)
        query.extend(new_items)
        if user.user_is_tqs:
            if user.user_tqs_customers:
                for customer in user.user_tqs_customers:
                    new_items, last_evaluated_key = self.query_paginated_user_models_by_created_at(customer["id"], "completed", last_evaluated_key=None, limit=limit)
                    query.extend(new_items)
        return query

    def query_paginated_user_models_by_name(self, user_email, model_state, last_evaluated_key=None, limit=20, reverse=False):
        key_schema = {"model_name": {"S": ""}, "sk": {"S": ""}, "pk": {"S": ""}}
        query, last_evaluated_key = self.execute_paginated_query({"TableName": lambda_constants["table_project"], "IndexName": "pk-model_name-index", "KeyConditionExpression": "#bef90 = :bef90", "ExpressionAttributeNames": {"#bef90": "pk"}, "ExpressionAttributeValues": {":bef90": {"S": "user#" + user_email + "#model_state#" + model_state}}}, limit, last_evaluated_key, key_schema, reverse=reverse)
        return self.execute_batch_get_item(query), last_evaluated_key

    def query_paginated_user_models_by_created_at(self, user_email, model_state, last_evaluated_key=None, limit=20, reverse=False):
        key_schema = {"created_at": {"S": ""}, "sk": {"S": ""}, "pk": {"S": ""}}
        query, last_evaluated_key = self.execute_paginated_query({"TableName": lambda_constants["table_project"], "IndexName": "pk-created_at-index", "KeyConditionExpression": "#bef90 = :bef90", "ExpressionAttributeNames": {"#bef90": "pk"}, "ExpressionAttributeValues": {":bef90": {"S": "user#" + user_email + "#model_state#" + model_state}}}, limit, last_evaluated_key, key_schema, reverse=reverse)
        return self.execute_batch_get_item(query), last_evaluated_key

    ### PROJECT ###

    def get_project(self, project_id):
        return self.execute_get_item({"TableName": lambda_constants["table_web_data"], "Key": {"pk": {"S": "proj#" + project_id}, "sk": {"S": "proj#" + project_id}}})

    def get_site(self, project_id, site_id):
        return self.execute_get_item({"TableName": lambda_constants["table_web_data"], "Key": {"pk": {"S": "proj#" + project_id + "#site"}, "sk": {"S": "site#" + site_id}}})

    def get_building(self, project_id, building_id):
        query = self.execute_query({"TableName": lambda_constants["table_web_data"], "IndexName": "sk-pk-index", "KeyConditionExpression": "#e7110 = :e7110", "ExpressionAttributeNames": {"#e7110": "sk"}, "ExpressionAttributeValues": {":e7110": {"S": "building#" + building_id}}}, ScanIndexForward=False)
        if query:
            return self.get_entity(query[0]["pk"], query[0]["sk"], table=lambda_constants["table_web_data"])

    def get_storey(self, project_id, storey_id):
        query = self.execute_query({"TableName": lambda_constants["table_web_data"], "IndexName": "sk-pk-index", "KeyConditionExpression": "#e7110 = :e7110", "ExpressionAttributeNames": {"#e7110": "sk"}, "ExpressionAttributeValues": {":e7110": {"S": "storey#" + storey_id}}}, ScanIndexForward=False)
        if query:
            return self.get_entity(query[0]["pk"], query[0]["sk"], table=lambda_constants["table_web_data"])

    def query_sites(self, project_id):
        return self.execute_query({"TableName": lambda_constants["table_web_data"], "KeyConditionExpression": "#e7110 = :e7110", "ExpressionAttributeNames": {"#e7110": "pk"}, "ExpressionAttributeValues": {":e7110": {"S": "proj#" + project_id + "#site"}}}, ScanIndexForward=False)

    def query_buildings(self, project_id, site_id):
        return self.execute_query({"TableName": lambda_constants["table_web_data"], "KeyConditionExpression": "#e7110 = :e7110", "ExpressionAttributeNames": {"#e7110": "pk"}, "ExpressionAttributeValues": {":e7110": {"S": "proj#" + project_id + "#site#" + site_id + "#building"}}}, ScanIndexForward=False)

    def query_storeys(self, project_id, site_id, building_id):
        return self.execute_query({"TableName": lambda_constants["table_web_data"], "KeyConditionExpression": "#e7110 = :e7110", "ExpressionAttributeNames": {"#e7110": "pk"}, "ExpressionAttributeValues": {":e7110": {"S": "proj#" + project_id + "#site#" + site_id + "#building#" + building_id + "#storey"}}}, ScanIndexForward=False)

    def query_categorys(self, project_id, site_id, building_id, storey_id):
        return self.execute_query({"TableName": lambda_constants["table_web_data"], "KeyConditionExpression": "#e7110 = :e7110", "ExpressionAttributeNames": {"#e7110": "pk"}, "ExpressionAttributeValues": {":e7110": {"S": "proj#" + project_id + "#site#" + site_id + "#building#" + building_id + "#storey#" + storey_id + "#category"}}}, ScanIndexForward=False)

    def get_element(self, project_id, element_id):
        query = self.execute_query({"TableName": lambda_constants["table_web_data"], "IndexName": "sk-pk-index", "KeyConditionExpression": "#e7110 = :e7110", "ExpressionAttributeNames": {"#e7110": "sk"}, "ExpressionAttributeValues": {":e7110": {"S": "proj#" + project_id + "#element#" + element_id}}}, ScanIndexForward=False)
        if query:
            return self.get_entity(query[0]["pk"], query[0]["sk"], table=lambda_constants["table_web_data"])

    def get_sub_element(self, project_id, sub_element_id):
        query = self.execute_query({"TableName": lambda_constants["table_web_data"], "IndexName": "sk-pk-index", "KeyConditionExpression": "#e7110 = :e7110", "ExpressionAttributeNames": {"#e7110": "sk"}, "ExpressionAttributeValues": {":e7110": {"S": "proj#" + project_id + "#sub_element#" + sub_element_id}}}, ScanIndexForward=False)
        if query:
            return self.get_entity(query[0]["pk"], query[0]["sk"], table=lambda_constants["table_web_data"])

    def get_sub_sub_element(self, project_id, sub_sub_element_id):
        query = self.execute_query({"TableName": lambda_constants["table_web_data"], "IndexName": "sk-pk-index", "KeyConditionExpression": "#e7110 = :e7110", "ExpressionAttributeNames": {"#e7110": "sk"}, "ExpressionAttributeValues": {":e7110": {"S": "proj#" + project_id + "#sub_sub_element#" + sub_sub_element_id}}}, ScanIndexForward=False)
        if query:
            return self.get_entity(query[0]["pk"], query[0]["sk"], table=lambda_constants["table_web_data"])

    def get_nano_element(self, project_id, nano_element_id):
        query = self.execute_query({"TableName": lambda_constants["table_web_data"], "IndexName": "sk-pk-index", "KeyConditionExpression": "#e7110 = :e7110", "ExpressionAttributeNames": {"#e7110": "sk"}, "ExpressionAttributeValues": {":e7110": {"S": "proj#" + project_id + "#nano_element#" + nano_element_id}}}, ScanIndexForward=False)
        if query:
            return self.get_entity(query[0]["pk"], query[0]["sk"], table=lambda_constants["table_web_data"])

    def query_elements(self, project_id, site_id, building_id, storey_id, category_id):
        return self.execute_query({"TableName": lambda_constants["table_web_data"], "KeyConditionExpression": "#e7110 = :e7110", "ExpressionAttributeNames": {"#e7110": "pk"}, "ExpressionAttributeValues": {":e7110": {"S": "proj#" + project_id + "#site#" + site_id + "#building#" + building_id + "#storey#" + storey_id + "#category#" + category_id + "#element"}}}, ScanIndexForward=False)

    def get_property(self, project_id, property_id):
        return self.execute_get_item({"TableName": lambda_constants["table_web_data"], "Key": {"pk": {"S": "proj#" + project_id + "#property#" + property_id}, "sk": {"S": "property#" + property_id}}})

    def query_sub_elements(self, project_id, site_id, building_id, storey_id, category_id, element_id):
        return self.execute_query({"TableName": lambda_constants["table_web_data"], "KeyConditionExpression": "#e7110 = :e7110", "ExpressionAttributeNames": {"#e7110": "pk"}, "ExpressionAttributeValues": {":e7110": {"S": "proj#" + project_id + "#site#" + site_id + "#building#" + building_id + "#storey#" + storey_id + "#category#" + category_id + "#element#" + element_id + "#sub_element"}}}, ScanIndexForward=False)

    def query_sub_sub_elements(self, project_id, site_id, building_id, storey_id, category_id, element_id, sub_element_id):
        return self.execute_query({"TableName": lambda_constants["table_web_data"], "KeyConditionExpression": "#e7110 = :e7110", "ExpressionAttributeNames": {"#e7110": "pk"}, "ExpressionAttributeValues": {":e7110": {"S": "proj#" + project_id + "#site#" + site_id + "#building#" + building_id + "#storey#" + storey_id + "#category#" + category_id + "#element#" + element_id + "#sub_element#" + sub_element_id + "#sub_sub_element"}}}, ScanIndexForward=False)

    def query_nano_elements(self, project_id, site_id, building_id, storey_id, category_id, element_id, sub_element_id, sub_sub_element_id):
        return self.execute_query({"TableName": lambda_constants["table_web_data"], "KeyConditionExpression": "#e7110 = :e7110", "ExpressionAttributeNames": {"#e7110": "pk"}, "ExpressionAttributeValues": {":e7110": {"S": "proj#" + project_id + "#site#" + site_id + "#building#" + building_id + "#storey#" + storey_id + "#category#" + category_id + "#element#" + element_id + "#sub_element#" + sub_element_id + "#sub_sub_element#" + sub_sub_element_id + "#nano_element"}}}, ScanIndexForward=False)

    def query_layer_global_ids(self, project_id, layer_id):
        return self.execute_query({"TableName": lambda_constants["table_web_data"], "KeyConditionExpression": "#e7110 = :e7110", "ExpressionAttributeNames": {"#e7110": "pk"}, "ExpressionAttributeValues": {":e7110": {"S": "proj#" + project_id + "#layer#" + layer_id}}}, ScanIndexForward=False)

    def query_global_ids_from_category(self, project_id, category_id):
        return self.execute_query({"TableName": lambda_constants["table_web_data"], "IndexName": "project_id_category-guid_id-index", "KeyConditionExpression": "#e7110 = :e7110", "ProjectionExpression": "#96c00", "ExpressionAttributeNames": {"#96c00": "guid_id", "#e7110": "project_id_category"}, "ExpressionAttributeValues": {":e7110": {"S": "proj#" + project_id + "#category#" + category_id}}}, ScanIndexForward=False)

    def query_global_ids_from_storey(self, project_id, storey_id):
        return self.execute_query({"TableName": lambda_constants["table_web_data"], "IndexName": "project_id_storey-guid_id-index", "KeyConditionExpression": "#e7110 = :e7110", "ProjectionExpression": "#96c00", "ExpressionAttributeNames": {"#96c00": "guid_id", "#e7110": "project_id_storey"}, "ExpressionAttributeValues": {":e7110": {"S": "proj#" + project_id + "#storey#" + storey_id}}}, ScanIndexForward=False)

    def get_batch_property(self, project_id, property_ids):
        query = []
        for property_id in property_ids:
            query.append({"pk": "proj#" + project_id + "#property#" + property_id, "sk": "property#" + property_id})
        return self.execute_batch_get_item(query, table=lambda_constants["table_web_data"])

    ### DEFAULT ###

    # def compress_python_obj(self, python_obj):
    #     compressed_python_obj = {}
    #     for param, value in python_obj.items():
    #         if "_" in param and param not in ignore_brotli_params:
    #             if not "data" in compressed_python_obj:
    #                 compressed_python_obj["data"] = {}
    #             compressed_python_obj["data"][param] = value
    #         else:
    #             compressed_python_obj[param] = value
    #     if "data" in compressed_python_obj:
    #         input_data = json.dumps(compressed_python_obj["data"]).encode("utf-8")
    #         compressed_data = brotli.compress(input_data)
    #         compressed_python_obj["data"] = compressed_data
    #     return compressed_python_obj

    # def decompress_python_obj(self, python_obj):
    #     decompressed_python_obj = {}
    #     decompressed_data = brotli.decompress(python_obj["data"].value)
    #     decompressed_data = json.loads(decompressed_data.decode())

    #     for param, value in python_obj.items():
    #         if not "_" in param or param in ignore_brotli_params:
    #             decompressed_python_obj[param] = value
    #     for param, value in decompressed_data.items():
    #         decompressed_python_obj[param] = value

    #     del decompressed_python_obj["data"]
    #     return decompressed_python_obj

    def dynamo_obj_to_python_obj(self, dynamo_obj: dict) -> dict:
        deserializer = TypeDeserializer()
        python_obj = {k: deserializer.deserialize(v) for k, v in dynamo_obj.items()}
        for attribute in python_obj:
            if str(type(python_obj[attribute])) == "<class 'decimal.Decimal'>":
                try:
                    python_obj[attribute] = int(python_obj[attribute])
                except:
                    python_obj[attribute] = float(python_obj[attribute])
        return python_obj

    def python_obj_to_dynamo_obj(self, python_obj: dict) -> dict:
        serializer = TypeSerializer()
        return {k: serializer.serialize(v) for k, v in python_obj.items()}

    def get_entity_from_crypto(self, crypto_entity):
        from dynamodb_encryption_sdk.encrypted.table import EncryptedTable
        from dynamodb_encryption_sdk.identifiers import CryptoAction
        from dynamodb_encryption_sdk.material_providers.aws_kms import AwsKmsCryptographicMaterialsProvider
        from dynamodb_encryption_sdk.structures import AttributeActions

        actions = AttributeActions(default_action=CryptoAction.ENCRYPT_AND_SIGN)
        aws_kms_cmp = AwsKmsCryptographicMaterialsProvider(key_id=lambda_constants["kms_key_id"])
        encrypted_table = EncryptedTable(table=table, materials_provider=aws_kms_cmp, attribute_actions=actions)
        return encrypted_table.get_item(Key=crypto_entity)

    def put_entity_into_crypto(self, crypto_entity):
        from dynamodb_encryption_sdk.encrypted.table import EncryptedTable
        from dynamodb_encryption_sdk.identifiers import CryptoAction
        from dynamodb_encryption_sdk.material_providers.aws_kms import AwsKmsCryptographicMaterialsProvider
        from dynamodb_encryption_sdk.structures import AttributeActions

        actions = AttributeActions(default_action=CryptoAction.ENCRYPT_AND_SIGN)
        aws_kms_cmp = AwsKmsCryptographicMaterialsProvider(key_id=lambda_constants["kms_key_id"])
        encrypted_table = EncryptedTable(table=table, materials_provider=aws_kms_cmp, attribute_actions=actions)
        return encrypted_table.put_item(Item=crypto_entity)

    def query_entity(self, entity, ScanIndexForward=False):
        query = self.execute_query({"TableName": lambda_constants["table_project"], "IndexName": "entity-created_at-index", "KeyConditionExpression": "#e7110 = :e7110", "ExpressionAttributeNames": {"#e7110": "entity"}, "ExpressionAttributeValues": {":e7110": {"S": entity}}}, ScanIndexForward=ScanIndexForward)
        return self.execute_batch_get_item(query)

    def query_pk(self, pk):
        return self.execute_query({"TableName": lambda_constants["table_project"], "KeyConditionExpression": "#e7110 = :e7110", "ExpressionAttributeNames": {"#e7110": "pk"}, "ExpressionAttributeValues": {":e7110": {"S": pk}}})

    def get_last_from_entity(self, entity):
        last_from_entity, last_evaluated_key = self.execute_paginated_query({"TableName": lambda_constants["table_project"], "IndexName": "entity-created_at-index", "KeyConditionExpression": "#bef90 = :bef90", "ExpressionAttributeNames": {"#bef90": "entity"}, "ExpressionAttributeValues": {":bef90": {"S": entity}}}, 1, None, None)
        if last_from_entity:
            return self.get_entity(last_from_entity[0]["pk"], last_from_entity[0]["sk"])
        return None

    def get_entity(self, pk=None, sk=None, table=None):
        if not table:
            table = lambda_constants["table_project"]
        return self.execute_get_item({"TableName": table, "Key": {"pk": {"S": pk}, "sk": {"S": sk}}})

    def put_entity(self, entity_dict, table=None):
        if not table:
            table = lambda_constants["table_project"]
        self.execute_put_item({"TableName": table, "Item": self.python_obj_to_dynamo_obj(entity_dict)})

    def update_entity(self, entity_dict, attribute, value, type="S"):
        if type == "N":
            value = str(value)
        return self.execute_update_item({"TableName": lambda_constants["table_project"], "Key": {"pk": {"S": str(entity_dict["pk"])}, "sk": {"S": str(entity_dict["sk"])}}, "UpdateExpression": "SET #75e20 = :75e20", "ExpressionAttributeNames": {"#75e20": attribute}, "ExpressionAttributeValues": {":75e20": {type: value}}})

    def update_entity_map(self, entity_dict, attribute, value):
        return self.execute_update_item({"TableName": lambda_constants["table_project"], "Key": {"pk": {"S": str(entity_dict["pk"])}, "sk": {"S": str(entity_dict["sk"])}}, "UpdateExpression": "SET #75e20 = :75e20", "ExpressionAttributeNames": {"#75e20": attribute}, "ExpressionAttributeValues": {":75e20": {"M": self.python_obj_to_dynamo_obj(value)}}})

    def put_dynamo_item_into_table(self, item):
        self.execute_put_item({"TableName": lambda_constants["table_project"], "Item": item})

    def delete_entity(self, entity_dict):
        self.execute_delete_item({"TableName": lambda_constants["table_project"], "Key": {"pk": {"S": str(entity_dict["pk"])}, "sk": {"S": str(entity_dict["sk"])}}})

    def execute_get_item(self, input):
        input["ReturnConsumedCapacity"] = "TOTAL"
        response = dynamodb_client.get_item(**input)
        print("Get_item Consumed Capacity:" + str(response["ConsumedCapacity"]["CapacityUnits"]))
        if "Item" in response:
            return self.dynamo_obj_to_python_obj(response["Item"])
        return None

    def execute_batch_get_item(self, input, table=None):
        if not table:
            table = lambda_constants["table_project"]
        filtered_response = []
        filtered_ordered_response = []
        if input:
            pagination = 99
            if len(input) > pagination:
                request_keys = []
                for index, key in enumerate(input):
                    request_keys.append(self.python_obj_to_dynamo_obj({"pk": key["pk"], "sk": key["sk"]}))
                    if ((index / pagination).is_integer() and index > 0) or (index + 1) == len(input):
                        batch_keys = {table: {"Keys": request_keys}}
                        response = dynamodb_client.batch_get_item(RequestItems=batch_keys, ReturnConsumedCapacity="TOTAL")
                        print("Batch_get_item Consumed Capacity:" + str(response["ConsumedCapacity"][0]))
                        if response["Responses"].get(table):
                            for item in response["Responses"][table]:
                                filtered_response.append(self.dynamo_obj_to_python_obj(item))
                        request_keys = []
            else:
                batch_keys = {table: {"Keys": [self.python_obj_to_dynamo_obj({"pk": key["pk"], "sk": key["sk"]}) for key in input]}}
                response = dynamodb_client.batch_get_item(RequestItems=batch_keys, ReturnConsumedCapacity="TOTAL")
                print("Batch_get_item Consumed Capacity:" + str(response["ConsumedCapacity"][0]))
                if response["Responses"].get(table):
                    for item in response["Responses"][table]:
                        filtered_response.append(self.dynamo_obj_to_python_obj(item))
            if filtered_response:
                batch_keys = {table: {"Keys": [self.python_obj_to_dynamo_obj({"pk": key["pk"], "sk": key["sk"]}) for key in input]}}
                for item in batch_keys[table]["Keys"]:
                    for response_item in filtered_response:
                        if response_item["pk"] == item["pk"]["S"] and response_item["sk"] == item["sk"]["S"]:
                            filtered_ordered_response.append(response_item)
        return filtered_ordered_response

    def execute_no_parse_get_item(self, input):
        response = dynamodb_client.get_item(**input)
        if "Item" in response:
            return response["Item"]
        return None

    def execute_update_item(self, input):
        input["ReturnConsumedCapacity"] = "TOTAL"
        response = dynamodb_client.update_item(**input)
        print("Update_item Consumed Capacity:" + str(response["ConsumedCapacity"]["CapacityUnits"]))
        return True

    def execute_query(self, input, ScanIndexForward=False):
        input["ReturnConsumedCapacity"] = "INDEXES"
        input["ScanIndexForward"] = ScanIndexForward
        response = dynamodb_client.query(**input)
        print("Query Consumed Capacity:" + str(response["ConsumedCapacity"]["CapacityUnits"]))
        print("Query Consumed Count/ScannedCount:" + str(response["Count"]) + "/" + str(response["ScannedCount"]))
        if "LastEvaluatedKey" in response:
            response_last_evaluated = {}
            response_last_evaluated["LastEvaluatedKey"] = response["LastEvaluatedKey"]
            while True:
                input["ExclusiveStartKey"] = response_last_evaluated["LastEvaluatedKey"]
                response_last_evaluated = dynamodb_client.query(**input)
                print("Query Consumed Capacity:" + str(response_last_evaluated["ConsumedCapacity"]["CapacityUnits"]))
                print("Query Consumed Count/ScannedCount:" + str(response_last_evaluated["Count"]) + "/" + str(response_last_evaluated["ScannedCount"]))
                response["Items"].extend(response_last_evaluated["Items"])
                if not "LastEvaluatedKey" in response_last_evaluated:
                    break
                if len(response["Items"]) > 10000:
                    break
        if "Items" in response:
            deserializer_list = []
            for item in response["Items"]:
                deserializer_list.append(self.dynamo_obj_to_python_obj(item))
            return deserializer_list
        else:
            return []

    def execute_paginated_query(self, input, limit=20, last_evaluated_key=None, key_schema=None, reverse=False):
        input["ReturnConsumedCapacity"] = "TOTAL"
        input["ScanIndexForward"] = reverse
        input["Limit"] = int(limit)
        if last_evaluated_key:
            if last_evaluated_key == key_schema:
                return [], key_schema
            input["ExclusiveStartKey"] = last_evaluated_key
        response = dynamodb_client.query(**input)
        print("Query Consumed Capacity:" + str(response["ConsumedCapacity"]["CapacityUnits"]))
        if len(response["Items"]) < limit:
            last_evaluated_key = key_schema
        if "LastEvaluatedKey" in response:
            last_evaluated_key = response["LastEvaluatedKey"]
        if "Items" in response:
            deserializer_list = []
            for item in response["Items"]:
                deserializer_list.append(self.dynamo_obj_to_python_obj(item))
            if not last_evaluated_key and key_schema:
                last_evaluated_key = {}
                if deserializer_list:
                    for param in deserializer_list[-1]:
                        if param in key_schema:
                            last_evaluated_key[param] = {"S": deserializer_list[-1][param]}
            return deserializer_list, last_evaluated_key
        else:
            return [], key_schema

    def execute_put_item(self, input):
        input["ReturnConsumedCapacity"] = "TOTAL"
        response = dynamodb_client.put_item(**input)
        return True

    def execute_delete_item(self, input):
        print("executing delete_item")
        dynamodb_client.delete_item(**input)
        return True

    def execute_scan(self):
        print("executing execute_scan")
        response = table.scan()
        data = response["Items"]
        while True:
            if "LastEvaluatedKey" in response:
                print("Reading items...")
                response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
                data.extend(response["Items"])
            else:
                break
        return data
