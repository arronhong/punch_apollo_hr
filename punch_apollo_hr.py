import hashlib
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from enum import Enum, IntEnum

USER_AGENT = "APOLLO/1.1.43 (com.mayohr.tube; build:1; iOS 16.1.1) Alamofire/1.1.43"
HRM_BASE_URL = "https://pt-be.mayohr.com"
LINKUP_BASE_URL = "https://linkup-be.mayohr.com"
AUTH_BASE_URL = "https://asiaauth.mayohr.com"


class ServiceLocation(Enum):
    GLOBAL = "HUANU4G3app"
    CHINA = "PCRU8J4app"


class PunchType(IntEnum):
    PUNCH_IN = 1
    PUNCH_OUT = 2


def magic_hash(method: str, path: str, epoch: int, srv_loc: ServiceLocation):
    return hashlib.sha256(f"{method}{path}{epoch}{srv_loc.value}".encode()).hexdigest()


def get_token_info(company_code: str, employee_no: str, password: str):
    now = int(datetime.now().timestamp())
    hash_val = magic_hash("POST", "/token", now, ServiceLocation.GLOBAL)
    user_name = f"{company_code}-{employee_no}"
    qs = urllib.parse.urlencode({"time": f"{now}", "hash": hash_val, "_sd": "HRM"})
    url = f"{AUTH_BASE_URL}/token?{qs}"
    data = urllib.parse.urlencode(
        {"grant_type": "password", "userName": user_name, "password": password}
    ).encode()
    headers = {
        "Content-type": "application/x-www-form-urlencoded; charset=utf-8",
        "User-Agent": USER_AGENT,
    }
    req = urllib.request.Request(url, data=data, method="POST", headers=headers)
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def get_access_token(code: str):
    qs = urllib.parse.urlencode({"code": code, "response_type": "id_token"})
    url = f"{LINKUP_BASE_URL}/api/auth/checkticket?{qs}"
    headers = {"User-Agent": USER_AGENT}
    req = urllib.request.Request(url, method="GET", headers=headers)
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def get_locations(token: str):
    url = f"{HRM_BASE_URL}/api/locations/AppEnableList"
    headers = {
        "User-Agent": USER_AGENT,
        "Authorization": token,
    }
    req = urllib.request.Request(url, method="GET", headers=headers)
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def punch(
    company_code: str,
    employee_no: str,
    password: str,
    attendance_type: PunchType,
    location_name: str,
):
    token_info = get_token_info(company_code, employee_no, password)
    access_token = get_access_token(token_info["code"])
    locations_resp = get_locations(access_token["id_token"])

    try:
        location = next(
            {
                "latitude": loc["Latitude"],
                "longitude": loc["Longitude"],
                "id": loc["PunchesLocationId"],
            }
            for loc in locations_resp["Data"]
            if loc["LocationName"] == location_name
        )
    except StopIteration:
        location = {
            "latitude": 0.0,
            "longitude": 0.0,
            "id": "00000000-0000-0000-0000-000000000000",
        }

    url = f"{HRM_BASE_URL}/api/checkin/punch/locate"
    data = urllib.parse.urlencode(
        {
            "AttendanceType": attendance_type.value,
            "Latitude": location["latitude"],
            "Longitude": location["longitude"],
            "PunchesLocationId": location["id"],
            "IsOverride": True,
        }
    ).encode()
    headers = {
        "Authorization": access_token["id_token"],
        "Content-type": "application/x-www-form-urlencoded; charset=utf-8",
        "User-Agent": USER_AGENT,
        "actioncode": "Default",
        "functioncode": "APP-LocationCheckin",
    }
    req = urllib.request.Request(url, data=data, method="POST", headers=headers)
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


if __name__ == "__main__":
    company_code = os.getenv("COMPANY_CODE")
    employee_no = os.getenv("EMPLOYEE_NO")
    password = os.getenv("PASSWORD")
    punch_type = PunchType[sys.argv[1].upper()]
    location = sys.argv[2].upper()

    print(punch(company_code, employee_no, password, punch_type, location))
