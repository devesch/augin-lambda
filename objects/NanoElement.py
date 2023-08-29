import time


class NanoElement:
    def __init__(self, project_id, site_id, building_id, storey_id, category_id, element_id, sub_element_id, sub_sub_element_id, nano_element_id, nano_element_name, nano_element_data, nano_element_properties, storey_index, element_index, sub_element_index, sub_sub_element_index, nano_element_index) -> None:
        self.pk = "proj#" + project_id + "#site#" + site_id + "#building#" + building_id + "#storey#" + storey_id + "#category#" + category_id + "#element#" + element_id + "#sub_element#" + sub_element_id + "#sub_sub_element#" + sub_sub_element_id + "#nano_element"
        self.sk = "proj#" + project_id + "#nano_element#" + nano_element_id
        self.nano_element_project_id = project_id
        self.nano_element_site_id = site_id
        self.nano_element_building_id = building_id
        self.nano_element_storey_id = storey_id
        self.nano_element_category_id = category_id
        self.nano_element_element_id = element_id
        self.nano_element_sub_element_id = sub_element_id
        self.nano_element_sub_sub_element_id = sub_sub_element_id
        self.nano_element_id = nano_element_id
        self.nano_element_name = nano_element_name
        self.nano_element_data = nano_element_data
        self.nano_element_properties = nano_element_properties
        self.nano_element_storey_index = storey_index
        self.nano_element_element_index = element_index
        self.nano_element_sub_element_index = sub_element_index
        self.nano_element_sub_sub_element_index = sub_sub_element_index
        self.nano_element_index = nano_element_index
        self.ttl = int(time.time()) + 10400000  ### 120 dias
        # self.project_id_category = "proj#" + project_id + "#category#" + category_id
        # self.project_id_storey = "proj#" + project_id + "#storey#" + storey_id
        # self.guid_id = nano_element_id
        # self.created_at = str(time.time())
