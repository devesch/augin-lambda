import time


class Storey:
    def __init__(self, project_id, site_id, building_id, storey_id, storey_name, storey_data, storey_properties, storey_index) -> None:
        self.pk = "proj#" + project_id + "#site#" + site_id + "#building#" + building_id + "#storey"
        self.sk = "storey#" + storey_id
        self.storey_project_id = project_id
        self.storey_site_id = site_id
        self.storey_building_id = building_id
        self.storey_id = storey_id
        self.storey_name = storey_name
        self.storey_data = storey_data
        self.storey_properties = storey_properties
        self.storey_index = storey_index
        self.ttl = int(time.time()) + 10400000  ### 120 dias
        # self.project_id_storey = "proj#" + project_id + "#storey#" + storey_id
        # self.guid_id = storey_id
        # self.created_at = str(time.time())
