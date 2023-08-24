import clipboard
import pyperclip

file_relative_copy_path = clipboard.paste()
file_relative_copy_path = file_relative_copy_path.replace(".html", "").replace("src\html\\", "").replace("\\", "/")
pyperclip.copy('html = self.utils.read_html("' + file_relative_copy_path + '")')
