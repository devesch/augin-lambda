from python_web_frame.panel_page import PanelPage
from utils.AWS.Dynamo import Dynamo


class PanelExploreProjectsModalEditFederatedModelHtml(PanelPage):
    def run(self):
        federated_model = Dynamo().get_model(self.post["federated_model_id"])
        federated_required_models = Dynamo().batch_get_models(federated_model["model_federated_required_ids"])
        return {"success": self.list_html_edit_federated_model_rows(federated_required_models)}
