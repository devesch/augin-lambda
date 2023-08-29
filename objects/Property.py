import time


class Property:
    def __init__(self, project_id, property_id, property_name, property_type, property_class, property_data) -> None:
        self.pk = "proj#" + project_id + "#property#" + property_id
        self.sk = "property#" + property_id
        self.property_project_id = project_id
        self.property_id = property_id
        self.property_type = property_type
        self.property_name = property_name
        self.property_class = property_class
        self.property_data = property_data
        self.ttl = int(time.time()) + 10400000  ### 120 dias
        # self.created_at = str(time.time())
