class EncodeDecode:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(EncodeDecode, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def encode_to_sha1(self, string):
        from hashlib import sha1

        hash_object = sha1(str.encode(string))
        return hash_object.hexdigest()

    def encode_to_sha256(self, string):
        from hashlib import sha256

        hash_object = sha256(str.encode(string))
        return hash_object.hexdigest()

    def encode_to_project_password(self, password, salt):
        return self.encode_to_sha1(salt + self.encode_to_sha1(salt + self.encode_to_sha1(password)))

    def encode_to_b64(self, string):
        import base64

        sample_string_bytes = str(string).encode("ascii")
        base64_bytes = base64.b64encode(sample_string_bytes)
        base64_string = base64_bytes.decode("ascii")
        return base64_string

    def decode_from_b64(self, string):
        import base64

        base64_bytes = str(string).encode("ascii")
        try:
            sample_string_bytes = base64.b64decode(base64_bytes)
            sample_string = sample_string_bytes.decode("ascii")
            return sample_string
        except:
            return None

    def encode_to_url(self, string):
        import urllib

        return urllib.parse.quote(string).replace("/", "%2F")

    def decode_from_url(self, string):
        import urllib

        return urllib.parse.unquote(string)
