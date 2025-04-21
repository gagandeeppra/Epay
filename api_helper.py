import requests
import json

def post():
    body = {
        "employersSitesList": [
            {
            "employerId": 227999,
            "siteId": 31209421
            }
        ],
        "lookBackWindowsInMinutes": 0,
        "managerIdList": [
            {
            "employeeId": 0
            }
        ],
        "processId": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    }
    response = requests.post("https://nexd.epaysystems.com/employee/v1/TimeClockEmployee/Employees", json=body)
    employeeTaskTypeList = json.loads(response.text)["data"]["employeeTaskTypeList"]
    print(len(employeeTaskTypeList))

