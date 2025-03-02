import json
import requests
from django.conf import settings
from payroll.utils.general.general import Queries, ParseValues, EvaluateQueryResults
from payroll.utils.queries.employees import EmployeeOnboardingQueries as Employee
from payroll.utils.queries.read.read_config import GetCompanyConfig


class CompaniesOnboardingQueries:
    def __init__(self, request):
        self.request = request
        self.body = json.loads(request.body)
        self.config = GetCompanyConfig(self.body["company_id"]).execute()

    def create(self):
        body = self.body
        payload = {
            "operations": body["operations"],
            "data": {
                "company": body["data"]["company"],
                "address": body["data"]["address"]
            }
        }
        result = self._save_company(payload, '/users/crud-companies')
        if result["status"]:
            if self.config["force_user_employee_link"]:
                Employee(self.request).create(id=result["id"])

            return {
                "status": True,
                "message": "Create new User or/and Employee was Successful"
            }
        else:
            return {
                "status": False,
                "message": "Saving of User or/and Employee failed."
            }

    def change(self):
        body = self.body
        payload = {
            "operations": body["operations"],
            "data": {
                "company": body["data"]["company"],
                "address": body["data"]["address"]
            }
        }
        result = self._save_company(payload, '/users/crud-companies')
        if result["status"]:
            if self.config["force_user_employee_link"]:
                Employee(self.request).create(id=result["id"])

            return {
                "status": True,
                "message": "Create new User or/and Employee was Successful"
            }
        else:
            return {
                "status": False,
                "message": "Saving of User or/and Employee failed."
            }

    def deactivate(self):
        pass

    def reactivate(self):
        pass

    def _save_company(self, payload, path):
        data = self.request
        cookies = {
            'company_id': data.COOKIES['company_id'],
            'token': data.COOKIES['token'],
            'user_id': data.COOKIES['user_id'],
        }
        response = requests.post(
            settings.USER_SERVICE_URL + path,
            json=payload,
            cookies=cookies,
            verify=False
        )
        response_dict = response.json()
        if response_dict["result"]["status"]:
            return response_dict["result"]
        else:
            return {"error": "An error occurred!"}
