import time


class Layer:
    def __init__(self, project_id, layer_id, global_id) -> None:
        self.pk = "proj#" + project_id + "#layer#" + layer_id
        self.sk = "global_id#" + global_id
        self.layer_project_id = project_id
        self.layer_global_id = global_id
        self.ttl = int(time.time()) + 10400000  ### 120 dias
        # self.created_at = str(time.time())
