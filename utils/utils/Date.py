from datetime import datetime


class Date:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Date, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def format_to_str_time(self, created_at):
        dt_object = datetime.fromtimestamp(float(created_at))
        formatted_date = dt_object.strftime("%b %d, %Y")
        return formatted_date

    def get_current_br_month(self):
        import datetime

        br_months = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        current_int_month = datetime.datetime.now().strftime("%m")
        return br_months[int(current_int_month) - 1]

    def add_days_to_current_unix_time(self, days):
        import time

        return float(time.time() + (int(days) * 86.400))

    def generate_delta_time_from_unix_time(self, unix_time):
        import time

        return int(time.time()) - int(float(unix_time))

    def format_unixtime_to_billingtime(self, unix_time):
        return self.format_unixtime(int(float(unix_time)), "%Y-%m-%dT%H:%M:%S") + ".000-02:00"

    def format_total_time_to_hh_mm_ss(self, time):
        time = str(round((time.real * 10) * (6)))
        while len(time) < 6:
            time = "0" + time
        return "{}:{}:{}".format(time[:2], time[2:4], time[4:6])

    def format_html_time_to_unixtime(self, html_time):
        import dateutil

        parsed_t = dateutil.parser.parse(html_time)
        t_in_seconds = parsed_t.timestamp()
        return str(round(int(t_in_seconds)))

    def format_unixtime_to_html_time(self, unix_time):
        return self.format_unixtime(int(float(unix_time)), "%Y-%m-%d")

    def format_unixtime(self, unix_time, format_str):
        import datetime

        return datetime.datetime.fromtimestamp(int(float(unix_time))).strftime(format_str)

    def format_unixtime_to_br_datetime(self, unix_time):
        return self.format_unixtime(int(float(unix_time)) - 10800, "%d/%m/%y %H:%M")

    def format_unixtime_to_navigator_datetime(self, unix_time):
        return self.format_unixtime(int(float(unix_time)) - 10800, "%Y/%m/%d %H:%M")

    def format_unixtime_to_inter_datetime(self, unix_time):
        return self.format_unixtime(int(float(unix_time)), "%d/%m/%y - %H:%M") + " GMT 0"

    def format_unixtime_to_time(self, unix_time):
        return self.format_unixtime(int(float(unix_time)), "%H:%M:%S")
