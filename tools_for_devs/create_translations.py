from googletrans import Translator
import json
import os, sys
import codecs
import os
import re


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))


###########################
### CREATE TRANSLATIONS ###
###########################


html_source_path = os.path.normpath(os.getcwd() + "/src/html")
api_source_path = os.path.normpath(os.getcwd() + "/api")

filtered_placeholders = [
    "Downgrade de plano",
    "1 segundo atrás",
    "1 minuto atrás",
    "1 hora atrás",
    "1 dia atrás",
    "1 mês atrás",
    "1 ano atrás",
    "segundos atrás",
    "minutos atrás",
    "horas atrás",
    "dias atrás",
    "meses atrás",
    "anos atrás",
    "Não foi possível encontrar esta pasta",
    "Não foi possível encontrar este cupom",
    "Não foi possível encontrar esta ordem",
    "Não foi possível decoficar o email",
    "Não foi possível encontrar esse código de validação",
    "Não foi possível encontrar este projeto",
    "Não foi possível encontrar este elemento",
    "Augin - Solicitação de troca de email",
    "Augin - Seu código de verficação chegou",
    "Augin - Seu código de verficação é ",
    "Augin - Solicitação de troca de email código ",
    "Augin - Sua senha foi alterada",
    "Faça um upgrade para aumentar esse limite.",
    "Reprocessar",
    "Reprocessando...",
    "O arquivo .zip se encontra trancado com senha.",
    "É necessário atualizar os seus dados para processeguir na compra",
    "Ilimitado",
    "Já existe um projeto com este arquivo chamado: ",
    "O projeto excede o tamanho máximo da suportado pela sua conta.",
    "Algum arquivo dentro do .zip excede o tamanho máximo da suportado pela sua conta.",
    "Incompleta/Expirada",
    "boleto",
    "Incompleta",
    "Sua compra está sendo reembolsada",
    "Não Emitida",
    "Emitida",
    "Cancelada",
    "Ativa",
    "Cancelada",
    "O .zip contem arquivos duplicados.",
    "O projeto excede o tamanho máximo de 1Gb.",
    "Algum arquivo dentro do .zip excede o tamanho máximo de 1Gb.",
    "Os formartos suportados de IFC são: IFC2x3 e IFC4.",
    "Algum arquivo dentro do .zip não está dentro dos nossos formatos suportados: suportados de IFC são: IFC2x3 e IFC4.",
    "Este mesmo arquivo já se encontra na fila de processamento.",
    "Incompleto",
    "Pago",
    "Não autorizado",
    "Cartão expirado",
    "Cartão bloqueado",
    "Cartão cancelado",
    "Problemas no cartão",
    "Excedeu o limite de tentativas",
    "Reembolsado",
    "Cartão de crédito",
    "Boleto",
    "Pix",
    "mensalmente",
    "anualmente",
    "Cartão de crédito",
    "Boleto",
    "Pix",
    "Pagamento Direto",
    "Creditado pela Augin",
    "Você precisa estar logado para acessar esta página",
    "Você não possui as credenciais para acessar esta página",
    "Ocultar senha",
    "Exibir senha",
    "mês",
    "Cobrado mensalmente",
    "ano",
    "Cobrado anualmente",
    "indisponível",
    "único",
    "múltiplo",
    "Indisponível",
    "Único",
    "Múltiplo",
    "Um ou mais de seus arquivos possui um erro, por favor exclua os arquivos com erro para realizar o processamento",
    "Favoritos",
    "Não Federados",
    "Air Conditioning",
    "Architecture",
    "Electric",
    "Structural",
    "Executive",
    "Gas",
    "Hydraulics",
    "Fire",
    "Infrastructure",
    "Interiors",
    "Federated",
    "Others",
    "Verificando arquivos...",
    "É necessário selecionar para qual pasta será movido o projeto atual.",
    "Upload realizado com sucesso.",
    "Copiado!",
    "Copiar",
    "Desfavoritar",
    "Mostrar senha.",
    "Ocultar senha.",
    "Ícone de seta para baixo",
    "Ícone de seta para cima",
    "É necessário selecionar o projeto que será usado para atualizar o projeto atual.",
    "O projeto excede o tamanho máximo de 1Gb.",
    "Algum arquivo dentro do .zip excede o tamanho máximo de 1Gb.",
    "Arquivo IFC ou FBX encontrado porém se não é válido.",
    "Algum arquivo dentro do .zip é inválido.",
    "Os formartos suportados de IFC são: IFC2x3 e IFC4.",
    "Algum arquivo dentro do .zip não está dentro dos nossos formatos suportados: suportados de IFC são: IFC2x3 e IFC4.",
]
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
                        if not ".py" in file:
                            placeholders = html_file.split("{{")
                            for index, placeholder in enumerate(placeholders):
                                if placeholder:
                                    placeholders[index] = placeholder.split("}}")[0]
                            for index, placeholder in enumerate(placeholders):
                                if placeholder:
                                    if not "_val" in placeholder and not "html_" in placeholder and not "js." in placeholder and not "_" in placeholder and not "<" in placeholder and not "header" in placeholder and not "menu" in placeholder and not "footer" in placeholder and placeholder not in filtered_placeholders:
                                        filtered_placeholders.append(placeholder)
                        else:
                            pattern = r'self\.render_get_with_error\("([^"]*)"\)'
                            placeholders = re.findall(pattern, html_file)
                            filtered_placeholders.extend(placeholders)


for file in os.listdir(api_source_path):
    if os.path.isfile(api_source_path + "/" + file):
        with codecs.open(api_source_path + "/" + file, "r", "utf-8-sig") as read_file:
            html_file = read_file.read()
        pattern = r'return \{"error": "([^"]*)"\}'
        result = re.findall(pattern, html_file)
        filtered_placeholders.extend(result)


translator = Translator()

# translated_keys = [
#     "Aruba",
#     "Afghanistan",
#     "Angola",
#     "Anguilla",
#     "Åland Islands",
#     "Albania",
#     "Andorra",
#     "United Arab Emirates",
#     "Argentina",
#     "Armenia",
#     "American Samoa",
#     "Antarctica",
#     "French Southern Territories",
#     "Antigua and Barbuda",
#     "Australia",
#     "Austria",
#     "Azerbaijan",
#     "Burundi",
#     "Belgium",
#     "Benin",
#     "Bonaire, Sint Eustatius and Saba",
#     "Burkina Faso",
#     "Bangladesh",
#     "Bulgaria",
#     "Bahrain",
#     "Bahamas",
#     "Bosnia and Herzegovina",
#     "Saint Barthélemy",
#     "Belarus",
#     "Belize",
#     "Bermuda",
#     "Bolivia, Plurinational State of",
#     "Brazil",
#     "Barbados",
#     "Brunei Darussalam",
#     "Bhutan",
#     "Bouvet Island",
#     "Botswana",
#     "Central African Republic",
#     "Canada",
#     "Cocos (Keeling) Islands",
#     "Switzerland",
#     "Chile",
#     "China",
#     "Côte d'Ivoire",
#     "Cameroon",
#     "Congo, The Democratic Republic of the",
#     "Congo",
#     "Cook Islands",
#     "Colombia",
#     "Comoros",
#     "Cabo Verde",
#     "Costa Rica",
#     "Cuba",
#     "Curaçao",
#     "Christmas Island",
#     "Cayman Islands",
#     "Cyprus",
#     "Czechia",
#     "Germany",
#     "Djibouti",
#     "Dominica",
#     "Denmark",
#     "Dominican Republic",
#     "Algeria",
#     "Ecuador",
#     "Egypt",
#     "Eritrea",
#     "Western Sahara",
#     "Spain",
#     "Estonia",
#     "Ethiopia",
#     "Finland",
#     "Fiji",
#     "Falkland Islands (Malvinas)",
#     "France",
#     "Faroe Islands",
#     "Micronesia, Federated States of",
#     "Gabon",
#     "United Kingdom",
#     "Georgia",
#     "Guernsey",
#     "Ghana",
#     "Gibraltar",
#     "Guinea",
#     "Guadeloupe",
#     "Gambia",
#     "Guinea-Bissau",
#     "Equatorial Guinea",
#     "Greece",
#     "Grenada",
#     "Greenland",
#     "Guatemala",
#     "French Guiana",
#     "Guam",
#     "Guyana",
#     "Hong Kong",
#     "Heard Island and McDonald Islands",
#     "Honduras",
#     "Croatia",
#     "Haiti",
#     "Hungary",
#     "Indonesia",
#     "Isle of Man",
#     "India",
#     "British Indian Ocean Territory",
#     "Ireland",
#     "Iran, Islamic Republic of",
#     "Iraq",
#     "Iceland",
#     "Israel",
#     "Italy",
#     "Jamaica",
#     "Jersey",
#     "Jordan",
#     "Japan",
#     "Kazakhstan",
#     "Kenya",
#     "Kyrgyzstan",
#     "Cambodia",
#     "Kiribati",
#     "Saint Kitts and Nevis",
#     "Korea, Republic of",
#     "Kuwait",
#     "Lao People's Democratic Republic",
#     "Lebanon",
#     "Liberia",
#     "Libya",
#     "Saint Lucia",
#     "Liechtenstein",
#     "Sri Lanka",
#     "Lesotho",
#     "Lithuania",
#     "Luxembourg",
#     "Latvia",
#     "Macao",
#     "Saint Martin (French part)",
#     "Morocco",
#     "Monaco",
#     "Moldova, Republic of",
#     "Madagascar",
#     "Maldives",
#     "Mexico",
#     "Marshall Islands",
#     "North Macedonia",
# ]

# for key, val in country_data.items():
#     if val["name"] not in translated_keys:
#         print("Getting translation for " + val["name"])
#         translations[val["name"]] = {"pt": "", "es": "", "en": val["name"]}
#         translations[val["name"]]["pt"] = translator.translate(text=placeholder, src="en", dest="pt").text
#         translations[val["name"]]["es"] = translator.translate(text=placeholder, src="en", dest="es").text
#         translated_keys.append(val["name"])

for placeholder in filtered_placeholders:
    if not "_val" in placeholder and not "html_" in placeholder and not "js." in placeholder and not "_" in placeholder and not "<" in placeholder and not "header" in placeholder and not "menu" in placeholder and not "footer" in placeholder:
        if placeholder not in translations:
            print("getting translation for: " + placeholder)
            translations[placeholder] = {"pt": placeholder, "es": "", "en": ""}
            translations[placeholder]["es"] = translator.translate(text=placeholder, src="pt", dest="es").text
            translations[placeholder]["en"] = translator.translate(text=placeholder, src="pt", dest="en").text

        if placeholder[0].isupper():
            translations[placeholder]["pt"] = translations[placeholder]["pt"][0].upper() + translations[placeholder]["pt"][1:]
            translations[placeholder]["es"] = translations[placeholder]["es"][0].upper() + translations[placeholder]["es"][1:]
            translations[placeholder]["en"] = translations[placeholder]["en"][0].upper() + translations[placeholder]["en"][1:]
        else:
            translations[placeholder]["pt"] = translations[placeholder]["pt"][0].lower() + translations[placeholder]["pt"][1:]
            translations[placeholder]["es"] = translations[placeholder]["es"][0].lower() + translations[placeholder]["es"][1:]
            translations[placeholder]["en"] = translations[placeholder]["en"][0].lower() + translations[placeholder]["en"][1:]

for key, translation in translations.items():
    translation["pt"] = translation["pt"].replace("augin", "Augin").replace("AUGIN", "Augin")
    translation["es"] = translation["es"].replace("augin", "Augin").replace("AUGIN", "Augin")
    translation["en"] = translation["en"].replace("augin", "Augin").replace("AUGIN", "Augin")

with open("utils/translations.json", "w", encoding="utf-8") as json_file:
    json.dump(translations, json_file, sort_keys=True, ensure_ascii=False, indent=4)

print("Create translations completed")
