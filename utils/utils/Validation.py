import os
import json


class Validation:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Validation, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def check_if_is_json(self, value):
        try:
            post_dict = json.loads(value)
            return isinstance(post_dict, dict)
        except:
            return False

    def check_if_date(self, date):
        import datetime

        try:
            datetime.datetime.strptime(date, "%Y-%m-%d")
            return True
        except:
            return False

    def check_if_is_number(self, number):
        try:
            int(number)
            return True
        except:
            return False

    def check_if_is_money(self, money):
        try:
            int(money.replace(".", "").replace(",", ""))
            return True
        except:
            return False

    def check_if_email(self, email):
        import re

        regex_email = r"([A-Za-z0-9]+[._])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"
        return bool(re.fullmatch(regex_email, email))

    def check_if_password(self, password):
        return 8 <= len(str(password)) <= 45

    def check_if_htmltime(self, html_time):
        import dateutil
        import datetime

        try:
            parsed_t = dateutil.parser.parse(html_time)
            t_in_seconds = parsed_t.timestamp()
            datetime.datetime.fromtimestamp(int(float(t_in_seconds))).strftime("%d/%m/%Y-%H:%M")
            return True
        except:
            return False

    def check_if_cpf(self, cpf):
        digits = [int(digit) for digit in cpf if digit.isdigit()]
        if len(digits) != 11 or len(set(digits)) == 1:
            return False
        sum_of_products = sum(a * b for a, b in zip(digits[0:9], range(10, 1, -1)))
        expected_digit = (sum_of_products * 10 % 11) % 10
        if digits[9] != expected_digit:
            return False
        sum_of_products = sum(a * b for a, b in zip(digits[0:10], range(11, 1, -1)))
        expected_digit = (sum_of_products * 10 % 11) % 10
        if digits[10] != expected_digit:
            return False
        return True

    def check_if_cnpj(self, cnpj, length_cnpj=14):
        import itertools

        if len(cnpj) != length_cnpj or cnpj in (c * length_cnpj for c in "1234567890"):
            return False
        cnpj_r = cnpj[::-1]
        for i in range(2, 0, -1):
            cnpj_enum = zip(itertools.cycle(range(2, 10)), cnpj_r[i:])
            dv = sum(int(x[1]) * x[0] for x in cnpj_enum) * 10 % 11
            if cnpj_r[i - 1 : i] != str(dv % 10):
                return False
        return True

    def check_if_phone(self, phone, country_alpha_2):
        import phonenumbers

        try:
            phone_number_obj = phonenumbers.parse(str(phone), country_alpha_2)
            return phonenumbers.is_valid_number(phone_number_obj)
        except phonenumbers.NumberParseException:
            return False

    def check_if_br_phone(self, phone):
        return self.check_if_phone(phone, "BR")

    def check_if_valid_url_param(self, param):
        import urllib.parse

        return param == urllib.parse.quote_plus(param)

    def check_if_local_env(self):
        return os.environ.get("AWS_EXECUTION_ENV") is None
