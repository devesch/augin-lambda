import clipboard
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

f = open("_testnow.json", "w")
payload = clipboard.paste()
# payload = payload.replace("\\", "")
f.write(payload)
f.close()
