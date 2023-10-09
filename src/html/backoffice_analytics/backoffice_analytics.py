from objects.AnalyticsNewUserRegistered import AnalyticsNewUserRegistered
from objects.AnalyticsAppOpening import AnalyticsAppOpening
from objects.AnalyticsSoftwareOpening import AnalyticsSoftwareOpening
from objects.AnalyticsMyAuginOpening import AnalyticsMyAuginOpening
from objects.AnalyticsUserRegisteredInLast30DaysAndPublished import AnalyticsUserRegisteredInLast30DaysAndPublished
from objects.AnalyticsNewProjectPublished import AnalyticsNewProjectPublished
from python_web_frame.backoffice_page import BackofficePage
from utils.AWS.Dynamo import Dynamo
from utils.utils.Date import Date
import random
import time

ANALYTIC_TYPES = ("new_user_registered", "app_opening", "software_opening", "my_augin_opening", "user_registered_in_last_30_days_and_published", "new_project_published")


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
        analytics_app_openings = Dynamo().query_analytics("app_opening", days_ago_unix_delta)
        analytics_software_openings = Dynamo().query_analytics("software_opening", days_ago_unix_delta)
        analytics_my_augin_opening = Dynamo().query_analytics("my_augin_opening", days_ago_unix_delta)

        analytics_new_user_registereds = self.add_dates_to_analytics(analytics_new_user_registereds)
        analytics_app_openings = self.add_dates_to_analytics(analytics_app_openings)
        analytics_software_openings = self.add_dates_to_analytics(analytics_software_openings)
        analytics_my_augin_opening = self.add_dates_to_analytics(analytics_my_augin_opening)

        dates = self.generate_dates(days_ago)
        html.esc("dates_val", dates)

        for analytic_name in ANALYTIC_TYPES:
            analytics_data = Dynamo().query_analytics(analytic_name, days_ago_unix_delta)
            formatted_analytics_data = self.add_dates_to_analytics(analytics_data)
            daily_data, total_data = self.generate_analytics_data(dates, formatted_analytics_data)

            html.esc(f"{analytic_name}_daily_amounts_val", daily_data)
            html.esc(f"{analytic_name}_total_amounts_val", total_data)

        ### TODO REMOVE BEFORE PROD

        for x in range(1):
            sample_data = AnalyticsNewUserRegistered().__dict__
            sample_data["sk"] = str(time.time() - random.randint(1, 31536000))
            Dynamo().put_entity(sample_data)

        for x in range(2):
            sample_data = AnalyticsAppOpening().__dict__
            sample_data["sk"] = str(time.time() - random.randint(1, 31536000))
            Dynamo().put_entity(sample_data)

        for x in range(3):
            sample_data = AnalyticsSoftwareOpening().__dict__
            sample_data["sk"] = str(time.time() - random.randint(1, 31536000))
            Dynamo().put_entity(sample_data)

        for x in range(4):
            sample_data = AnalyticsMyAuginOpening().__dict__
            sample_data["sk"] = str(time.time() - random.randint(1, 31536000))
            Dynamo().put_entity(sample_data)

        for x in range(5):
            sample_data = AnalyticsUserRegisteredInLast30DaysAndPublished().__dict__
            sample_data["sk"] = str(time.time() - random.randint(1, 31536000))
            Dynamo().put_entity(sample_data)

        for x in range(10):
            sample_data = AnalyticsNewProjectPublished().__dict__
            sample_data["sk"] = str(time.time() - random.randint(1, 31536000))
            Dynamo().put_entity(sample_data)

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
