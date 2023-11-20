snakecase_page_name = "search_show_10_models_by_date"
public = False
bypass = False


import os
import os.path
import sys
import codecs

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from utils.utils.Http import Http, lambda_constants

inputs = []
default_inputs = []
list_table = {}
list_thumbs = {}
inputs = [
    # {"input_name": "email_subject", "input_placeholder": "Assunto do Email", "input_js": "", "input_type": "text", "input_min_lenght": "", "input_max_lenght": "60", "input_render_with_py_function": "", "input_py_verification": "", "input_required": True, "input_sex": "M"},
    # {"input_name": "email_text", "input_placeholder": "Texto do Email", "input_js": "", "input_type": "text", "input_min_lenght": "", "input_max_lenght": "60", "input_render_with_py_function": "", "input_py_verification": "", "input_required": True, "input_sex": "M"},
    # {"input_name": "email_file", "input_placeholder": "Arquivo", "input_js": "uploadFile", "input_type": "file", "input_min_lenght": "", "input_max_lenght": "", "input_render_with_py_function": "", "input_py_verification": "", "input_required": False, "input_sex": "M"},
    # {"input_name": "email_file_filename", "input_placeholder": "Nome do arquivo do email", "input_js": "", "input_type": "hidden", "input_min_lenght": "", "input_max_lenght": "", "input_render_with_py_function": "", "input_py_verification": "check_if_file_exists", "input_required": False, "input_sex": "M"},
    # {"input_name": "user_email", "input_placeholder": "Email", "input_js": "", "input_type": "email", "input_min_lenght": "", "input_max_lenght": "", "input_render_with_py_function": "", "input_py_verification": "check_if_email", "input_required": True, "input_sex": "M"},
    # {"input_name": "user_name", "input_placeholder": "Nome", "input_js": "formatToLetter", "input_type": "text", "input_min_lenght": "", "input_max_lenght": "", "input_render_with_py_function": "", "input_py_verification": "", "input_required": True, "input_sex": "M"},
    # {"input_name": "user_last_name", "input_placeholder": "Sobrenome", "input_js": "formatToLetter", "input_type": "text", "input_min_lenght": "", "input_max_lenght": "", "input_render_with_py_function": "", "input_py_verification": "", "input_required": True, "input_sex": "M"},
    # {"input_name": "user_phone", "input_placeholder": "Telefone", "input_js": "formatToPhone", "input_type": "text", "input_min_lenght": "15", "input_max_lenght": "15", "input_render_with_py_function": "format_to_phone", "input_py_verification": "check_if_br_phone", "input_required": True, "input_sex": "M"},
    # {"input_name": "user_cpf", "input_placeholder": "CPF", "input_js": "formatToCPF", "input_type": "text", "input_min_lenght": "14", "input_max_lenght": "14", "input_render_with_py_function": "format_to_cpf", "input_py_verification": "check_if_cpf", "input_required": True, "input_sex": "M"},
    # {"input_name": "user_cnpj", "input_placeholder": "CNPJ", "input_js": "formatToCNPJ", "input_type": "text", "input_min_lenght": "18", "input_max_lenght": "18", "input_render_with_py_function": "format_to_cnpj", "input_py_verification": "check_if_cnpj", "input_required": True, "input_sex": "M"},
    # {"input_name": "user_password", "input_placeholder": "Senha", "input_js": "", "input_min_lenght": "8", "input_max_lenght": "", "input_render_with_py_function": "", "input_type": "password", "input_py_verification": "check_if_password", "input_required": True, "input_sex": "F"},
    # {"input_name": "model_password", "input_placeholder": "Senha", "input_js": "", "input_min_lenght": "", "input_max_lenght": "", "input_render_with_py_function": "", "input_type": "password", "input_py_verification": "", "input_required": True, "input_sex": "F"},
    # {"input_name": "user_password_confirm", "input_placeholder": "Confirmação de Senha", "input_js": "", "input_min_lenght": "8", "input_max_lenght": "", "input_render_with_py_function": "", "input_type": "password", "input_py_verification": "check_if_password", "input_required": True, "input_sex": "F"},
    # {"input_name": "user_agree_with_communication", "input_placeholder": "Concordo em receber comunicados", "input_js": "", "input_min_lenght": "", "input_max_lenght": "", "input_render_with_py_function": "", "input_type": "checkbox", "input_py_verification": "", "input_required": False, "input_sex": "M"},
    # {"input_name": "user_agree_with_terms", "input_placeholder": "Concordo com os termos", "input_js": "", "input_min_lenght": "", "input_max_lenght": "", "input_render_with_py_function": "", "input_type": "checkbox", "input_py_verification": "", "input_required": True, "input_sex": "M"},
    # {"input_name": "user_image", "input_placeholder": "Imagem", "input_js": "uploadImage", "input_type": "file", "input_min_lenght": "", "input_max_lenght": "", "input_render_with_py_function": "", "input_py_verification": "", "input_required": True, "input_sex": "F"},
    # {"input_name": "user_image_filename", "input_placeholder": "Nome da Imagem", "input_js": "", "input_type": "hidden", "input_min_lenght": "", "input_max_lenght": "", "input_render_with_py_function": "", "input_py_verification": "check_if_file_exists", "input_required": True, "input_sex": "M"},
    # {"input_name": "blog_post_image", "input_placeholder": "Imagem", "input_js": "uploadImage", "input_type": "file", "input_min_lenght": "", "input_max_lenght": "", "input_render_with_py_function": "", "input_py_verification": "", "input_required": True, "input_sex": "F"},
    # {"input_name": "blog_post_image_filename", "input_placeholder": "Nome da Imagem", "input_js": "", "input_type": "hidden", "input_min_lenght": "", "input_max_lenght": "", "input_render_with_py_function": "", "input_py_verification": "check_if_file_exists", "input_required": True, "input_sex": "M"},
    # {"input_name": "blog_post_title", "input_placeholder": "Título da Postagem", "input_js": "", "input_type": "text", "input_min_lenght": "", "input_max_lenght": "100", "input_render_with_py_function": "", "input_py_verification": "", "input_required": True, "input_sex": "M"},
    # {"input_name": "blog_post_text", "input_placeholder": "Texto", "input_js": "", "input_type": "text", "input_min_lenght": "", "input_max_lenght": "2000", "input_render_with_py_function": "", "input_py_verification": "", "input_required": True, "input_sex": "M"},
    # {"input_name": "comment_image", "input_placeholder": "Imagem", "input_js": "uploadImage", "input_type": "file", "input_min_lenght": "", "input_max_lenght": "", "input_render_with_py_function": "", "input_py_verification": "", "input_required": True, "input_sex": "F"},
    # {"input_name": "comment_image_filename", "input_placeholder": "Nome da Imagem", "input_js": "", "input_type": "hidden", "input_min_lenght": "", "input_max_lenght": "", "input_render_with_py_function": "", "input_py_verification": "check_if_file_exists", "input_required": True, "input_sex": "M"},
    # {"input_name": "comment_author", "input_placeholder": "Título da Postagem", "input_js": "", "input_type": "text", "input_min_lenght": "", "input_max_lenght": "100", "input_render_with_py_function": "", "input_py_verification": "", "input_required": True, "input_sex": "M"},
    # {"input_name": "comment_text", "input_placeholder": "Texto", "input_js": "", "input_type": "text", "input_min_lenght": "", "input_max_lenght": "2000", "input_render_with_py_function": "", "input_py_verification": "", "input_required": True, "input_sex": "M"},
]

# default_inputs = [{"default_input_name": "upload_to_bucket", "default_input_value": lambda_constants["img_bucket"]}]

# list_table = {"entity": "blog_post", "query": "query_paginated_all_blog_post", "attributes": [{"attribute_name": "Imagem", "attribute_value": "blog_post_image_filename"}, {"attribute_name": "Titulo", "attribute_value": "blog_post_title"}, {"attribute_name": "Texto", "attribute_value": "blog_post_text"}]}
# list_table = {"entity": "comment", "query": "query_paginated_all_comment", "attributes": [{"attribute_name": "Imagem", "attribute_value": "comment_image_filename"}, {"attribute_name": "Autor", "attribute_value": "comment_author"}, {"attribute_name": "Comentário", "attribute_value": "comment_text"}]}
# list_table = {"entity": "order", "query": "query_paginated_all_orders", "attributes": [{"attribute_name": "ID", "attribute_value": "order_id"}, {"attribute_name": "Email", "attribute_value": "order_user_email"}]}
# list_table = {"entity": "blog_post", "query": "query_paginated_all_blog_post", "attributes": [{"attribute_name": "Imagem", "attribute_value": "blog_post_image_url"}, {"attribute_name": "Título", "attribute_value": "blog_post_title"}, {"attribute_name": "Texto", "attribute_value": "blog_post_text"}]}
# list_thumbs = {"entity": "blog_post", "query": "query_paginated_all_blog_post", "attributes": [{"attribute_name": "Imagem", "attribute_value": "blog_post_image_url"}, {"attribute_name": "Título", "attribute_value": "blog_post_title"}, {"attribute_name": "Texto", "attribute_value": "blog_post_text"}]}

utils = Utils()
root_folder = os.getcwd().replace("\\", "/") + "/"
py_page = utils.read_file_with_codecs("tools_for_devs/py_samples/default_py_page.py")
py_page = py_page.replace("default_lambda_page_name_val", utils.format_snakecase_to_camelcase(snakecase_page_name))
py_page = py_page.replace("public_val", str(public))
py_page = py_page.replace("bypass_val", str(bypass))


try:
    os.mkdir(root_folder + "src/html/" + snakecase_page_name)
    os.mkdir(root_folder + "src/html/" + snakecase_page_name + "/_codes")
except:
    print("folders already exists")

new_html = utils.read_file_with_codecs("tools_for_devs/html_samples/default_html_page.html")

if not list_thumbs:
    new_html = new_html.replace("html_list_thumbs_val", "")
    py_page = py_page.replace("default_list_thumbs_val", "")

if list_thumbs:
    new_html = new_html.replace("html_list_thumbs_val", utils.read_file_with_codecs("tools_for_devs/html_samples/list_thumbs.html"))
    new_html = new_html.replace("entity_val", list_thumbs["entity"])

    thumb_html = utils.read_file_with_codecs("tools_for_devs/html_samples/thumb.html")
    thumb_attributes = []
    for attribute in list_thumbs["attributes"]:
        thumb_attribute = utils.read_file_with_codecs("tools_for_devs/html_samples/thumb.html")

if not list_table:
    new_html = new_html.replace("html_table_header_val", "")
    new_html = new_html.replace("pagination_inputs_and_js_val", "")
    py_page = py_page.replace("default_list_entity_val", "")

if list_table:
    new_html = new_html.replace("html_table_header_val", utils.read_file_with_codecs("tools_for_devs/html_samples/table_header.html"))
    new_html = new_html.replace("entity_val", list_table["entity"])

    table_header_attributes = []
    table_rows_attributes = []
    for attribute in list_table["attributes"]:
        table_header_attribute = utils.read_file_with_codecs("tools_for_devs/html_samples/table_header_attributes.html")
        table_header_attribute = table_header_attribute.replace("attribute_name_val", attribute["attribute_name"])
        table_header_attributes.append(table_header_attribute)
        table_rows_attribute = utils.read_file_with_codecs("tools_for_devs/html_samples/table_rows_attributes.html")
        table_rows_attribute = table_rows_attribute.replace("attribute_value_val", attribute["attribute_value"] + "_val")
        table_rows_attributes.append(table_rows_attribute)
    table_header_attributes = "\n            ".join(table_header_attributes)
    table_rows_attributes = "<tr>\n    " + "\n    ".join(table_rows_attributes) + "\n</tr>"

    new_html = new_html.replace("table_header_attributes_val", table_header_attributes)
    new_html = new_html.replace("entity_val", list_table["entity"])
    new_html = new_html.replace("pagination_inputs_and_js_val", utils.read_file_with_codecs("tools_for_devs/html_samples/pagination_inputs_and_js.html"))

    with codecs.open("src/html/" + snakecase_page_name + "/_codes/" + "html_" + list_table["entity"] + "_table_rows.html", "w", "utf-8-sig") as new_html_page:
        new_html_page.write(table_rows_attributes)
        new_html_page.close()

    py_page = py_page.replace("default_list_entity_val", utils.read_file_with_codecs("tools_for_devs/py_samples/default_list_entity.py"))
    py_page = py_page.replace("def_list_entity_html_val", utils.read_file_with_codecs("tools_for_devs/py_samples/def_list_entity_html.py"))

    default_list_entity_replaces = []
    for attribute in list_table["attributes"]:
        default_list_entity_replace = utils.read_file_with_codecs("tools_for_devs/py_samples/default_list_entity_replace.py")
        default_list_entity_replace = default_list_entity_replace.replace("attribute_value_val", attribute["attribute_value"])
        default_list_entity_replaces.append(default_list_entity_replace)
    default_list_entity_replaces = "\n".join(default_list_entity_replaces)

    py_page = py_page.replace("default_list_entity_replaces_val", default_list_entity_replaces)
    py_page = py_page.replace("entity_val", list_table["entity"])
    py_page = py_page.replace("query_val", list_table["query"])
    py_page = py_page.replace("snakecase_page_name_val", snakecase_page_name)


if not inputs:
    new_html = new_html.replace("html_form_val", "")
    py_page = py_page.replace("if_post_in_render_get_val", "")
    py_page = py_page.replace("if_not_post_in_render_post_val", "")
    py_page = py_page.replace("if_post_verification_in_render_post_val", "")
    py_page = py_page.replace("\n\n", "\n")

if inputs:
    if_post_in_render_get = []
    for input in inputs:
        input_py = utils.read_file_with_codecs("tools_for_devs/py_samples/if_post_in_render_get.py")
        input_py = input_py.replace("input_name_val", input["input_name"])
        if input["input_type"] == "checkbox":
            input_py = input_py.replace(input["input_name"] + "_val", input["input_name"] + "_pre_checked_val")
            input_py = input_py.replace('self.post["' + input["input_name"] + '"]', '"' + "checked='checked'" + '"')
        if input["input_render_with_py_function"]:
            input_py = input_py.replace('self.post["' + input["input_name"] + '"]', "self.utils." + input["input_render_with_py_function"] + "(" + 'self.post["' + input["input_name"] + '"]' + ")")

        if_post_in_render_get.append(input_py)
    if_post_in_render_get = "".join(if_post_in_render_get)
    py_page = py_page.replace("if_post_in_render_get_val", if_post_in_render_get)

    if_not_post_in_render_post = []
    for input in inputs:
        if input["input_required"]:
            input_py = utils.read_file_with_codecs("tools_for_devs/py_samples/if_not_post_in_render_post.py")
            input_py = input_py.replace("input_name_val", input["input_name"])
            input_py = input_py.replace("input_placeholder_val", input["input_placeholder"])
            if input["input_sex"] == "F":
                input_py = input_py.replace("um", "uma")
            if_not_post_in_render_post.append(input_py)
    if_not_post_in_render_post = "\n".join(if_not_post_in_render_post)
    py_page = py_page.replace("if_not_post_in_render_post_val", if_not_post_in_render_post)

    if_post_verification_in_render_post = []
    for input in inputs:
        if input["input_py_verification"]:
            input_py = utils.read_file_with_codecs("tools_for_devs/py_samples/if_post_verification_in_render_post.py")
            input_py = input_py.replace("input_name_val", input["input_name"])
            input_py = input_py.replace("input_py_verification_val", input["input_py_verification"])
            input_py = input_py.replace("input_placeholder_val", input["input_placeholder"])
            if input["input_sex"] == "F":
                input_py = input_py.replace("um", "uma")
                input_py = input_py.replace("válido", "válida")
            if input["input_py_verification"] == "check_if_file_exists":
                input_py = input_py.replace("_in_s3(", '_in_s3(lambda_constants["img_bucket"], ')
            if_post_verification_in_render_post.append(input_py)
    if_post_verification_in_render_post = "".join(if_post_verification_in_render_post)
    py_page = py_page.replace("if_post_verification_in_render_post_val", if_post_verification_in_render_post)

    form_html = utils.read_file_with_codecs("tools_for_devs/html_samples/form.html")
    form_html = form_html.replace("page_name_form_val", snakecase_page_name + "_form")
    inputs_html = []
    for input in inputs:
        input_html = utils.read_file_with_codecs("tools_for_devs/html_samples/form_input.html")
        input_html = input_html.replace("input_type_val", input["input_type"])
        input_html = input_html.replace("input_name_val", input["input_name"])
        input_html = input_html.replace("input_value_val", "{{" + input["input_name"] + "_val}}")
        input_html = input_html.replace("input_placeholder_val", input["input_placeholder"])

        if input["input_min_lenght"]:
            input_html = input_html.replace("input_min_lenght_val", 'minlength="' + input["input_min_lenght"] + '"')
        else:
            input_html = input_html.replace("input_min_lenght_val", "")

        if input["input_max_lenght"]:
            input_html = input_html.replace("input_max_lenght_val", 'maxlength="' + input["input_max_lenght"] + '"')
        else:
            input_html = input_html.replace("input_max_lenght_val", "")

        if input["input_js"]:
            input_html = input_html.replace("input_js_val", 'oninput="js.index.' + input["input_js"] + '(this)"')
        else:
            input_html = input_html.replace("input_js_val", "")
        if input["input_required"]:
            input_html = input_html.replace("input_required_val", "required")
        else:
            input_html = input_html.replace("input_required_val", "")
        if input["input_type"] == "checkbox":
            input_html = input_html.replace('value="{{' + input["input_name"] + '_val}}"', "")
            input_html = input_html.replace("input_presel_val", "{{" + input["input_name"] + "_pre_checked_val}}")
            input_label = utils.read_file_with_codecs("tools_for_devs/html_samples/form_label.html")
            input_label.replace("input_name_val", input["input_name"])
            input_label.replace("input_placeholder_val", input["input_placeholder"])
        else:
            input_html = input_html.replace("input_presel_val", "")

        inputs_html.append(input_html)

        if input["input_type"] == "checkbox":
            input_label = utils.read_file_with_codecs("tools_for_devs/html_samples/form_label.html")
            input_label = input_label.replace("input_name_val", input["input_name"])
            input_label = input_label.replace("input_placeholder_val", input["input_placeholder"])
            inputs_html.append(input_label)

    inputs_html = "\n    ".join(inputs_html)
    form_html = form_html.replace("inputs_val", inputs_html)
    new_html = new_html.replace("html_form_val", form_html)

if not default_inputs:
    new_html = new_html.replace("default_input_val", "")
    py_page = py_page.replace("default_inputs_replace_val", "")

if default_inputs:
    default_inputs_replace = []
    for default_input in default_inputs:
        input_py = utils.read_file_with_codecs("tools_for_devs/py_samples/default_inputs_replace.py")
        input_py = input_py.replace("default_input_name_val", default_input["default_input_name"])
        input_py = input_py.replace("default_input_value_val", default_input["default_input_value"])

        default_inputs_replace.append(input_py)
    default_inputs_replace = "".join(default_inputs_replace)
    py_page = py_page.replace("default_inputs_replace_val", default_inputs_replace)

    default_inputs_html = []
    for default_input in default_inputs:
        input_label = utils.read_file_with_codecs("tools_for_devs/html_samples/page_input.html")
        input_label = input_label.replace("default_input_name_val", default_input["default_input_name"])
        input_label = input_label.replace("default_input_value_val", "{{" + default_input["default_input_name"] + "_val}}")
        default_inputs_html.append(input_label)
    default_inputs_html = "\n    ".join(default_inputs_html)
    new_html = new_html.replace("default_input_val", default_inputs_html)


with codecs.open("src/html/" + snakecase_page_name + "/" + snakecase_page_name + ".py", "w", "utf-8-sig") as new_py_page:
    py_page = py_page.replace("\r\n\r\n", "\r\n").replace("\r\n\r\n", "\r\n")
    new_py_page.write(py_page)
    new_py_page.close()

with codecs.open("src/html/" + snakecase_page_name + "/index.html", "w", "utf-8-sig") as new_html_page:
    new_html = new_html.replace("\r\n\r\n", "\r\n").replace("\r\n\r\n", "\r\n").replace("\r\n\r\n", "\r\n").replace("\r\n\r\n", "\r\n")
    new_html_page.write(new_html)
    new_html_page.close()

print("end")
