from utils.utils.Validation import Validation
from utils.AWS.Dynamo import Dynamo
import time


class UserDevice:
    def __init__(self, user_id, device_id, device_name, device_model, device_os) -> None:
        self.pk = "user#" + user_id
        self.sk = "device#" + device_id
        self.device_id = device_id
        self.device_user_id = user_id

        self.device_name = device_name
        self.device_model = device_model
        self.device_os = device_os
        self.device_status = "connected"  # connected/disconnected
        self.device_first_access_at = str(time.time())
        self.device_last_access_at = str(time.time())
        self.device_disconnected_at = ""

        self.created_at = str(time.time())
        self.entity = "device"


def generate_device_icon(device):
    OS_ICONS = {"windows": "windows_computer", "mac": "mac_computer", "ios": "mac_mobile", "android": "android_mobile"}
    attributes_to_check = ["device_os", "os_version"]
    for attribute in attributes_to_check:
        if device.get(attribute):
            device_name = str(device[attribute]).lower()
            for os_name, icon in OS_ICONS.items():
                if os_name in device_name:
                    return icon

    return "unknown_device"


def disconnect_device(device):
    device["device_status"] = "disconnected"
    device["device_disconnected_at"] = str(time.time())
    Dynamo().put_entity(device)
    return device


def reconnect_device(device):
    device["device_status"] = "connected"
    device["device_first_access_at"] = str(time.time())
    Dynamo().put_entity(device)
    return device


def generate_connected_and_disconnected_devices(user_devices):
    connected_devices = []
    disconnected_devices = []
    if user_devices:
        for device in user_devices:
            if device["device_status"] == "connected":
                connected_devices.append(device)
            else:
                disconnected_devices.append(device)
    return connected_devices, disconnected_devices


def generate_disconnected_devices_in_last_30d(disconnected_devices):
    disconnected_devices_in_last_30d = []
    if disconnected_devices:
        for device in disconnected_devices:
            if Validation().check_if_less_than_30_days_ago(device["device_disconnected_at"]):
                disconnected_devices_in_last_30d.append(device)
    return disconnected_devices_in_last_30d
