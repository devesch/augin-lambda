from python_web_frame.base_page import BasePage


class default_lambda_page_name_val(BasePage):
    public = public_val
    bypass = bypass_val

    def render_get(self):
        html = super().parse_html()
        self.check_error_msg(html, self.error_msg)
default_list_thumbs_val
default_list_entity_val
default_inputs_replace_val

if_post_in_render_get_val
        return str(html)

    def render_post(self):
if_not_post_in_render_post_val

if_post_verification_in_render_post_val
        return self.render_get()

def_list_entity_html_val