import os
import os.path
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from utils.utils.Http import Http
from utils.AWS.Dynamo import Dynamo
from objects.Model import Model

utils = Utils()
dynamo = Dynamo()

all_models = dynamo.query_entity("model")

xml_deltas = []
for model in all_models:
    if model.get("model_xml_ec2_machine") and model.get("model_xml_total_time") and model["model_filesize"] == "605300743":
        xml_deltas.append({"model_xml_ec2_machine": model["model_xml_ec2_machine"], "model_xml_total_time": model["model_xml_total_time"]})

print("here")
