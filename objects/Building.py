import time


class Building:
    def __init__(self, project_id, site_id, building_id, building_name, building_data, building_properties) -> None:
        self.pk = "proj#" + project_id + "#site#" + site_id + "#building"
        self.sk = "building#" + building_id
        self.building_project_id = project_id
        self.building_site_id = site_id
        self.building_id = building_id
        self.building_name = building_name
        self.building_data = building_data
        self.building_properties = building_properties
        self.ttl = int(time.time()) + 10400000  ### 120 dias
        # self.created_at = str(time.time())
