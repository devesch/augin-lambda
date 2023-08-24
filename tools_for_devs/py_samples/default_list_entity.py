        backoffice_data = self.dynamo.get_backoffice_data()
        entity_vals, last_evaluated_key = self.dynamo.query_val()
        html.esc("last_evaluated_key_val", dumps(last_evaluated_key))
        html.esc("showing_total_count_val", len(entity_vals))
        html.esc("html_pagination", self.show_html_pagination(len(entity_vals), backoffice_data["backoffice_data_total_entity_val"], "query_val", last_evaluated_key))
        html.esc("html_entity_val_table_rows", self.list_html_entity_val_table_rows(entity_vals))
