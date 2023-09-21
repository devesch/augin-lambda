from utils.Code import Code


class StrFormat:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(StrFormat, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def format_status(self, status):
        if status == "active":
            return "Ativa"
        if status == "canceled":
            return "Cancelada"
        else:
            raise Exception("TODO")

    def format_to_payment_method(self, payment_method):
        if payment_method == "card":
            return Code().translate("Cartão de crédito")
        if payment_method == "boleto":
            return Code().translate("Boleto")
        if payment_method == "pix":
            return Code().translate("Pix")
        else:
            raise Exception("TODO")

    def format_recurrency(self, recurrency):
        if recurrency == "monthly":
            return Code().translate("mensalmente")
        if recurrency == "annually":
            return Code().translate("anualmente")
        else:
            raise Exception("TODO")

    def format_bytes_to_megabytes(self, bytes_value):
        return int(bytes_value) / (1024 * 1024)

    def format_currency_to_symbol(self, currency):
        if currency.lower() == "brl":
            return "R$"
        if currency.lower() == "usd":
            return "U$"
        else:
            raise Exception("TODO")

    def format_snakecase_to_title(self, string):
        return " ".join(x.capitalize() or "_" for x in string.split("_"))

    def format_snakecase_to_camelcase(self, string):
        return "".join(x.capitalize() or "_" for x in string.split("_"))

    def format_camelcase_to_snakecase(self, string):
        import re

        return re.sub(r"(?<!^)(?=[A-Z])", "_", string).lower()

    def format_to_numbers(self, string):
        digits = [char for char in string if char.isdigit()]
        return "".join(digits)

    def format_to_letters(self, string):
        non_url_safe = ["<", ">", "*", "!", '"', "#", "$", "%", "&", "+", ",", "/", ":", ";", "=", "?", "@", "[", "\\", "]", "^", "`", "{", "|", "}", "~", "'", "(", ")"]
        return "".join(c for c in string if c not in non_url_safe and not c.isdigit())

    def format_to_zip_code(self, postal_code):
        return "{}{}-{}".format(postal_code[:2], postal_code[2:5], postal_code[5:])

    def format_to_phone(self, mobile_phone_number):
        return "({}) {}-{}".format(mobile_phone_number[:2], mobile_phone_number[2:7], mobile_phone_number[7:])

    def format_to_international_phone(self, alpha_2_country, mobile_phone_number):
        return "(" + self.get_country_phone_code()[alpha_2_country] + ") " + mobile_phone_number

    def format_to_cpf(self, cpf):
        if cpf:
            return "{}.{}.{}-{}".format(cpf[:3], cpf[3:6], cpf[6:9], cpf[9:11])
        return ""

    def format_to_cnpj(self, cnpj):
        if cnpj:
            return "{}.{}.{}/{}-{}".format(cnpj[:2], cnpj[2:5], cnpj[5:8], cnpj[8:12], cnpj[12:])
        return ""

    def format_to_money(self, money, currency, big=False):
        if currency == "brl":
            return self.format_to_brl_money(money, big)
        elif currency == "usd":
            return self.format_to_usd_money(money, big)

    def format_to_billing_money(self, money):
        money = str(money).replace(".", "").replace(",", "")
        if money == "0":
            return "0.00"
        return f"{money[:-2]}.{money[-2:]}"

    def format_to_brl_money(self, money, big=False):
        money = str(money).replace(".", "").replace(",", "")
        if money == "0":
            if big:
                return "0"
            return "0,00"
        formatted_money = f"{money[:-5]}.{money[-5:-2]},{money[-2:]}" if len(money) >= 6 else f"{money[:-2]},{money[-2:]}"
        if big:
            return formatted_money[:-3]
        return formatted_money

    def format_to_usd_money(self, money, big=False):
        money = str(money).replace(".", "").replace(",", "")
        if money == "0":
            if big:
                return "0"
            return "0.00"
        formatted_money = f"{money[:-5]},{money[-5:-2]}.{money[-2:]}" if len(money) >= 6 else f"{money[:-2]}.{money[-2:]}"
        if big:
            return formatted_money[:-3]
        return formatted_money

    def format_to_ddd(self, ddd_number):
        return "({})".format(ddd_number[:2])

    def format_to_phone_number_without_ddd(self, phone_number):
        return "{}-{}".format(phone_number[:4], phone_number[4:])
