from datetime import datetime
from utils.Config import lambda_constants
from utils.Code import Code


class Date:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Date, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def format_to_ago_str_time(self, unix_time):
        from datetime import datetime

        now = datetime.now()
        past = datetime.fromtimestamp(float(unix_time))
        delta = now - past

        seconds = delta.total_seconds()
        if seconds < 60:
            return Code().translate("1 segundo atrás") if seconds <= 1 else str(int(seconds)) + " " + Code().translate("segundos atrás")
        minutes = seconds // 60
        if minutes < 60:
            return Code().translate("1 minuto atrás") if minutes == 1 else str(int(minutes)) + " " + Code().translate("minutos atrás")
        hours = minutes // 60
        if hours < 24:
            return Code().translate("1 hora atrás") if hours == 1 else str(int(hours)) + " " + Code().translate("horas atrás")
        days = hours // 24
        if days < 30:
            return Code().translate("1 dia atrás") if days == 1 else str(int(days)) + " " + Code().translate("dias atrás")
        months = days // 30
        if months < 12:
            return Code().translate("1 mês atrás") if months == 1 else str(int(months)) + " " + Code().translate("meses atrás")
        years = months // 12
        return Code().translate("1 ano atrás") if years == 1 else str(int(years)) + " " + Code().translate("anos atrás")

    def format_to_str_time(self, unix_time, without_year=False):
        dt_object = datetime.fromtimestamp(float(unix_time))
        if without_year:
            formatted_date = dt_object.strftime("%b %d")
        else:
            formatted_date = dt_object.strftime("%b %d, %Y")
        if lambda_constants["current_language"] == "en":
            return formatted_date
        if lambda_constants["current_language"] == "es":
            return formatted_date.replace("Jan", "Ene").replace("Apr", "Abr").replace("May", "Mai").replace("Aug", "Ago").replace("Dec", "Dic")
        else:
            return formatted_date.replace("Feb", "Fev").replace("Apr", "Abr").replace("May", "Mai").replace("Aug", "Ago").replace("Sep", "Set").replace("Oct", "Out").replace("Dec", "Dez")

    def get_current_br_month(self):
        import datetime

        br_months = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        current_int_month = datetime.datetime.now().strftime("%m")
        return br_months[int(current_int_month) - 1]

    def add_days_to_current_unix_time(self, days):
        import time

        return float(time.time() + (int(days) * 86400))

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

    def format_unixtime_to_br_date(self, unix_time):
        return self.format_unixtime(int(float(unix_time)) - 10800, "%d/%m/%y")

    def format_unixtime_to_date(self, unix_time):
        return self.format_unixtime(int(float(unix_time)), "%d/%m/%y")

    def format_unixtime_to_br_datetime(self, unix_time):
        return self.format_unixtime(int(float(unix_time)) - 10800, "%d/%m/%y %H:%M")

    def format_unixtime_to_navigator_datetime(self, unix_time):
        return self.format_unixtime(int(float(unix_time)) - 10800, "%Y/%m/%d %H:%M")

    def format_unixtime_to_inter_datetime(self, unix_time):
        return self.format_unixtime(int(float(unix_time)), "%d/%m/%y - %H:%M") + " GMT 0"

    def format_unixtime_to_time(self, unix_time):
        if not unix_time:
            return ""
        return self.format_unixtime(int(float(unix_time)), "%H:%M:%S")
