from utils.AWS.Dynamo import Dynamo
import time


class AnalyticsUserRegisteredInLast30DaysAndPublished:
    def __init__(self) -> None:
        self.pk = "analytics_user_registered_in_last_30_days_and_published#"
        self.sk = str(time.time())


def check_and_save_user_registered_in_last_30d_and_published_analytics():
    Dynamo().put_entity(AnalyticsUserRegisteredInLast30DaysAndPublished().__dict__)
