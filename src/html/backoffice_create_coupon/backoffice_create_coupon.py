from python_web_frame.backoffice_page import BackofficePage
from utils.AWS.Dynamo import Dynamo


class BackofficeCreateCoupon(BackofficePage):
    name = "Backoffice - Criar Cupon"
    public = False
    bypass = False
    admin = True

    def render_get(self):
        html = super().parse_html()
        if self.path.get("coupon") and not self.post:
            for attribute, value in self.path["coupon"].items():
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

            if self.post.get("coupon_has_limited_quantity"):
                html.esc("coupon_has_limited_quantity_checked_val", "checked='checked'")
            else:
                html.esc("coupon_has_limited_quantity_div_visibility_val", "display:none;")

            if self.post.get("coupon_discount_type"):
                html.esc("coupon_discount_type_val", self.post["coupon_discount_type"])
                html.esc(self.post["coupon_discount_type"] + "_pre_sel_val", "selected='selected'")

            if self.post.get("coupon_brl_discount"):
                html.esc("coupon_brl_discount_val", self.post["coupon_brl_discount"])
            if self.post.get("coupon_usd_discount"):
                html.esc("coupon_usd_discount_val", self.post["coupon_usd_discount"])

            if self.post.get("coupon_percentage_discount"):
                html.esc("coupon_percentage_discount_val", self.post["coupon_percentage_discount"])

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
            html.esc("coupon_has_limited_quantity_div_visibility_val", "display:none;")

        plans = Dynamo().query_entity("plan")
        html.esc("html_coupon_available_plans", self.list_html_coupon_available_plans(plans))

        return str(html)

    def render_post(self):
        self.post["coupons plans"] = [value for key, value in self.post.items() if key.startswith("coupon_plan_")]
        return self.render_get_with_error("TODO POST")
        # if not self.post.get("plan_name_pt"):
        #     return self.render_get_with_error("É necessárion informar um nome em PT")
        # if not self.post.get("plan_name_en"):
        #     return self.render_get_with_error("É necessárion informar um nome em EN")
        # if not self.post.get("plan_name_es"):
        #     return self.render_get_with_error("É necessárion informar um nome em ES")
        # if not self.post.get("plan_description_pt"):
        #     return self.render_get_with_error("É necessárion informar uma descrição em PT")
        # # if not self.post.get("plan_description_en"):
        # #     return self.render_get_with_error("É necessárion informar uma descrição em EN")
        # # if not self.post.get("plan_description_es"):
        # #     return self.render_get_with_error("É necessárion informar uma descrição em ES")

        # if self.post.get("plan_price_annually_brl"):
        #     if not Validation().check_if_is_number(self.post["plan_price_annually_brl"]):
        #         return self.render_get_with_error("O preço do plano anual em BRL deve ser um número")
        # if self.post.get("plan_price_annually_brl_actual"):
        #     if not Validation().check_if_is_number(self.post["plan_price_annually_brl_actual"]):
        #         return self.render_get_with_error("O preço atual do plano anual em BRL deve ser um número")

        # if self.post.get("plan_price_annually_usd"):
        #     if not Validation().check_if_is_number(self.post["plan_price_annually_usd"]):
        #         return self.render_get_with_error("O preço do plano anual em USD deve ser um número")
        # if self.post.get("plan_price_annually_usd_actual"):
        #     if not Validation().check_if_is_number(self.post["plan_price_annually_usd_actual"]):
        #         return self.render_get_with_error("O preço atual do plano anual em USD deve ser um número")

        # if self.post.get("plan_price_monthly_brl"):
        #     if not Validation().check_if_is_number(self.post["plan_price_monthly_brl"]):
        #         return self.render_get_with_error("O preço do plano mensal em BRL deve ser um número")
        # if self.post.get("plan_price_monthly_brl_actual"):
        #     if not Validation().check_if_is_number(self.post["plan_price_monthly_brl_actual"]):
        #         return self.render_get_with_error("O preço atual do plano mensal em BRL deve ser um número")

        # if self.post.get("plan_price_monthly_usd"):
        #     if not Validation().check_if_is_number(self.post["plan_price_monthly_usd"]):
        #         return self.render_get_with_error("O preço do plano mensal em USD deve ser um número")
        # if self.post.get("plan_price_monthly_usd_actual"):
        #     if not Validation().check_if_is_number(self.post["plan_price_monthly_usd_actual"]):
        #         return self.render_get_with_error("O preço atual do plano mensal em USD deve ser um número")

        # if self.post.get("plan_cloud_space_in_mbs"):
        #     if not Validation().check_if_is_number(self.post["plan_cloud_space_in_mbs"]):
        #         return self.render_get_with_error("O tamanho máximo em núvem deve ser um número")
        # if self.post.get("plan_maxium_model_size_in_mbs"):
        #     if not Validation().check_if_is_number(self.post["plan_maxium_model_size_in_mbs"]):
        #         return self.render_get_with_error("O tamanho do modelo máximo deve ser um número")
        # if self.post.get("plan_maxium_federated_size_in_mbs"):
        #     if not Validation().check_if_is_number(self.post["plan_maxium_federated_size_in_mbs"]):
        #         return self.render_get_with_error("O tamanho de federado máximo deve ser um número")
        # if self.post.get("plan_maxium_devices_available"):
        #     if not Validation().check_if_is_number(self.post["plan_maxium_devices_available"]):
        #         return self.render_get_with_error("A quantidade máxima de dispositivos deve ser um número")
        # if self.post.get("plan_maxium_devices_changes_in_30d"):
        #     if not Validation().check_if_is_number(self.post["plan_maxium_devices_changes_in_30d"]):
        #         return self.render_get_with_error("A quantidade máxima de troca de dispositivos deve ser um número")
        # if self.post.get("plan_trial_duration_in_days"):
        #     if not Validation().check_if_is_number(self.post["plan_trial_duration_in_days"]):
        #         return self.render_get_with_error("A duração do plano trial em dias deve ser um número")

        # if self.post.get("plan_app_can_be_offline_in_days"):
        #     if not Validation().check_if_is_number(self.post["plan_app_can_be_offline_in_days"]):
        #         return self.render_get_with_error("A duração do APP offline em dias deve ser um número")

        # if not self.post.get("plan_trial_duration_in_days"):
        #     self.post["plan_trial_duration_in_days"] = "0"

        # if not self.path.get("plan"):
        #     plan = Plan(Generate().generate_short_id()).__dict__
        #     plan["plan_name_pt"] = self.post["plan_name_pt"]
        #     StripeController().create_product(plan, "plan")
        # else:
        #     plan = self.path["plan"]

        # plan["plan_name_pt"] = self.post["plan_name_pt"]
        # plan["plan_name_en"] = self.post["plan_name_en"]
        # plan["plan_name_es"] = self.post["plan_name_es"]

        # plan["plan_description_pt"] = self.post["plan_description_pt"]
        # # plan["plan_description_en"] = self.post["plan_description_en"]
        # # plan["plan_description_es"] = self.post["plan_description_es"]

        # if self.post.get("plan_available_for_purchase"):
        #     plan["plan_available_for_purchase"] = True
        # else:
        #     plan["plan_available_for_purchase"] = False

        # if self.post.get("plan_available_annually"):
        #     plan["plan_available_annually"] = True
        # else:
        #     plan["plan_available_annually"] = False
        # plan["plan_price_annually_brl"] = self.post["plan_price_annually_brl"]
        # plan["plan_price_annually_brl_actual"] = self.post["plan_price_annually_brl_actual"]
        # plan["plan_price_annually_usd"] = self.post["plan_price_annually_usd"]
        # plan["plan_price_annually_usd_actual"] = self.post["plan_price_annually_usd_actual"]
        # if self.post.get("plan_annually_card_payment_method"):
        #     plan["plan_annually_card_payment_method"] = True
        # else:
        #     plan["plan_annually_card_payment_method"] = False
        # if self.post.get("plan_annually_boleto_payment_method"):
        #     plan["plan_annually_boleto_payment_method"] = True
        # else:
        #     plan["plan_annually_boleto_payment_method"] = False
        # if self.post.get("plan_annually_pix_payment_method"):
        #     plan["plan_annually_pix_payment_method"] = True
        # else:
        #     plan["plan_annually_pix_payment_method"] = False

        # if self.post.get("plan_available_monthly"):
        #     plan["plan_available_monthly"] = True
        # else:
        #     plan["plan_available_monthly"] = False
        # plan["plan_price_monthly_brl"] = self.post["plan_price_monthly_brl"]
        # plan["plan_price_monthly_brl_actual"] = self.post["plan_price_monthly_brl_actual"]
        # plan["plan_price_monthly_usd"] = self.post["plan_price_monthly_usd"]
        # plan["plan_price_monthly_usd_actual"] = self.post["plan_price_monthly_usd_actual"]
        # if self.post.get("plan_monthly_card_payment_method"):
        #     plan["plan_monthly_card_payment_method"] = True
        # else:
        #     plan["plan_monthly_card_payment_method"] = False
        # if self.post.get("plan_monthly_boleto_payment_method"):
        #     plan["plan_monthly_boleto_payment_method"] = True
        # else:
        #     plan["plan_monthly_boleto_payment_method"] = False
        # if self.post.get("plan_monthly_pix_payment_method"):
        #     plan["plan_monthly_pix_payment_method"] = True
        # else:
        #     plan["plan_monthly_pix_payment_method"] = False

        # plan["plan_cloud_space_in_mbs"] = self.post["plan_cloud_space_in_mbs"]
        # plan["plan_maxium_model_size_in_mbs"] = self.post["plan_maxium_model_size_in_mbs"]
        # plan["plan_maxium_federated_size_in_mbs"] = self.post["plan_maxium_federated_size_in_mbs"]
        # plan["plan_reference_tracker"] = self.post["plan_reference_tracker"]
        # plan["plan_maxium_devices_available"] = self.post["plan_maxium_devices_available"]
        # plan["plan_maxium_devices_changes_in_30d"] = self.post["plan_maxium_devices_changes_in_30d"]
        # plan["plan_app_can_be_offline_in_days"] = self.post["plan_app_can_be_offline_in_days"]
        # plan["plan_team_play_participants"] = self.post["plan_team_play_participants"]

        # if self.post.get("plan_download_files"):
        #     plan["plan_download_files"] = True
        # else:
        #     plan["plan_download_files"] = False

        # if self.post.get("plan_share_files"):
        #     plan["plan_share_files"] = True
        # else:
        #     plan["plan_share_files"] = False

        # if self.post.get("plan_has_trial"):
        #     plan["plan_has_trial"] = True
        # else:
        #     plan["plan_has_trial"] = False

        # plan["plan_trial_duration_in_days"] = self.post["plan_trial_duration_in_days"]

        # if plan["plan_price_annually_brl_actual"]:
        #     if not plan["plan_price_annually_brl_actual_stripe_id"]:
        #         plan["plan_price_annually_brl_actual_stripe_id"] = StripeController().create_price(plan["plan_id"], "brl", plan["plan_price_annually_brl_actual"], "year")
        #     else:
        #         stripe_price = StripeController().get_price(plan["plan_price_annually_brl_actual_stripe_id"])
        #         if str(stripe_price.unit_amount) != plan["plan_price_annually_brl_actual"]:
        #             plan["plan_price_annually_brl_actual_stripe_id"] = StripeController().create_price(plan["plan_id"], "brl", plan["plan_price_annually_brl_actual"], "year")
        # if plan["plan_price_annually_usd_actual"]:
        #     if not plan["plan_price_annually_usd_actual_stripe_id"]:
        #         plan["plan_price_annually_usd_actual_stripe_id"] = StripeController().create_price(plan["plan_id"], "usd", plan["plan_price_annually_usd_actual"], "year")
        #     else:
        #         stripe_price = StripeController().get_price(plan["plan_price_annually_usd_actual_stripe_id"])
        #         if str(stripe_price.unit_amount) != plan["plan_price_annually_usd_actual"]:
        #             plan["plan_price_annually_usd_actual_stripe_id"] = StripeController().create_price(plan["plan_id"], "usd", plan["plan_price_annually_usd_actual"], "year")

        # if plan["plan_price_monthly_brl_actual"]:
        #     if not plan["plan_price_monthly_brl_actual_stripe_id"]:
        #         plan["plan_price_monthly_brl_actual_stripe_id"] = StripeController().create_price(plan["plan_id"], "brl", plan["plan_price_monthly_brl_actual"], "month")
        #     else:
        #         stripe_price = StripeController().get_price(plan["plan_price_monthly_brl_actual_stripe_id"])
        #         if str(stripe_price.unit_amount) != plan["plan_price_monthly_brl_actual"]:
        #             plan["plan_price_monthly_brl_actual_stripe_id"] = StripeController().create_price(plan["plan_id"], "brl", plan["plan_price_monthly_brl_actual"], "month")
        # if plan["plan_price_monthly_usd_actual"]:
        #     if not plan["plan_price_monthly_usd_actual_stripe_id"]:
        #         plan["plan_price_monthly_usd_actual_stripe_id"] = StripeController().create_price(plan["plan_id"], "usd", plan["plan_price_monthly_usd_actual"], "month")
        #     else:
        #         stripe_price = StripeController().get_price(plan["plan_price_monthly_usd_actual_stripe_id"])
        #         if str(stripe_price.unit_amount) != plan["plan_price_monthly_usd_actual"]:
        #             plan["plan_price_monthly_usd_actual_stripe_id"] = StripeController().create_price(plan["plan_id"], "usd", plan["plan_price_monthly_usd_actual"], "month")

        # StripeController().update_product(plan, type="plan")

        # Dynamo().put_entity(plan)

        # trial_plan = Dynamo().get_plan(plan["plan_id"] + "-trial")
        # if plan["plan_has_trial"]:
        #     if not trial_plan:
        #         trial_plan = plan
        #         trial_plan["pk"] = "plan#" + plan["plan_id"] + "-trial"
        #         trial_plan["sk"] = "plan#" + plan["plan_id"] + "-trial"
        #         trial_plan["plan_id"] = plan["plan_id"] + "-trial"
        #         trial_plan["plan_name_pt"] = plan["plan_name_pt"] + " Trial"
        #         trial_plan["plan_name_en"] = plan["plan_name_en"] + " Trial"
        #         trial_plan["plan_name_es"] = plan["plan_name_es"] + " Trial"

        #         trial_plan["plan_available_for_purchase"] = False
        #         trial_plan["plan_is_trial"] = True
        #         trial_plan["plan_has_trial"] = False
        #         Dynamo().put_entity(trial_plan)
        # else:
        #     if trial_plan:
        #         Dynamo().delete_entity(trial_plan)

        # return Http().redirect("backoffice_plans")
