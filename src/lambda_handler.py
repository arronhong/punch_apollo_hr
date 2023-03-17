import os

from punch_apollo_hr import PunchType, punch


def lambda_handler(event, context):
    company_code = os.getenv("COMPANY_CODE")
    employee_no = os.getenv("EMPLOYEE_NO")
    password = os.getenv("PASSWORD")
    location = os.getenv("LOCATION")
    punch_type = PunchType[event["action"].upper()]

    ret = punch(company_code, employee_no, password, punch_type, location)
    print(
        {
            "type": punch_type.name,
            "location": ret.get("Data", {}).get("LocationName"),
            "punched_at": ret.get("Data", {}).get("punchDate"),
        }
    )


if __name__ == "__main__":
    event = {"action": "punch_out"}
    lambda_handler(event, None)
