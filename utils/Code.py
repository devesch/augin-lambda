from utils.Config import lambda_constants
import json

translations = None
code = {}


class Code:
    parts = []
    placeholders = {}
    replaced_placeholders = {}
    nested_placeholders = False
    code = ""
    common_changes = {}
    filename = None

    def __init__(self, filename=""):
        if filename:
            self.filename = filename
            import codecs

            with codecs.open("src/html/" + filename + ".html", "r", "utf-8-sig") as read_file:
                self.code = read_file.read()
                self.clean_new_lines()
                # self.clean_double_spaces()
                self.parse()
                return None

    def clean_new_lines(self):
        self.code = self.code.replace("\n", "")

    def clean_double_spaces(self):
        self.code = self.code.replace("  ", "")
        self.code = self.code.replace("  ", "")
        self.code = self.code.replace("  ", "")
        self.code = self.code.replace("  ", "")

    def parse(self):
        self.parts = []
        self.placeholders = {}
        if "{{{{" in self.code or "}}}}" in self.code:
            self.nested_placeholders = True
        parts = self.code.split("{{")
        for part in parts:
            if part == "":
                continue
            if not "}}" in part:
                self.parts.append(part)
            else:
                placeholder_text_splited = part.split("}}")
                if len(placeholder_text_splited) == 2:
                    placeholder_text, rest = placeholder_text_splited
                else:
                    placeholder_text = placeholder_text_splited[0]
                    rest = "".join(placeholder_text_splited[1:])
                # check if placeholder is a constant
                constant = lambda_constants.get(placeholder_text.replace("_val", ""))
                if constant:
                    self.parts.append(constant)
                    self.parts.append(rest)
                    continue
                part = placeholder_text.replace("}}", "")
                part_get = self.placeholders.get(part)
                if part_get:
                    self.placeholders[part].append(len(self.parts))
                else:
                    self.placeholders[part] = [len(self.parts)]
                self.parts.append(part)
                if rest != "":
                    self.parts.append(rest)
        for common_change in self.common_changes:
            self.esc(common_change, self.common_changes[common_change])

    def esc(self, placeholder, value):
        placeholder_index = self.placeholders.get(placeholder)
        if placeholder_index:
            for pi in placeholder_index:
                self.parts[pi] = str(value)
            self.placeholders[placeholder] = []

    def __str__(self):
        for placeholder_list in self.placeholders:
            placeholder_indexes = self.placeholders.get(placeholder_list)
            if len(placeholder_indexes) == 0:
                continue
            if self.common_changes:
                found_placeholder_in_common_changes = self.common_changes.get(placeholder_list.replace("_val", ""))
                if found_placeholder_in_common_changes:
                    self.esc(placeholder_list, found_placeholder_in_common_changes)
                    continue
                else:
                    found_placeholder_in_common_changes = self.common_changes.get(placeholder_list)
                    if found_placeholder_in_common_changes:
                        self.esc(placeholder_list, found_placeholder_in_common_changes)
                        continue
            translations = self.get_translations()
            for placeholder_position in self.placeholders[placeholder_list]:
                if self.parts[placeholder_position] in translations:
                    self.parts[placeholder_position] = translations[self.parts[placeholder_position]][lambda_constants["current_language"]]
                else:
                    self.parts[placeholder_position] = ""
        return "".join(self.parts)

    def get_translations(self):
        global translations

        if translations:
            return translations
        translations = json.load(open("utils/translations.json", "r", encoding="utf-8"))
        return translations

    def translate(self, key, lang=""):
        if not lang:
            lang = lambda_constants["current_language"]
        return self.get_translations().get(key)[lang]
