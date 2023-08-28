from utils.Config import lambda_constants
import json

lambda_client = None
stepfunctions_client = None


class Lambda:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Lambda, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def start_stepfunction_execution(self, state_machine_arn, payload):
        return self.get_stepfunctions_client().start_execution(stateMachineArn=state_machine_arn, input=json.dumps(payload))

    def invoke(self, function_name, invocation_type, payload):
        return self.get_lambda_client().invoke(FunctionName=function_name, InvocationType=invocation_type, Payload=json.dumps(payload))

    def get_lambda_client(self):
        global lambda_client
        if lambda_client:
            return lambda_client
        import boto3

        lambda_client = boto3.client("lambda", region_name=lambda_constants["region"])
        return lambda_client

    def get_stepfunctions_client(self):
        global stepfunctions_client
        if stepfunctions_client:
            return stepfunctions_client
        import boto3

        stepfunctions_client = boto3.client("stepfunctions", lambda_constants["region"])
        return stepfunctions_client
