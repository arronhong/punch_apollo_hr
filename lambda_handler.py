import os
from datetime import datetime
from zoneinfo import ZoneInfo

from punch_apollo_hr import PunchType, punch


def lambda_handler(event, context):
    company_code = os.getenv("COMPANY_CODE")
    employee_no = os.getenv("EMPLOYEE_NO")
    password = os.getenv("PASSWORD")
    location = os.getenv("LOCATION")
    punch_time = datetime.strptime(event["time"], "%Y-%m-%dT%H:%M:%S%z")
    punch_time = punch_time.astimezone(ZoneInfo("Asia/Taipei"))
    if punch_time.hour < 12:
        punch_type = PunchType.PUNCH_IN
    else:
        punch_type = PunchType.PUNCH_OUT

    ret = punch(company_code, employee_no, password, punch_type, location)
    print(
        {
            "type": punch_type.name,
            "location": ret.get("Data", {}).get("LocationName"),
            "punched_at": ret.get("Data", {}).get("punchDate"),
        }
    )


if __name__ == "__main__":
    event = {
        "id": "cdc73f9d-aea9-11e3-9d5a-835b769c0d9c",
        "detail-type": "Scheduled Event",
        "source": "aws.events",
        "account": "123456789012",
        "time": "2023-01-01T10:42:13Z",
        "region": "us-east-1",
        "resources": ["arn:aws:events:us-east-1:123456789012:rule/ExampleRule"],
        "detail": {},
    }
    lambda_handler(event, None)
