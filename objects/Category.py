import time


class Category:
    def __init__(self, project_id, site_id, building_id, storey_id, category_id) -> None:
        self.pk = "proj#" + project_id + "#site#" + site_id + "#building#" + building_id + "#storey#" + storey_id + "#category"
        self.sk = "category#" + category_id
        self.category_project_id = project_id
        self.category_site_id = site_id
        self.category_building_id = building_id
        self.category_storey_id = storey_id
        self.category_id = category_id
        self.category_elements_count = "0"
        self.ttl = int(time.time()) + 10400000  ### 120 dias
        # self.created_at = str(time.time())
