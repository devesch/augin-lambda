import time


class Site:
    def __init__(self, project_id, site_id, site_name, site_data, site_properties) -> None:
        self.pk = "proj#" + project_id + "#site"
        self.sk = "site#" + site_id
        self.site_project_id = project_id
        self.site_id = site_id
        self.site_name = site_name
        self.site_data = site_data
        self.site_properties = site_properties
        self.ttl = int(time.time()) + 10400000  ### 120 dias
        # self.created_at = str(time.time())
