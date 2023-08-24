import clipboard
from json import loads

f = open("_testnow.json", "w")
payload = clipboard.paste()
payload = payload.replace("\\", "")
payload = payload.replace("'", '"')
payload = payload.replace("True", "true")
payload = payload.replace("False", "false")
# try:
#     payload_splitted = payload.split("body")
#     if payload_splitted[1][4] == "{" and payload_splitted[1][3] == '"':
#         new_body = payload_splitted[1][:2] + payload_splitted[1][4:]
#         new_body_splitted = new_body.split(', "isBase64Encoded"')
#         new_body = new_body_splitted[0][:-1] + ', "isBase64Encoded"' + new_body_splitted[1]
#         payload = payload_splitted[0] + "body" + new_body
#         payload = payload.replace("n  ", "")
#         payload = payload.replace("n}", "}")
#         payload = payload.replace("False", "false")
#         payload = payload.replace("True", "true")
# except:
#     pass
# if payload[0] == '"':
#     payload = payload[1:]
# if payload[-1] == '"':
#     payload = payload[:-1]{prefix_name}{domain_name}{sufix_name}
# if "sec-ch-ua" in payload:
#     sec_slitted_payload = payload.split("sec-ch-ua")
#     final_payload = sec_slitted_payload[0] + "sec-fetch-dest" + sec_slitted_payload[3].split("sec-fetch-dest")[-1]
#     payload = final_payload
f.write(payload)
f.close()
