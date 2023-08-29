import os

from objects.Model import Model
from utils.Config import lambda_constants
from utils.AWS.S3 import S3
from utils.AWS.Sqs import Sqs
from utils.AWS.Dynamo import Dynamo
from utils.AWS.Lambda import Lambda
from utils.utils.Generate import Generate
from utils.utils.EncodeDecode import EncodeDecode
from utils.utils.ReadWrite import ReadWrite
from utils.utils.Validation import Validation
from utils.utils.StrFormat import StrFormat
from utils.utils.Http import Http


class ModelController:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ModelController, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def generate_new_model(self, email):
        model_id = Dynamo().get_next_model_id()
        new_model = Model(email, model_id, model_id, "not_created").__dict__
        Dynamo().put_entity(new_model)
        return new_model
