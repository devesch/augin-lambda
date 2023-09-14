from python_web_frame.base_page import BasePage
from utils.utils.ReadWrite import ReadWrite
from utils.Config import lambda_constants


class BackofficePage(BasePage):
    def __init__(self) -> None:
        super().__init__()

    def list_html_plan_reference_tracker_options(self):
        full_html = []
        for plan_reference_tracker in lambda_constants["plan_reference_trackers"]:
            html = ReadWrite().read_html("backoffice_create_plan/_codes/html_plan_reference_tracker_options")
            html.esc("plan_reference_tracker_val", lambda_constants["plan_reference_trackers"][plan_reference_tracker])
            html.esc("plan_reference_tracker_name_val", self.translate(plan_reference_tracker))
            if self.post.get("plan_reference_tracker") == plan_reference_tracker:
                html.esc("pre_sel_val", "selected='selected'")
            full_html.append(str(html))
        return "".join(full_html)
