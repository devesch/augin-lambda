import os
import boto3
import re
import datetime
import json
import uuid
import traceback

ec2_client = None
ses_client = None
us_ses_client = None


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

        ec2_client = boto3.client("ec2", region_name=get_region())
        return ec2_client


avarage_benchmark = "0.40"

benchmarks = {
    "c6a.4xlarge": "1.0",
    "m6a.2xlarge": "0.9083281995899064",
    "c5a.8xlarge": "0.8252643146475042",
    "c5ad.8xlarge": "0.801864937049298",
    "c6in.4xlarge": "0.7951352124012134",
    "c5a.4xlarge": "0.7929069143304885",
    "c5ad.4xlarge": "0.7905079194026571",
    "m6a.4xlarge": "0.7859370715790706",
    "m6i.4xlarge": "0.7597415919370031",
    "r6i.2xlarge": "0.7412767614653772",
    "m6i.2xlarge": "0.7160775145740537",
    "r6i.4xlarge": "0.6741083021257697",
    "i4i.4xlarge": "0.6557770403123465",
    "m5zn.6xlarge": "0.6552019764600174",
    "c5ad.xlarge": "0.6440660057742537",
    "c5a.xlarge": "0.6400420972326807",
    "c6i.4xlarge": "0.6303903069531763",
    "m5a.4xlarge": "0.6138650719968337",
    "m5ad.4xlarge": "0.6101377484696068",
    "c5.xlarge": "0.5909457322105043",
    "r5a.4xlarge": "0.5848171806060065",
    "c5n.4xlarge": "0.5771062941720857",
    "m5a.2xlarge": "0.574238173757352",
    "c5d.4xlarge": "0.5738607814458786",
    "m5.4xlarge": "0.573290200658294",
    "i3en.3xlarge": "0.5520208126048954",
    "r5n.4xlarge": "0.5460644747612788",
    "c5d.xlarge": "0.541674229118824",
    "r5.4xlarge": "0.5373685448742641",
    "m5zn.2xlarge": "0.5239412877082764",
    "r5n.2xlarge": "0.523078769080539",
    "m5d.2xlarge": "0.5229092105611319",
    "r5d.2xlarge": "0.5178124274177948",
    "r5b.xlarge": "0.5067695364064507",
    "r5b.4xlarge": "0.5024940015795113",
    "r5b.2xlarge": "0.4816339805905302",
    "r5a.xlarge": "0.47741614441338603",
    "r4.4xlarge": "0.4681477920908481",
    "r6i.xlarge": "0.4630142974926251",
    "r3.4xlarge": "0.4552537319737032",
    "r5n.xlarge": "0.45147738716123237",
    "i4i.xlarge": "0.4455919338024985",
    "r5.xlarge": "0.44313685079880644",
    "m5.2xlarge": "0.4316511941418003",
    "i3en.2xlarge": "0.42908536589390606",
    "m4.2xlarge": "0.42595693969311765",
    "m3.xlarge": "0.42132801721171836",
    "m3.2xlarge": "0.41998767528460523",
    "m5zn.3xlarge": "0.40776439437474443",
    "r3.xlarge": "0.40663608903121456",
    "r4.xlarge": "0.4033667968739349",
    "r4.2xlarge": "0.395176556160008",
    "r5ad.4xlarge": "0.391040846556983",
    "r3.2xlarge": "0.3789376829691344",
    "x1e.xlarge": "0.33997343283818254",
    "r5d.xlarge": "0.31115599188098675",
    "r5a.2xlarge": "0.23058805139991845",
}


def is_excluded(instance_name, instance_dict):
    excluded_prefixes = ["g", "t", "x", "u", "trn", "p", "f", "d", "l", "h"]
    excluded_families = ["a", "g", "metal"]
    instance_parts = re.split(r"(\d+)", instance_name, 1)  # split on the first number in the instance name
    instance_prefix = instance_parts[0]
    instance_family = instance_parts[2] if len(instance_parts) > 2 and "." in instance_parts[2] else ""
    if any(x in instance_family for x in excluded_families) or any(instance_prefix.startswith(x) for x in excluded_prefixes):
        return True
    return False


def is_vcpu_memory_sufficient(instance_dict):
    vcpuinfo = instance_dict.get("VCpuInfo", {})
    vcpu = vcpuinfo.get("DefaultVCpus", 0)
    memory = instance_dict.get("MemoryInfo", {}).get("SizeInMiB", 0)
    # if vcpu >= 8 and memory >= 16384:  # 16 GB is 16384 MB
    if vcpu >= 4 and memory >= 8000:  # 8 GB is 8192 MB
        return vcpu, memory / 1024
    return 0, 0


def is_spot_supported(instance_dict):
    if "SupportedUsageClasses" in instance_dict and "spot" in instance_dict["SupportedUsageClasses"]:
        return True
    return False


def is_supported_architecture(instance_dict):
    if "ProcessorInfo" in instance_dict:
        if "SupportedArchitectures" in instance_dict["ProcessorInfo"]:
            if "x86_64" in instance_dict["ProcessorInfo"]["SupportedArchitectures"]:
                return True
    return False


def has_gpu(instance_dict):
    return "GpuInfo" in instance_dict


def is_burstable(instance_dict):
    return instance_dict["BurstablePerformanceSupported"]


def is_fpga(instance_dict):
    return "FpgaInfo" in instance_dict


def is_metal(instance_dict):
    return instance_dict["BareMetal"]


def get_minimum_vcpu_memory(_vcpu, _memory):
    for instance_name, instance_data in all_instances.items():
        if not is_spot_supported(instance_data):
            continue
        if not is_supported_architecture(instance_data):
            continue
        vcpu, ram = is_vcpu_memory_sufficient(instance_data)
        if vcpu == 0:
            continue
        if has_gpu(instance_data) or is_burstable(instance_data) or is_fpga(instance_data) or is_metal(instance_data):
            continue
        if vcpu >= _vcpu and ram >= _memory:
            filtered_instances[instance_name] = {"vcpu": vcpu, "ram": ram}
    return filtered_instances


def get_best_price(filtered_instances, _limit=100):
    best_prices = []
    end_time = datetime.datetime.utcnow()
    start_time = end_time - datetime.timedelta(hours=1)
    response = Ec2().describe_spot_price_history(filtered_instances, start_time, end_time)
    latest_prices = {}
    for spot_price in response["SpotPriceHistory"]:
        instance_type = spot_price["InstanceType"]
        price = float(spot_price["SpotPrice"])
        vcpus = filtered_instances.get(instance_type, {}).get("vcpu", 1)
        ram = filtered_instances.get(instance_type, {}).get("ram", 1)
        timestamp = spot_price["Timestamp"]
        if instance_type in benchmarks:
            benchmark = float(benchmarks[instance_type])
        else:
            benchmark = float(avarage_benchmark)
        PerformancePrice = benchmark / price
        if instance_type not in latest_prices or timestamp > latest_prices[instance_type]["Timestamp"]:
            latest_prices[instance_type] = {"InstanceType": instance_type, "PerformancePrice": PerformancePrice, "SpotPrice": price, "Benchmark": benchmark, "Timestamp": timestamp, "VCPU": vcpus, "ram": ram}

    latest_prices_list = list(latest_prices.values())
    latest_prices_list.sort(key=lambda x: x["PerformancePrice"], reverse=True)
    for price_info in latest_prices_list[0:_limit]:
        if "Timestamp" in price_info:
            del price_info["Timestamp"]
        best_prices.append(price_info)
    return best_prices


def get_region():
    if os.environ.get("AWS_EXECUTION_ENV") is None:
        with open(".vscode/enviroment_variables.json", "r", encoding="utf-8") as read_file:
            env_var = json.load(read_file)
            return env_var["region"]
    else:
        session = boto3.session.Session()
        return session.region_name


def create_ec2_spot_fleet_request(instance_types):
    if get_region() == "sa-east-1":
        subnets = ["subnet-5d01133a", "subnet-2f110a77", "subnet-70f22f39"]
        launch_template_id = "lt-03c9136a3ba0eaafd"
    elif get_region() == "us-east-1":
        launch_template_id = "lt-051d9221c74acbc2d"
        subnets = ["subnet-e76a07ad", "subnet-412df426", "subnet-e3a749dd"]

    overrides = []
    for instance_type in instance_types:
        for subnet in subnets:
            overrides.append({"InstanceType": instance_type, "SubnetId": subnet, "WeightedCapacity": 1.0})
    LaunchTemplateConfigs = [{"LaunchTemplateSpecification": {"LaunchTemplateId": launch_template_id, "Version": "$Default"}, "Overrides": overrides}]

    create_fleet_response = Ec2().create_fleet(LaunchTemplateConfigs)
    print("Fleet Response Id " + create_fleet_response["FleetId"])
    return create_fleet_response["FleetId"]


all_instances = Ec2().get_all_instances()
filtered_instances = {}
best_price_instances_map = {}


def main_lambda_handler(event, context):
    print(json.dumps(event))
    global best_price_instances_map

    if event.get("ec2_instance"):
        return create_ec2_spot_fleet_request([event["ec2_instance"]])

    if not event.get("ec_requested_gbs"):
        event["ec_requested_gbs"] = "20.0"

    if best_price_instances_map.get("ec_requested_gbs"):
        best_instances_types = best_price_instances_map["ec_requested_gbs"]

    else:
        best_price_instances = get_best_price(get_minimum_vcpu_memory(4, float(event["ec_requested_gbs"])), _limit=100)
        best_instances_types = []
        for instance in best_price_instances[:3]:
            best_instances_types.append(instance["InstanceType"])

    best_price_instances_map[event["ec_requested_gbs"]] = best_instances_types
    return create_ec2_spot_fleet_request(best_instances_types)


def lambda_handler(event, context):
    try:
        return main_lambda_handler(event, context)
    except Exception as e:
        send_error_email(event, "AUGIN lambda_EC2-Launcher", e)


def send_error_email(event, function, error, email_destination=["eugenio@devesch.com.br", "matheus@devesch.com.br"]):
    try:
        tb = traceback.format_exc()
    except:
        tb = "Não ocorreu"
    try:
        body_html = f"ERROR {function.upper()}: {error}\n\n<br><br> TRACEBACK: {tb}\n\n<br><br> EVENT: {json.dumps(event)}"
    except:
        body_html = f"ERROR {function.upper()}: {error}\n\n<br><br> TRACEBACK: {tb}\n\n<br><br> EVENT: {str(event.__dict__)}"

    return send_email(email_destination, body_html, body_html, subject_data=f"ERROR {function.upper()}", region=get_region())


def send_email(email_destination, body_html="", body_text="", subject_data="", region=get_region()):
    ToAddresses = []
    if type(email_destination) == list:
        ToAddresses = email_destination
    else:
        ToAddresses = [email_destination]

    if region == "us-east-1":
        ses_client = get_us_ses_client()
    else:
        ses_client = get_ses_client()

    ses_client.send_email(
        Destination={"ToAddresses": ToAddresses},
        Message={
            "Body": {
                "Html": {
                    "Charset": "utf-8",
                    "Data": str(body_html),
                },
                "Text": {
                    "Charset": "utf-8",
                    "Data": str(body_text),
                },
            },
            "Subject": {
                "Charset": "utf-8",
                "Data": subject_data,
            },
        },
        Source="eugenio@devesch.com.br",
        ConfigurationSetName="Config",
    )
    return True


def get_us_ses_client():
    global us_ses_client
    if us_ses_client:
        return us_ses_client
    import boto3

    us_ses_client = boto3.client("ses", region_name="us-east-1")
    return us_ses_client


def get_ses_client():
    global ses_client
    if ses_client:
        return ses_client
    import boto3

    ses_client = boto3.client("ses", region_name=get_region())
    return ses_client


if os.environ.get("AWS_EXECUTION_ENV") is None:
    with open("_testnow_ec2launcher.json", "r") as read_file:
        event = json.load(read_file)
        html = main_lambda_handler(event, None)
