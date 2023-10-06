from objects.AnalyticsNewUserRegistered import AnalyticsNewUserRegistered
from objects.AnalyticsAppOpening import AnalyticsAppOpening
from python_web_frame.backoffice_page import BackofficePage
from utils.AWS.Dynamo import Dynamo
from utils.utils.Date import Date
import json
import random
import time


class BackofficeAnalytics(BackofficePage):
    name = "Backoffice - Analytics"
    public = False
    bypass = False
    admin = True

    def render_get(self):
        html = super().parse_html()
        self.check_error_msg(html, self.error_msg)

        days_ago = self.path.get("analytics_date_filter", "7")
        days_ago_unix_delta = str(time.time() - (int(days_ago) * 86400))

        analytics_new_user_registereds = Dynamo().query_analytics("new_user_registered", days_ago_unix_delta)
        analytics_app_openings = Dynamo().query_analytics("new_user_registered", days_ago_unix_delta)
        analytics_new_user_registereds = self.add_dates_to_analytics(analytics_new_user_registereds)
        analytics_app_openings = self.add_dates_to_analytics(analytics_app_openings)

        dates = self.generate_dates(days_ago)

        new_user_registered_daily_amounts, new_user_registered_total_amounts = self.generate_analytics_data(dates, analytics_new_user_registereds)
        app_opening_daily_amounts, app_opening_total_amounts = self.generate_analytics_data(dates, analytics_app_openings)

        html.esc(days_ago + "_checked_val", 'selected="selected"')
        html.esc("dates_val", dates)

        html.esc("new_user_registered_daily_amounts_val", new_user_registered_daily_amounts)
        html.esc("new_user_registered_total_amounts_val", new_user_registered_total_amounts)

        html.esc("app_opening_daily_amounts_val", app_opening_daily_amounts)
        html.esc("app_opening_total_amounts_val", app_opening_total_amounts)

        # for x in range(100):
        #     analytics_new_user_registered = AnalyticsNewUserRegistered().__dict__
        #     analytics_new_user_registered["sk"] = str(time.time() - random.randint(1, 31536000))
        #     Dynamo().put_entity(analytics_new_user_registered)

        # for x in range(1000):
        #     analytics_app_opening = AnalyticsAppOpening().__dict__
        #     analytics_app_opening["sk"] = str(time.time() - random.randint(1, 31536000))
        #     Dynamo().put_entity(analytics_app_opening)

        return str(html)

    def render_post(self):
        return self.render_get()

    def generate_dates(self, days_ago):
        from datetime import datetime, timedelta

        today = datetime.today()
        date_list = [(today - timedelta(days=x)).strftime("%d/%m/%y") for x in range(int(days_ago))]
        return date_list[::-1]

    def generate_analytics_data(self, dates, analytics):
        daily_amounts_list = []
        total_amounts_list = []

        total_amounts = 0
        for date in dates:
            daily_amounts = 0
            for analytic in analytics:
                if analytic["date"] == date:
                    daily_amounts += 1

            total_amounts += daily_amounts
            daily_amounts_list.append(daily_amounts)
            total_amounts_list.append(total_amounts)

        return daily_amounts_list, total_amounts_list

    def add_dates_to_analytics(self, analytics):
        if analytics:
            for analytic in analytics:
                analytic["date"] = Date().format_unixtime_to_br_date(analytic["sk"])
        return analytics
