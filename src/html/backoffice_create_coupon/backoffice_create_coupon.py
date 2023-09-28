from python_web_frame.backoffice_page import BackofficePage
from objects.Coupon import Coupon
from utils.AWS.Dynamo import Dynamo
from utils.utils.Date import Date
from utils.utils.Http import Http
from utils.utils.Validation import Validation


class BackofficeCreateCoupon(BackofficePage):
    name = "Backoffice - Criar Cupom"
    public = False
    bypass = False
    admin = True

    def render_get(self):
        html = super().parse_html()
        self.check_error_msg(html, self.error_msg)
        if self.path.get("coupon") and not self.post:
            for attribute, value in self.path["coupon"].items():
                if attribute in ["coupon_start_date", "coupon_end_date"] and self.path["coupon"]["coupon_available_for_limited_time"]:
                    self.post[attribute] = Date().format_unixtime_to_html_time(self.path["coupon"][attribute])
                else:
                    self.post[attribute] = value

        if self.post:
            if self.post.get("coupon_name"):
                html.esc("coupon_name_val", self.post["coupon_name"])
            if self.post.get("coupon_description"):
                html.esc("coupon_description_val", self.post["coupon_description"])
            if self.post.get("coupon_code"):
                html.esc("coupon_code_val", self.post["coupon_code"])

            if self.post.get("coupon_available_for_limited_time"):
                html.esc("coupon_available_for_limited_time_checked_val", "checked='checked'")
            else:
                html.esc("coupon_available_for_limited_time_div_visibility_val", "display:none;")

            if self.post.get("coupon_start_date"):
                html.esc("coupon_start_date_val", self.post["coupon_start_date"])
            if self.post.get("coupon_end_date"):
                html.esc("coupon_end_date_val", self.post["coupon_end_date"])

            if self.post.get("coupon_has_limited_uses_count"):
                html.esc("coupon_has_limited_uses_count_checked_val", "checked='checked'")
                if self.post.get("coupon_maxium_uses_count"):
                    html.esc("coupon_maxium_uses_count_val", self.post["coupon_maxium_uses_count"])
            else:
                html.esc("coupon_has_limited_uses_count_div_visibility_val", "display:none;")

            if self.post.get("coupon_discount_type"):
                html.esc("coupon_discount_type_val", self.post["coupon_discount_type"])
                html.esc(self.post["coupon_discount_type"] + "_pre_sel_val", "selected='selected'")

            if self.post.get("coupon_brl_discount"):
                html.esc("coupon_brl_discount_val", self.post["coupon_brl_discount"])
            if self.post.get("coupon_usd_discount"):
                html.esc("coupon_usd_discount_val", self.post["coupon_usd_discount"])

            if self.post.get("coupon_percentage_discount"):
                html.esc("coupon_percentage_discount_val", self.post["coupon_percentage_discount"])

            if self.post.get("coupon_recurrence_months"):
                html.esc("coupon_recurrence_months_val", self.post["coupon_recurrence_months"])

            if self.post.get("coupon_available_monthly"):
                html.esc("coupon_available_monthly_checked_val", "checked='checked'")
            if self.post.get("coupon_available_annually"):
                html.esc("coupon_available_annually_checked_val", "checked='checked'")
            if self.post.get("coupon_available_in_brl"):
                html.esc("coupon_available_in_brl_checked_val", "checked='checked'")
            if self.post.get("coupon_available_in_usd"):
                html.esc("coupon_available_in_usd_checked_val", "checked='checked'")
        else:
            html.esc("coupon_available_for_limited_time_div_visibility_val", "display:none;")
            html.esc("coupon_has_limited_uses_count_div_visibility_val", "display:none;")

        plans = Dynamo().query_entity("plan")
        html.esc("html_coupon_available_plans", self.list_html_coupon_available_plans(plans))

        return str(html)

    def render_post(self):
        self.post["coupons_plans_ids"] = [value for key, value in self.post.items() if key.startswith("coupon_plan_")]

        if not self.post.get("coupon_name"):
            return self.render_get_with_error("É necessário informar um nome")
        if not self.post.get("coupon_description"):
            return self.render_get_with_error("É necessário informar uma descrição")
        if not self.post.get("coupon_code"):
            return self.render_get_with_error("É necessário informar um código")
        if not self.post.get("coupon_recurrence_months"):
            return self.render_get_with_error("É informar durante quantos meses de recorrência o cupom será aplicado")

        if not Validation().check_if_valid_url_param(self.post["coupon_code"]):
            return self.render_get_with_error("O código do cupom não pode conter caracteres que não possam ser usados em uma URL")

        if not self.path.get("coupon"):
            coupon_check = Dynamo().get_coupon(self.post["coupon_code"])
            if coupon_check:
                return self.render_get_with_error("Já existe um cupom com este código")

        if self.post.get("coupon_available_for_limited_time"):
            if not self.post.get("coupon_start_date") or not self.post.get("coupon_end_date"):
                return self.render_get_with_error("É necessário informar uma data de início e de término quando o cupom for por tempo ilimitado")
            if int(Date().format_html_time_to_unixtime(self.post["coupon_start_date"])) > int(Date().format_html_time_to_unixtime(self.post["coupon_end_date"])):
                return self.render_get_with_error("A data de início de vigência deve ser antes da data de término")

        if self.post.get("coupon_has_limited_uses_count") and not (self.post.get("coupon_maxium_uses_count")):
            return self.render_get_with_error("É necessário informar a quantidade máxima de usos do cupom quando ele está limitado em quantidade")

        if self.post["coupon_discount_type"] == "percentage":
            if not self.post["coupon_percentage_discount"]:
                return self.render_get_with_error("É necessário informar o percentual de desconto")
            if int(self.post["coupon_percentage_discount"]) < 1 or int(self.post["coupon_percentage_discount"]) > 99:
                return self.render_get_with_error("O percentual de desconto deve ser um valor entre 1 e 99")

        if self.post["coupon_discount_type"] == "total":
            if not self.post.get("coupon_brl_discount") or not self.post.get("coupon_usd_discount"):
                return self.render_get_with_error("É necessário informar o valor de desconto em R$ e U$ quando o desconto de valor total está ativo")

        if int(self.post["coupon_recurrence_months"]) < 1 or int(self.post["coupon_recurrence_months"]) > 99:
            return self.render_get_with_error("A duração da recorrência deve ser valor entre 1 e 99")

        if not self.path.get("coupon"):
            self.increase_backoffice_data_total_count("coupon")
            coupon = Coupon(self.post["coupon_code"]).__dict__
        else:
            coupon = self.path["coupon"]

        coupon["coupon_name"] = self.post["coupon_name"]
        coupon["coupon_description"] = self.post["coupon_description"]

        for key in ["coupon_available_for_limited_time", "coupon_has_limited_uses_count", "coupon_available_monthly", "coupon_available_annually", "coupon_available_in_brl", "coupon_available_in_usd"]:
            coupon[key] = bool(self.post.get(key))

        if coupon["coupon_available_for_limited_time"]:
            coupon["coupon_start_date"] = Date().format_html_time_to_unixtime(self.post["coupon_start_date"])
            coupon["coupon_end_date"] = Date().format_html_time_to_unixtime(self.post["coupon_end_date"])

        if coupon["coupon_has_limited_uses_count"]:
            coupon["coupon_maxium_uses_count"] = self.post["coupon_maxium_uses_count"]

        coupon["coupon_discount_type"] = self.post["coupon_discount_type"]
        if coupon["coupon_discount_type"] == "percentage":
            coupon["coupon_percentage_discount"] = self.post["coupon_percentage_discount"]
        elif coupon["coupon_discount_type"] == "total":
            coupon["coupon_brl_discount"] = self.post["coupon_brl_discount"]
            coupon["coupon_usd_discount"] = self.post["coupon_usd_discount"]

        coupon["coupon_recurrence_months"] = self.post["coupon_recurrence_months"]
        coupon["coupons_plans_ids"] = self.post["coupons_plans_ids"]

        Dynamo().put_entity(coupon)
        return Http().redirect("backoffice_coupons")
