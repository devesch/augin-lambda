from utils.Config import lambda_constants
import uuid

ec2_client = None


class Ec2:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Ec2, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def get_all_instances(self):
        paginator = self.get_ec2_client().get_paginator("describe_instance_types")
        all_instances = {}
        for page in paginator.paginate():
            for instance in page["InstanceTypes"]:
                all_instances[instance["InstanceType"]] = instance
        return all_instances

    def create_fleet(self, LaunchTemplateConfigs):
        return self.get_ec2_client().create_fleet(
            DryRun=False, ClientToken=str(uuid.uuid4()), SpotOptions={"AllocationStrategy": "lowest-price", "InstanceInterruptionBehavior": "terminate", "MinTargetCapacity": 1, "MaxTotalPrice": "1.0"}, ExcessCapacityTerminationPolicy="termination", LaunchTemplateConfigs=LaunchTemplateConfigs, TargetCapacitySpecification={"TotalTargetCapacity": 1, "OnDemandTargetCapacity": 0, "SpotTargetCapacity": 1, "DefaultTargetCapacityType": "spot"}, Type="request", ReplaceUnhealthyInstances=False
        )

    def describe_spot_price_history(self, filtered_instances, start_time, end_time):
        return self.get_ec2_client().describe_spot_price_history(InstanceTypes=list(filtered_instances.keys()), ProductDescriptions=["Linux/UNIX"], MaxResults=300, StartTime=start_time.isoformat() + "Z", EndTime=end_time.isoformat() + "Z")

    def get_ec2_client(self):
        global ec2_client
        if ec2_client:
            return ec2_client
        import boto3

        ec2_client = boto3.client("ec2", region_name=lambda_constants["region"])
        return ec2_client
