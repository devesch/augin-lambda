import time


class SubElement:
    def __init__(self, project_id, site_id, building_id, storey_id, category_id, element_id, sub_element_id, sub_element_name, sub_element_data, sub_element_properties, sub_element_has_sub_sub_elements, storey_index, element_index, sub_element_index, sub_element_sub_sub_elements_count) -> None:
        self.pk = "proj#" + project_id + "#site#" + site_id + "#building#" + building_id + "#storey#" + storey_id + "#category#" + category_id + "#element#" + element_id + "#sub_element"
        self.sk = "proj#" + project_id + "#sub_element#" + sub_element_id
        self.sub_element_project_id = project_id
        self.sub_element_site_id = site_id
        self.sub_element_building_id = building_id
        self.sub_element_storey_id = storey_id
        self.sub_element_category_id = category_id
        self.sub_element_element_id = element_id
        self.sub_element_id = sub_element_id
        self.sub_element_name = sub_element_name
        self.sub_element_data = sub_element_data
        self.sub_element_properties = sub_element_properties
        self.sub_element_has_sub_sub_elements = sub_element_has_sub_sub_elements
        self.sub_element_storey_index = storey_index
        self.sub_element_element_index = element_index
        self.sub_element_index = sub_element_index
        self.sub_element_sub_sub_elements_count = sub_element_sub_sub_elements_count
        self.ttl = int(time.time()) + 10400000  ### 120 dias
        # self.project_id_category = "proj#" + project_id + "#category#" + category_id
        # self.project_id_storey = "proj#" + project_id + "#storey#" + storey_id
        # self.guid_id = sub_element_id
        # self.created_at = str(time.time())
