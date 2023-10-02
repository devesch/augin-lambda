from python_web_frame.backoffice_page import BackofficePage
from utils.AWS.Dynamo import Dynamo
from utils.utils.Validation import Validation
import json


class BackofficeModelsHtml(BackofficePage):
    def run(self):
        last_evaluated_key = {}
        query_filter = self.post["search_model_state"]
        if self.post.get("search_user") and self.post["search_model_state"] == "all":
            query = "get_model"
            model = Dynamo().get_model(self.post["search_user"])
            if not model:
                return {"success": "", "last_evaluated_key": json.dumps(last_evaluated_key), "query": query, "query_filter": query_filter, "showing_total_count": "0"}
            models = [model]
            return {"success": self.list_html_backoffice_models_table_rows(models), "last_evaluated_key": json.dumps(last_evaluated_key), "query": query, "query_filter": query_filter, "showing_total_count": len(models)}
        else:
            if self.post.get("search_model_state") != "all" and self.post.get("search_user"):
                searched_user = self.load_user(self.post["search_user"])
                query = "query_user_models_from_state"
                if not searched_user:
                    return {"success": "", "last_evaluated_key": json.dumps(last_evaluated_key), "query": query, "query_filter": query_filter, "showing_total_count": "0"}
                models = Dynamo().query_user_models_from_state(searched_user, self.post["search_model_state"])
            else:
                if self.post.get("search_model_state") != "all":
                    query = "query_paginated_all_models_by_state"
                    models, last_evaluated_key = Dynamo().query_paginated_all_models_by_state(self.post["search_model_state"], limit=int(self.user.user_pagination_count))
                else:
                    query = "query_paginated_all_models"
                    models, last_evaluated_key = Dynamo().query_paginated_all_models(limit=int(self.user.user_pagination_count))
            return {"success": self.list_html_backoffice_models_table_rows(models), "last_evaluated_key": json.dumps(last_evaluated_key), "query": query, "query_filter": query_filter, "showing_total_count": len(models)}