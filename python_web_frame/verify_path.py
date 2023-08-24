from utils.AWS.Dynamo import Dynamo
from utils.utils.EncodeDecode import EncodeDecode


def get_path_data(path, user):
    if path.get("user_encoded_email"):
        path["user_email"] = EncodeDecode().decode_from_b64(path["user_encoded_email"])
        if not path["user_email"]:
            return {"error": "error"}

    if path.get("verify_email_code"):
        path["verify_email"] = Dynamo().get_verify_email(path["user_email"], path["verify_email_code"])
        if not path["verify_email"]:
            return {"error": "error"}

    if path.get("reverse"):
        if "rue" in path["reverse"]:
            path["reverse"] = True
        else:
            path["reverse"] = False

    if path.get("project_id"):
        path["project"] = Dynamo().get_project(path["project_id"])
        if not path["project"]:
            return {"error": "error"}

    if path.get("model_id"):
        path["model"] = Dynamo().get_model_by_id(path["model_id"])
        if not path["model"]:
            return {"error": "error"}
        path["project_id"] = path["model"]["model_project_id"]
        path["project"] = Dynamo().get_project(path["project_id"])

    if path.get("element_id"):
        path["element"] = Dynamo().get_element(path["project_id"], path["element_id"])
        if not path["element"]:
            return {"error": "error"}

    if path.get("sub_element_id"):
        path["sub_element"] = Dynamo().get_sub_element(path["project_id"], path["sub_element_id"])
        if not path["sub_element"]:
            return {"error": "error"}

    if path.get("sub_sub_element_id"):
        path["sub_sub_element"] = Dynamo().get_sub_sub_element(path["project_id"], path["sub_sub_element_id"])
        if not path["sub_sub_element"]:
            return {"error": "error"}

    if path.get("nano_element_id"):
        path["nano_element"] = Dynamo().get_nano_element(path["project_id"], path["nano_element_id"])
        if not path["nano_element"]:
            return {"error": "error"}

    if path.get("layer_id"):
        path["layer"] = Dynamo().query_layer_global_ids(path["project_id"], path["layer_id"])

    return path
