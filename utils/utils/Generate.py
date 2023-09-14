from utils.AWS.S3 import S3
from utils.utils.Validation import Validation
from utils.Config import tmp_path


class Generate:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Generate, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def generate_qr_code(self, code, bucket, key=None):
        import qrcode

        file_path = tmp_path + "qrcode.png" if Validation().check_if_local_env() else tmp_path + "qrcode.png"

        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=2)
        qr.add_data(code)
        qr.make(fit=True)
        qr_pil = qr.make_image(fill_color="black", back_color="white")

        qr_pil.save(file_path)
        key = key or code
        S3().upload_file(bucket, key, file_path)

    def generate_image_format_from_user_agent(self, user_agent):
        # browser_image_support = {
        #     "Chrome": {"1": "jpeg", "4": "png", "32": "webp", "85": "avif"},
        #     "Edge": {"1": "jpeg", "12": "png", "18": "webp"},
        #     "Safari": {"3": "png", "16": "webp"},
        #     "Mobile Safari": {"1": "jpeg", "3": "png", "14": "webp", "16": "avif"},
        #     "Samsung Internet": {"1": "png", "4": "webp", "14": "avif"},
        #     "Firefox": {"2": "png", "65": "webp", "93": "avif"},
        #     "Firefox Mobile": {"1": "jpeg", "106": "avif"},
        #     "Opera": {"1": "jpeg", "10": "png", "19": "webp", "71": "avif"},
        #     "Opera Mobile": {"1": "jpeg", "12": "webp", "72": "avif"},
        #     "IE": {"93": "avif"},
        #     "UC Browser": {"1": "jpeg", "13": "webp"},
        #     "Android": {"1": "jpeg", "2": "png", "4": "webp", "107": "avif"},
        #     "Baiduspider": {"1": "jpeg", "13": "avif"},
        # }

        browser_image_support = {
            "Chrome": {1: "jpeg", 4: "png", 32: "webp"},
            "Edge": {1: "jpeg", 12: "png", 18: "webp"},
            "Safari": {3: "png", 16: "webp"},
            "Mobile Safari": {1: "jpeg", 3: "png", 14: "webp"},
            "Samsung Internet": {1: "png", 4: "webp"},
            "Firefox": {2: "png", 65: "webp"},
            "Firefox Mobile": {1: "jpeg", 106: "webp"},
            "Opera": {1: "jpeg", 10: "png", 19: "webp"},
            "Opera Mobile": {1: "jpeg", 12: "webp"},
            "IE": {93: "png"},
            "UC Browser": {1: "jpeg", 13: "webp"},
            "Android": {1: "jpeg", 2: "png", 4: "webp"},
            "Baiduspider": {1: "jpeg", 13: "webp"},
        }

        import user_agents

        browser_family = ""
        browser_version = ""

        try:
            obj_user_agent = user_agents.parse(user_agent)
            browser_family = obj_user_agent.browser.family
            browser_version = obj_user_agent.browser.version[0]
        except:
            return "jpeg"

        if "Chrome" in browser_family:
            browser_family = "Chrome"

        browser_dict = browser_image_support.get(browser_family)
        if not browser_dict:
            return "jpeg"
        best_image = browser_dict.get(browser_version)
        if best_image:
            return best_image
        for version in browser_dict:
            if version <= browser_version:
                best_image = browser_dict[version]
        return best_image if best_image else "jpeg"

    @staticmethod
    def generate_font_from_user_agent(user_agent):
        import user_agents

        font_family = {
            "Chrome": {4: "ttf", 5: "woff", 36: "woff2"},
            "Edge": {12: "woff", 14: "woff2"},
            "Safari": {3: "ttf", 5: "woff", 12: "woff2"},
            "Mobile Safari": {4: "ttf", 5: "woff", 10: "woff2"},
            "Samsung Internet": {4: "woff2"},
            "Firefox": {3: "ttf", 39: "woff2"},
            "Firefox Mobile": {106: "woff2"},
            "Opera": {10: "ttf", 23: "woff2"},
            "Opera Mobile": {12: "woff", 64: "woff2"},
            "IE": {9: "woff"},
            "UC Browser": {13: "woff2"},
            "Android": {106: "woff2"},
            "Baiduspider": {13: "woff2"},
        }

        try:
            obj_user_agent = user_agents.parse(user_agent)
            browser_family = obj_user_agent.browser.family
            browser_version = obj_user_agent.browser.version[0]
        except:
            return "ttf"

        if "Chrome" in browser_family:
            browser_family = "Chrome"
        browser_dict = font_family.get(browser_family, {})
        best_font = browser_dict.get(browser_version)
        if best_font:
            return best_font
        for version, font in browser_dict.items():
            if version <= browser_version:
                best_font = font
        return best_font or "ttf"

    def generate_salt(self, salt_length=32):
        import random

        salt_available_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        return "".join(random.choice(salt_available_chars) for _ in range(salt_length))

    def generate_int_id(self):
        import random

        return str(random.randint(100000000, 999999999))

    def generate_short_id(self):
        from uuid import uuid4

        return str(uuid4()).split("-")[-1]

    def generate_long_id(self):
        from uuid import uuid4

        return str(uuid4())
