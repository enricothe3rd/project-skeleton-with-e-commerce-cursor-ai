import json
from payroll.utils.general.general import Queries, EvaluateQueryResults
from payroll.models.core import EmployeePositions, Department, PositionsEmployeeRel, Employee


# CONTAINS POSITION LINES
class PositionsQueries:
    def __init__(self, requests):
        self.request = requests
        self.body = json.loads(requests.body)

    def create(self):
        try:
            company_id = self.request.COOKIES['company_id']
            body = self.body['data']
            department_obj = Department(id=body['department_id'])

            params = {
                "name": body['name'],
                "department_id": department_obj,
                "company_id": company_id
            }
            result = Queries(EmployeePositions).execute_create(params)

            return result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def change(self):
        try:
            body = self.body['data']

            params = {
                "name": body['name'],
                "department_id": body['department_id'],
            }
            result = Queries(EmployeePositions).execute_change(params, body['id'])

            return result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def deactivate(self):
        try:
            body = self.body['data']
            result = Queries(EmployeePositions).execute_deactivate(body['id'])

            return result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def reactivate(self):
        try:
            body = self.body['data']
            result = Queries(EmployeePositions).execute_reactivate(body['id'])

            return result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def validate(self):
        pass

    def read(self):
        pass


class PositionsRelQueries:
    def __init__(self, requests, employee_id):
        self.request = requests
        self.body = json.loads(requests.body)
        self.employee = employee_id

    def create(self):
        try:
            employee = self.employee
            position_rel_data = self.body['data']['positions']
            results = []

            for position in position_rel_data:
                position_obj = EmployeePositions(id=position['position_id'])

                params = {
                    "employee_id": employee,
                    "position_id": position_obj,
                    "is_primary": position['is_primary']
                }
                results.append(Queries(PositionsEmployeeRel).execute_create(params))

            return EvaluateQueryResults(results).execute_query_results()
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def change(self):
        try:
            employee = self.employee
            position_rel_data = self.body['data']['positions']
            results = []

            for position in position_rel_data:
                rel_id = position['id']

                params = {
                    "is_primary": position['is_primary']
                }

                if rel_id == "":
                    params["position_id"] = EmployeePositions(id=position['position_id'])
                    params["employee_id"] = Employee(id=employee)
                    results.append(Queries(PositionsEmployeeRel).execute_create(params))
                else:
                    params["position_id"] = position['position_id']
                    params["employee_id"] = employee
                    results.append(Queries(PositionsEmployeeRel).execute_change(params, rel_id))

            return EvaluateQueryResults(results).execute_query_results()
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def deactivate(self):
        try:
            body = self.body['data']
            result = Queries(EmployeePositions).execute_deactivate(body['id'])

            return result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def reactivate(self):
        try:
            body = self.body['data']
            result = Queries(EmployeePositions).execute_reactivate(body['id'])

            return result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def remove(self):
        try:
            positions_rel = self.body['archive']['positions']
            result = []

            if len(positions_rel) > 0:
                print(positions_rel)
                for position_rel in positions_rel:
                    result.append(Queries(PositionsEmployeeRel).execute_unrestricted_delete(position_rel))

            return result
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def validate(self):
        pass

    def read(self):
        pass


class PositionsCRUD:
    def __init__(self, requests):
        self.request = requests
        self.body = json.loads(requests.body)

    def create_update(self):
        try:
            data = self.body
            results = []
            print(data)
            for values in data:
                if values["id"] != "" and values["id"] and not None and values["id"] != 0:
                    params = {
                        "name": values["name"],
                        "supervisor_id": values["supervisor_id"],
                        "department_id_id": values["department_id"]
                    }
                    results.append(Queries(EmployeePositions).execute_change(params, values["id"]))
                else:
                    params = {
                        "name": values["name"],
                        "supervisor_id": values["supervisor_id"],
                        "department_id_id": values["department_id"],
                        "company_id": self.request.COOKIES['company_id']
                    }
                    results.append(Queries(EmployeePositions).execute_create(params))
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
            print(data)
            result = Queries(EmployeePositions).execute_deactivate(data["id"])

            if result[0]["status"]:
                return {
                    "status": True,
                    "message": "Department was archived.",
                    "error": None
                }
            else:
                return {
                    "status": False,
                    "message": "Archive of department failed.",
                    "error": "Archive Failed"
                }
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def excel_import(self):
        pass
