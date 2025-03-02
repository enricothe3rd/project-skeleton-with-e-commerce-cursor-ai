import json
import requests
from django.conf import settings
from payroll.utils.general.general import Queries, ParseValues, EvaluateQueryResults
from payroll.utils.queries.employees import EmployeeOnboardingQueries as Employee
from payroll.utils.queries.read.read_config import GetCompanyConfig


class UsersOnboardingQueries:
    def __init__(self, request):
        self.request = request
        self.body = json.loads(request.body)
        if "company_id" in self.body:
            self.config = GetCompanyConfig(self.body["company_id"]).execute()

    def create(self):
        body = self.body
        payload = {
            "operations": body["operations"],
            "data": {
                "details": body["data"]["users"],
                "credentials": body["data"]["credentials"]
            }
        }
        result = self._save_user(payload, '/users/crud-users')
        if result["status"]:
            if self.config["force_user_employee_link"]:
                if (body["data"]["users"]["associated_user_id"] != "" and
                        body["data"]["users"]["associated_user_id"] is not None and
                        body["data"]["users"]["associated_user_id"] != 0):
                    Employee(self.request).change(id=result["id"])
                else:
                    Employee(self.request).create(id=result["id"])

            return {
                "status": True,
                "message": "Create new User or/and Employee was Successful",
                "password": self.body["data"]["credentials"]["password"]
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
                "details": body["data"]["users"],
                "credentials": body["data"]["credentials"]
            }
        }
        result = self._save_user(payload, '/users/crud-users')
        if result["status"]:
            if self.config["force_user_employee_link"]:
                Employee(self.request).change(id=result["id"])
            return {
                "status": True,
                "message": "Update of User or/and Employee was Successful",
                "password": self.body["data"]["credentials"]["password"]
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

    def update_password(self):
        payload = self.body
        result = self._save_user(payload, '/users/user-password-change')
        # return result
        if result["status"]:
            return {
                "status": True,
                "message": "Password was successfully updated."
            }
        else:
            return {
                "status": False,
                "message": "Password update error."
            }

    def _save_user(self, payload, path):
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

    def excel_import(self):
        data = self.request
        payload = self.body
        cookies = {
            'company_id': data.COOKIES['company_id'],
            'token': data.COOKIES['token'],
            'user_id': data.COOKIES['user_id'],
        }
        response = requests.post(
            settings.USER_SERVICE_URL + "/users/excel-import",
            json=payload,
            cookies=cookies,
            verify=False
        )
        response_dict = response.json()
        return response_dict
