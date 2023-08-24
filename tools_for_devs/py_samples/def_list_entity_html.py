    def list_html_entity_val_table_rows(self, entity_vals):
        full_html = []
        if entity_vals:
            for entity_val in entity_vals:
                html = self.utils.read_html("snakecase_page_name_val/_codes/html_entity_val_table_rows")
default_list_entity_replaces_val
                full_html.append(str(html))
        return "".join(full_html)