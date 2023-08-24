snakecase_page_name = "webview_update_menu_count"
import os
import os.path
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from utils.utils.Http import Http

utils = Utils()
root_folder = os.getcwd().replace("\\", "/") + "/"
with open("aws/DefaultLambdaApiPage.py") as read_file:
    default_page = read_file.read()
default_page_renamed = default_page.replace("default_api_page_name_val", utils.format_snakecase_to_camelcase(snakecase_page_name))
new_page = open("api/" + snakecase_page_name + ".py", "w")
new_page.write(default_page_renamed)
new_page.close()
