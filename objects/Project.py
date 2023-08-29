import time


class Project:
    def __init__(self, project_id, project_ifc_project, project_layers) -> None:
        self.pk = "proj#" + project_id
        self.sk = "proj#" + project_id
        self.project_id = project_id
        self.project_model_id = project_id
        self.project_ifc_project = project_ifc_project
        self.project_layers = project_layers
        self.project_categories = []
        # self.created_at = str(time.time())
