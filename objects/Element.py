import time


class Element:
    def __init__(self, project_id, site_id, building_id, storey_id, category_id, element_id, element_name, element_data, element_properties, element_has_sub_elements, storey_index, element_index, element_sub_elements_count) -> None:
        self.pk = "proj#" + project_id + "#site#" + site_id + "#building#" + building_id + "#storey#" + storey_id + "#category#" + category_id + "#element"
        self.sk = "proj#" + project_id + "#element#" + element_id
        self.element_project_id = project_id
        self.element_site_id = site_id
        self.element_building_id = building_id
        self.element_storey_id = storey_id
        self.element_category_id = category_id
        self.element_id = element_id
        self.element_name = element_name
        self.element_data = element_data
        self.element_properties = element_properties
        self.element_has_sub_elements = element_has_sub_elements
        self.element_storey_index = storey_index
        self.element_index = element_index
        self.element_layer = ""
        self.element_sub_elements_count = element_sub_elements_count
        self.ttl = int(time.time()) + 10400000  ### 120 dias
        # self.project_id_category = "proj#" + project_id + "#category#" + category_id
        # self.project_id_storey = "proj#" + project_id + "#storey#" + storey_id
        # self.guid_id = element_id
        # self.created_at = str(time.time())
