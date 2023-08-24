import json
from utils.utils.ReadWrite import ReadWrite


class PaginatedPage:
    def show_html_dropdown_select_user_pagination(self, user_pagination_count):
        html = ReadWrite().read_html("main/_codes/html_dropdown_select_user_pagination")
        html.esc(user_pagination_count + "_presel_val", "selected='selected'")
        return str(html)

    def show_html_pagination(self, itens_actual_count, itens_total_count, query, last_evaluated_key=None, query_filter=""):
        html = ReadWrite().read_html("main/_codes/html_pagination")
        html.esc("itens_actual_count_val", itens_actual_count)
        html.esc("itens_total_count_val", itens_total_count)
        html.esc("query_val", query)
        if query_filter:
            html.esc("query_filter_val", query_filter)
        if self.post.get("showing_total_count"):
            html.esc("last_scroll_position_val", self.post.get("last_scroll_position", "0"))
        if not itens_total_count:
            html.esc("pagination_visibility_val", "display: none;")
        elif not last_evaluated_key:
            html.esc("pagination_visibility_val", "display: none;")
        else:
            html.esc("last_evaluated_key_val", json.dumps(last_evaluated_key))
            if str(itens_actual_count) == "0" or str(itens_total_count) == "0":
                html.esc("pagination_visibility_val", "display: none;")
            if int(itens_actual_count) == int(itens_total_count):
                html.esc("pagination_visibility_val", "display: none;")
        return str(html)
