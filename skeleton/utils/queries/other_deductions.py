import json
from payroll.utils.general.general import Queries, ParseValues, EvaluateQueryResults
from payroll.models.core import (OtherDeductions)


class OtherDeductionsCRUD:
    def __init__(self, requests):
        self.request = requests
        self.body = json.loads(requests.body)

    def create_update(self):
        try:
            results = []
            for values in self.body:
                date_from = ParseValues([values["date_from"]]).parse_date_from_string()[0]
                date_to = ParseValues([values["date_to"]]).parse_date_from_string()[0]
                if values["id"] != "" and values["id"] and not None and values["id"] != 0:
                    params = {
                        "name": values["name"],
                        "total_amount": values["total_amount"],
                        "amount_per_month": values["amount_per_month"],
                        "date_from": date_from,
                        "date_to": date_to,
                        "no_of_months": values["no_of_months"],
                        "deduction_category_id": values["deduction_category_id"],
                        "employee_id_id": values["employee_id_id"]
                    }
                    results.append(Queries(OtherDeductions).execute_change(params, values["id"]))
                else:
                    params = {
                        "name": values["name"],
                        "total_amount": values["total_amount"],
                        "amount_per_month": values["amount_per_month"],
                        "date_from": date_from,
                        "date_to": date_to,
                        "no_of_months": values["no_of_months"],
                        "deduction_category_id": values["deduction_category_id"],
                        "employee_id_id": values["employee_id_id"]
                    }
                    results.append(Queries(OtherDeductions).execute_create(params))
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
            result = Queries(OtherDeductions).execute_deactivate(data["id"])

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
