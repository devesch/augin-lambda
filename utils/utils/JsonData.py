import json

country_data = None
country_phone_code = None


class JsonData:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(JsonData, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def get_country_data(self):
        global country_data
        if country_data:
            return country_data
        country_data = json.load(open("utils/utils/country_data.json", "r", encoding="utf-8"))
        return country_data

    def get_country_phone_code(self):
        global country_phone_code
        if country_phone_code:
            return country_phone_code
        country_phone_code = json.load(open("utils/utils/country_phone_codes.json", "r", encoding="utf-8"))
        return country_phone_code

    def translate_country_alpha_2_to_country_name(self, country_alpha_2):
        return self.get_country_data()[country_alpha_2.upper()]["name"]
