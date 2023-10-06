from objects.AnalyticsNewUserRegistered import AnalyticsNewUserRegistered
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

        days_ago = "30"
        days_ago_unix_delta = str(time.time() - (int(days_ago) * 86400))

        analytics_new_user_registereds = Dynamo().query_analytics("new_user_registered", days_ago_unix_delta)
        analytics_new_user_registereds = self.add_dates_to_analytics_new_user_registereds(analytics_new_user_registereds)

        new_user_registered_dates, new_user_registered_daily_amounts, new_user_registered_total_amounts = self.generate_analytics_new_user_registereds_data(analytics_new_user_registereds, days_ago)

        html.esc("new_user_registered_dates_val", new_user_registered_dates)
        html.esc("new_user_registered_daily_amounts_val", new_user_registered_daily_amounts)
        html.esc("new_user_registered_total_amounts_val", new_user_registered_total_amounts)
        # for x in range(50):
        #     analytics_new_user_registered = AnalyticsNewUserRegistered().__dict__
        #     analytics_new_user_registered["sk"] = str(time.time() - random.randint(1, 31536000))
        #     Dynamo().put_entity(analytics_new_user_registered)

        return str(html)

    def render_post(self):
        return self.render_get()

    def generate_analytics_new_user_registereds_data(self, analytics_new_user_registereds, days_ago):
        from datetime import datetime, timedelta

        new_user_registered_dates = []
        new_user_registered_daily_amounts = []
        new_user_registered_total_amounts = []

        today = datetime.today()
        date_list = [(today - timedelta(days=x)).strftime("%d/%m/%y") for x in range(int(days_ago))]
        new_user_registered_dates = date_list[::-1]

        total_amounts = 0
        for date in new_user_registered_dates:
            daily_amounts = 0
            for analytics in analytics_new_user_registereds:
                if analytics["date"] == date:
                    daily_amounts += 1

            total_amounts += daily_amounts
            new_user_registered_daily_amounts.append(daily_amounts)
            new_user_registered_total_amounts.append(total_amounts)

        return new_user_registered_dates, new_user_registered_daily_amounts, new_user_registered_total_amounts

    def add_dates_to_analytics_new_user_registereds(self, analytics_new_user_registereds):
        if analytics_new_user_registereds:
            for analytics in analytics_new_user_registereds:
                analytics["date"] = Date().format_unixtime_to_br_date(analytics["sk"])
        return analytics_new_user_registereds
