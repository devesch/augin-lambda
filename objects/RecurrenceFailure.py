import time


class RecurrenceFailure:
    def __init__(self, user_id, order_id) -> None:
        self.pk = "user#" + user_id
        self.sk = "recurrence_failure#" + order_id

        self.recurrence_failure_user_id = user_id
        self.recurrence_failure_id = order_id
        self.recurrence_failure_order_id = order_id

        self.created_at = str(time.time())
        self.entity = "recurrence_failure"
