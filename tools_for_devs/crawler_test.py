import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))


from utils.utils.Http import Http, lambda_constants
from utils.AWS.Dynamo import Dynamo

utils = Utils()
dynamo = Dynamo()


def crawler(user_email, response, headers):
    print("running crawler")
    splitted_responses = response.split("https://")
    del splitted_responses[0]
    for splited_response in splitted_responses:
        new_link = "https://" + splited_response.split('"')[0]
        if "https://web.augin.app" in new_link:
            if new_link not in crawled_links[user_email]:
                new_link_response = utils.request("GET", new_link, headers, json=False)
                if "<separetor>" in new_link_response:
                    crawled_links[user_email][new_link] = new_link_response.split("<separetor>")[0]
                elif "None" in new_link_response:
                    crawled_links[user_email][new_link] = "none"
                else:
                    crawled_links[user_email][new_link] = "ok"
                crawler(user_email, new_link_response, headers)


crawled_links = {}
user = dynamo.get_user("vinicius@devesch.com.br")
if user["user_auth_token"]:
    crawled_links[user["user_email"]] = {}
    headers = {"Access-Control-Allow-Origin": "*", "Cookie": "__Secure-token=" + user["user_auth_token"]}
    response = utils.request("GET", lambda_constants["domain_name_url"], headers, json=False)
    crawler(user["user_email"], response, headers)


print("end")
