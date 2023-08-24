# from gettext import translation
from googletrans import Translator, LANGUAGES

from json import load, dumps, load, dump

# from re import findall
import os, sys
import codecs

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

# from numpy import place
# from utils.utils import format_to_letters_and_spaces
import time
import os
from utils.utils.Http import Http

###########################
### CREATE PAGE ROUTES  ###
###########################
utils = Utils()

html_source_path = os.getcwd().replace("\\", "/") + "/src/html"
project_pages = ["api"]
translations = load(open("utils/translations.json", "r", encoding="utf-8"))
for sub_dirs in os.listdir(html_source_path):
    if sub_dirs[0] != ".":
        print(sub_dirs)
        project_pages.append(sub_dirs)

if "main" in project_pages:
    project_pages.remove("main")

print(str(project_pages))
