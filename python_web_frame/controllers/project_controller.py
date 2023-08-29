import json
from utils.Config import lambda_constants
from utils.AWS.Dynamo import Dynamo
from utils.utils.EncodeDecode import EncodeDecode
from utils.utils.Sort import Sort
from utils.AWS.Sqs import Sqs


class ProjectController:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ProjectController, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def update_project_model_id(self, project, model):
        project = Dynamo().get_project(model["model_project_id"])
        project["project_model_id"] = model["model_id"]
        Dynamo().put_entity(project, table=lambda_constants["table_web_data"])

    def generate_js_property_ids(self, element_properties):
        js_property_ids = []
        for property in element_properties:
            js_property_ids.append(property["property_link"])
        return str(js_property_ids).replace("'", "\\'")

    def generate_project_variables(self, project_id, element):
        project_variables = {}
        if "site#" in element["sk"]:
            project_variables["element_type"] = "site"
            project_variables["site_id"] = element["site_id"]
            project_variables["building_id"] = None
            project_variables["storey_id"] = None
            project_variables["category_id"] = None
            project_variables["element_id"] = None
            project_variables["sub_element_id"] = None
            project_variables["sub_sub_element_id"] = None
            project_variables["nano_element_id"] = None
            element["site_data"]["Guid"] = element["site_id"]
            project_variables["data_encoded"] = EncodeDecode().encode_to_b64(json.dumps(element["site_data"]))
            project_variables["property_ids"] = element["site_properties"]
            project_variables["js_property_ids"] = self.generate_js_property_ids(element["site_properties"])
            project_variables["guid"] = element["site_id"]
            project_variables["last_selected_element"] = "accordion_header_" + project_id + project_variables["site_id"]

        if "building#" in element["sk"]:
            project_variables["element_type"] = "building"
            project_variables["site_id"] = element["building_site_id"]
            project_variables["building_id"] = element["building_id"]
            project_variables["storey_id"] = None
            project_variables["category_id"] = None
            project_variables["element_id"] = None
            project_variables["sub_element_id"] = None
            project_variables["sub_sub_element_id"] = None
            project_variables["nano_element_id"] = None
            element["building_data"]["Guid"] = element["building_id"]
            project_variables["data_encoded"] = EncodeDecode().encode_to_b64(json.dumps(element["building_data"]))
            project_variables["property_ids"] = element["building_properties"]
            project_variables["js_property_ids"] = self.generate_js_property_ids(element["building_properties"])
            project_variables["guid"] = element["building_id"]
            project_variables["last_selected_element"] = "accordion_header_" + project_id + project_variables["site_id"] + project_variables["building_id"]

        if "storey#" in element["sk"]:
            project_variables["element_type"] = "storey"
            project_variables["site_id"] = element["storey_site_id"]
            project_variables["building_id"] = element["storey_building_id"]
            project_variables["storey_id"] = element["storey_id"]
            project_variables["category_id"] = None
            project_variables["element_id"] = None
            project_variables["sub_element_id"] = None
            project_variables["sub_sub_element_id"] = None
            project_variables["nano_element_id"] = None
            element["storey_data"]["Guid"] = element["storey_id"]
            project_variables["data_encoded"] = EncodeDecode().encode_to_b64(json.dumps(element["storey_data"]))
            project_variables["property_ids"] = element["storey_properties"]
            project_variables["js_property_ids"] = self.generate_js_property_ids(element["storey_properties"])
            project_variables["guid"] = element["storey_id"]
            project_variables["last_selected_element"] = "accordion_header_" + project_id + project_variables["site_id"] + project_variables["building_id"] + project_variables["storey_id"]

        if "#element" in element["sk"]:
            project_variables["element_type"] = "element"
            project_variables["site_id"] = element["element_site_id"]
            project_variables["building_id"] = element["element_building_id"]
            project_variables["storey_id"] = element["element_storey_id"]
            project_variables["category_id"] = element["element_category_id"]
            project_variables["element_id"] = element["element_id"]
            project_variables["sub_element_id"] = None
            project_variables["sub_sub_element_id"] = None
            project_variables["nano_element_id"] = None
            element["element_data"]["Guid"] = element["element_id"]
            project_variables["data_encoded"] = EncodeDecode().encode_to_b64(json.dumps(element["element_data"]))
            project_variables["property_ids"] = element["element_properties"]
            project_variables["js_property_ids"] = self.generate_js_property_ids(element["element_properties"])
            project_variables["guid"] = element["element_id"]
            project_variables["last_selected_element"] = "accordion_header_" + project_id + project_variables["site_id"] + project_variables["building_id"] + project_variables["storey_id"] + project_variables["category_id"] + project_variables["element_id"]

        if "#sub_element" in element["sk"]:
            project_variables["element_type"] = "sub_element"
            project_variables["site_id"] = element["sub_element_site_id"]
            project_variables["building_id"] = element["sub_element_building_id"]
            project_variables["storey_id"] = element["sub_element_storey_id"]
            project_variables["category_id"] = element["sub_element_category_id"]
            project_variables["element_id"] = element["sub_element_element_id"]
            project_variables["sub_element_id"] = element["sub_element_id"]
            project_variables["sub_sub_element_id"] = None
            project_variables["nano_element_id"] = None
            element["sub_element_data"]["Guid"] = element["sub_element_id"]
            project_variables["data_encoded"] = EncodeDecode().encode_to_b64(json.dumps(element["sub_element_data"]))
            project_variables["property_ids"] = element["sub_element_properties"]
            project_variables["js_property_ids"] = self.generate_js_property_ids(element["sub_element_properties"])
            project_variables["guid"] = element["sub_element_id"]
            project_variables["last_selected_element"] = "accordion_header_" + project_id + project_variables["site_id"] + project_variables["building_id"] + project_variables["storey_id"] + project_variables["category_id"] + project_variables["element_id"] + project_variables["sub_element_id"]

        if "#sub_sub_element" in element["sk"]:
            project_variables["element_type"] = "sub_sub_element"
            project_variables["site_id"] = element["sub_sub_element_site_id"]
            project_variables["building_id"] = element["sub_sub_element_building_id"]
            project_variables["storey_id"] = element["sub_sub_element_storey_id"]
            project_variables["category_id"] = element["sub_sub_element_category_id"]
            project_variables["element_id"] = element["sub_sub_element_element_id"]
            project_variables["sub_element_id"] = element["sub_sub_element_sub_element_id"]
            project_variables["sub_sub_element_id"] = element["sub_sub_element_id"]
            project_variables["nano_element_id"] = None
            element["sub_sub_element_data"]["Guid"] = element["sub_sub_element_id"]
            project_variables["data_encoded"] = EncodeDecode().encode_to_b64(json.dumps(element["sub_sub_element_data"]))
            project_variables["js_property_ids"] = self.generate_js_property_ids(element["sub_sub_element_properties"])
            project_variables["property_ids"] = element["sub_sub_element_properties"]
            project_variables["guid"] = element["sub_sub_element_id"]
            project_variables["last_selected_element"] = "accordion_header_" + project_id + project_variables["site_id"] + project_variables["building_id"] + project_variables["storey_id"] + project_variables["category_id"] + project_variables["element_id"] + project_variables["sub_element_id"] + project_variables["sub_sub_element_id"]

        if "#nano_element" in element["sk"]:
            project_variables["element_type"] = "nano_element"
            project_variables["site_id"] = element["nano_element_site_id"]
            project_variables["building_id"] = element["nano_element_building_id"]
            project_variables["storey_id"] = element["nano_element_storey_id"]
            project_variables["category_id"] = element["nano_element_category_id"]
            project_variables["element_id"] = element["nano_element_element_id"]
            project_variables["sub_element_id"] = element["nano_element_sub_element_id"]
            project_variables["sub_sub_element_id"] = element["nano_element_sub_sub_element_id"]
            project_variables["nano_element_id"] = element["nano_element_id"]
            element["nano_element_data"]["Guid"] = element["nano_element_id"]
            project_variables["data_encoded"] = EncodeDecode().encode_to_b64(json.dumps(element["nano_element_data"]))
            project_variables["property_ids"] = element["nano_element_properties"]
            project_variables["js_property_ids"] = self.generate_js_property_ids(element["nano_element_properties"])
            project_variables["guid"] = element["nano_element_id"]
            project_variables["last_selected_element"] = "accordion_header_" + project_id + project_variables["site_id"] + project_variables["building_id"] + project_variables["storey_id"] + project_variables["category_id"] + project_variables["element_id"] + project_variables["sub_element_id"] + project_variables["sub_sub_element_id"] + project_variables["nano_element_id"]

        return project_variables

    def generate_type_and_material_data(self, propertys):
        filtered_properties = []
        type_and_material_data = []
        for property in propertys:
            if "material" in property["property_type"].lower():
                type_and_material_data.append({"key": "Material", "value": property["property_name"]})
            elif "type" in property["property_type"].lower():
                type_and_material_data.append({"key": "Type", "value": property["property_name"]})
            else:
                filtered_properties.append(property)
        return filtered_properties, type_and_material_data

    def remove_pset_from_property(self, property_name):
        if "Pset_" in property_name:
            return property_name.split("Pset_")[1]
        return property_name

    def add_project_to_process_xml_to_dynamo(self, model_id, output_bucket, output_key, output_project_domain_name, reprocess=False):
        sqs_message = {"model_id": model_id, "output_bucket": output_bucket, "output_key": output_key, "output_project_domain_name": output_project_domain_name, "reprocess": reprocess}
        Sqs().send_message(lambda_constants["sqs_queue_url_process_xml_to_dynamo"], sqs_message)

    def generate_project_storeys(self, project_id):
        storeys = []
        sites = Dynamo().query_sites(project_id)
        if sites:
            buildings = Dynamo().query_buildings(project_id, sites[0]["site_id"])
            if buildings:
                storeys = Dynamo().query_storeys(project_id, sites[0]["site_id"], buildings[0]["building_id"])
                if storeys:
                    storeys = Sort().sort_dict_list(storeys, "storey_index", reverse=False, integer=True)
        return storeys

    def generate_propertys(self, project_id, property_ids):
        if type(property_ids) == str:
            property_ids = property_ids.replace("#", "").strip("' ").split("', '")
        elif type(property_ids) == list:
            filtered_property_ids = []
            for property in property_ids:
                filtered_property_ids.append(property["property_link"].replace("#", ""))
                property_ids = filtered_property_ids
        return Dynamo().get_batch_property(project_id, property_ids)
