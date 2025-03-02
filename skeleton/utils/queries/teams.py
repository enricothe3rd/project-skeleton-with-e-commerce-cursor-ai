import json
from payroll.utils.general.general import Queries, ParseValues, EvaluateQueryResults
from payroll.models.core import (Team)


class TeamsCRUD:
    def __init__(self, requests):
        self.request = requests
        self.body = json.loads(requests.body)

    def create_update(self):
        try:
            data = self.body
            results = []
            for values in data:
                if values["id"] != "" and values["id"] and not None and values["id"] != 0:
                    params = {
                        "name": values["name"],
                        "manager_id": values["manager_id"],
                        "department_id": values["department_id"]
                    }
                    results.append(Queries(Team).execute_change(params, values["id"]))
                else:
                    params = {
                        "name": values["name"],
                        "manager_id": values["manager_id"],
                        "department_id": values["department_id"],
                        "company_id": self.request.COOKIES['company_id']
                    }
                    results.append(Queries(Team).execute_create(params))
            if EvaluateQueryResults(results).execute_query_results():
                return {
                    "status": True,
                    "message": "All records was saved/updated successfully!",
                    "error": None
                }
            else:
                return {
                    "status": False,
                    "message": "Not all records was saved/updated.",
                    "error": None
                }
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def archive(self):
        try:
            data = self.body
            result = Queries(Team).execute_deactivate(data["id"])

            if result[0]["status"]:
                return {
                    "status": True,
                    "message": "Team was archived.",
                    "error": None
                }
            else:
                return {
                    "status": False,
                    "message": "Archive of team failed.",
                    "error": "Archive Failed"
                }
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def excel_import(self):
        pass
