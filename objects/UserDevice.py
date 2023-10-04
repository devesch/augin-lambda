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
        self.device_desconnected_at = ""

        self.created_at = str(time.time())
        self.entity = "folder"


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
    device["device_desconnected_at"] = str(time.time())
    Dynamo().put_entity(device)
    return device
