from urllib.parse import *
import hashlib, time, json
import requests, base64, random
from utils.utils import *
import base64

def _xor(string):
    return "".join([hex(ord(c) ^ 5)[2:] for c in string])

iid = "7126211940330063622"
did = "6888243656290108930"
username = "rubenholg"

Solver(did, iid).solve_captcha()

params = urlencode(
    {
        "device_type": "SM-G973N",
        "app_name": "musical_ly",
        "host_abi": "armeabi-v7a",
        "channel": "googleplay",
        "device_platform": "android",
        "iid": iid,
        "version_code": 190103,
        "timezone_name": "Africa/Harare",
        "device_id": did,
        "device_brand": "samsung",
        "os_version": "7.1.2",
        "aid": 1233,
    }
)

payload = f"mix_mode=1&multi_login=1&login_name={_xor(username)}&find_way=1&account_sdk_source=app"
sign    = Xgorgon(params, payload, None).get_value()

response = requests.post(
    url     = "https://api16-va.tiktokv.com/passport/mobile/get_account/?" + params,
    data    = payload,
    headers = {
        "x-gorgon": sign["X-Gorgon"],
        "x-khronos": sign["X-Khronos"],
    },
)

token = response.json()["data"]["token"]

# --------------------------------------------------------------------------------------

payload = f"need_limit_platform=0&not_login_ticket={token}&account_sdk_source=app&need_limit_os=0&multi_login=1"
sign = Xgorgon("version_code=190303&aid=1233", payload, None).get_value()

response = requests.post(
    url     = "https://api16-va.tiktokv.com/passport/auth/available_ways/?version_code=190303&aid=1233",
    data    = payload,
    headers = {
        "x-gorgon": sign["X-Gorgon"],
        "x-khronos": sign["X-Khronos"],
    },
)

print(json.dumps(response.json(), indent=4))
