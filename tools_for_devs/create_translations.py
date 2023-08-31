from googletrans import Translator
import json
import os, sys
import codecs
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))


###########################
### CREATE TRANSLATIONS ###
###########################


html_source_path = os.path.normpath(os.getcwd() + "/src/html")
filtered_placeholders = ["Upload realizado com sucesso", "Copiado!", "Copiar", "Desfavoritar"]

translations = json.load(open("utils/translations.json", "r", encoding="utf-8"))
country_data = json.load(open("utils/utils/country_data.json", "r", encoding="utf-8"))

for key, val in country_data.items():
    filtered_placeholders.append(val["name"])

for sub_dirs in os.listdir(html_source_path):
    if sub_dirs[0] != ".":
        for file in os.listdir(html_source_path + "/" + sub_dirs):
            if file[0] != ".":
                if file == "_codes":
                    for _codes_file in os.listdir(html_source_path + "/" + sub_dirs + "/_codes"):
                        if _codes_file[0] != ".":
                            file_path = os.path.join(html_source_path + "/" + sub_dirs + "/_codes", _codes_file)
                            if os.path.isfile(file_path):
                                with codecs.open(file_path, "r", "utf-8-sig") as read_file:
                                    html_file = read_file.read()
                                ### GET PLACEHOLDERS STUFF ###
                                placeholders = html_file.split("{{")
                                for index, placeholder in enumerate(placeholders):
                                    if placeholder:
                                        placeholders[index] = placeholder.split("}}")[0]
                                for index, placeholder in enumerate(placeholders):
                                    if placeholder:
                                        if not "_val" in placeholder and not "html_" in placeholder and not "js." in placeholder and not "_" in placeholder and not "<" in placeholder and not "header" in placeholder and not "menu" in placeholder and not "footer" in placeholder and placeholder not in filtered_placeholders:
                                            filtered_placeholders.append(placeholder)
                    break
                else:
                    file_path = os.path.join(html_source_path + "/" + sub_dirs, file)
                    if os.path.isfile(file_path):
                        with codecs.open(file_path, "r", "utf-8-sig") as read_file:
                            html_file = read_file.read()
                        placeholders = html_file.split("{{")
                        for index, placeholder in enumerate(placeholders):
                            if placeholder:
                                placeholders[index] = placeholder.split("}}")[0]
                        for index, placeholder in enumerate(placeholders):
                            if placeholder:
                                if not "_val" in placeholder and not "html_" in placeholder and not "js." in placeholder and not "_" in placeholder and not "<" in placeholder and not "header" in placeholder and not "menu" in placeholder and not "footer" in placeholder and placeholder not in filtered_placeholders:
                                    filtered_placeholders.append(placeholder)


# py_source_path = "C:/Users/eugen/Desktop/Desenvolvimento/magipix-lambda/pages"
# for file in os.listdir(py_source_path):
#     if file[0] != ".":
#         file_path = os.path.join(py_source_path, file)
#         if os.path.isfile(file_path):
#             with codecs.open(file_path, "r", "utf-8-sig") as read_file:
#                 py_file = read_file.read()
#             ### GET PLACEHOLDERS STUFF ###
#             placeholders = py_file.split('self.render_get_with_error("')
#             for index, placeholder in enumerate(placeholders):
#                 if placeholder:
#                     placeholders[index] = placeholder.split('")')[0]
#             for index, placeholder in enumerate(placeholders):
#                 if placeholder:
#                     if not "from " in placeholder:
#                         filtered_placeholders.append(placeholder)


translator = Translator()

for placeholder in filtered_placeholders:
    if not "_val" in placeholder and not "html_" in placeholder and not "js." in placeholder and not "_" in placeholder and not "<" in placeholder and not "header" in placeholder and not "menu" in placeholder and not "footer" in placeholder:
        if placeholder not in translations:
            print("getting translation for: " + placeholder)
            translations[placeholder] = {"pt": placeholder, "es": "", "en": ""}
            translations[placeholder]["es"] = translator.translate(text=placeholder, src="pt", dest="es").text
            translations[placeholder]["en"] = translator.translate(text=placeholder, src="pt", dest="en").text


with open("utils/translations.json", "w", encoding="utf-8") as json_file:
    json.dump(translations, json_file, sort_keys=True, ensure_ascii=False, indent=4)

print("Create translations completed")
