import json
from payroll.utils.general.general import Queries, ParseValues, EvaluateQueryResults
from payroll.models.setup import AllowanceCategory, AllowanceTemplate, AllowanceTemplateLine
from payroll.models.core import (Allowance, Employee)


class AllowanceCategoryQueries:
    def __init__(self, requests):
        self.request = requests
        self.body = json.loads(requests.body)

    def create(self):
        try:
            company_id = self.request.COOKIES['company_id']
            body = self.body['data']

            params = {
                "name": body['name'],
                "company_id": company_id
            }
            result = Queries(AllowanceCategory).execute_create(params)

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
            }
            result = Queries(AllowanceCategory).execute_change(params, body['id'])

            return result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def deactivate(self):
        try:
            body = self.body['data']
            result = Queries(AllowanceCategory).execute_deactivate(body['id'])

            return result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def reactivate(self):
        try:
            body = self.body['data']
            result = Queries(AllowanceCategory).execute_reactivate(body['id'])

            return result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def validate(self):
        pass

    def read(self):
        pass

    def create_update(self):
        try:
            results = []
            for values in self.body:
                if values["id"] != "" and values["id"] and not None and values["id"] != 0:
                    params = {
                        "name": values["name"],
                        "is_pro_rated": values["is_pro_rated"],
                        "is_de_minimis": values["is_de_minimis"],
                        "max_untaxable_amount": values["max_untaxable_amount"],
                    }
                    results.append(Queries(AllowanceCategory).execute_change(params, values["id"]))
                else:
                    params = {
                        "name": values["name"],
                        "is_pro_rated": values["is_pro_rated"],
                        "is_de_minimis": values["is_de_minimis"],
                        "max_untaxable_amount": values["max_untaxable_amount"],
                        "company_id": self.request.COOKIES['company_id']
                    }
                    results.append(Queries(AllowanceCategory).execute_create(params))
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
            result = Queries(AllowanceCategory).execute_deactivate(data["id"])

            if result[0]["status"]:
                return {
                    "status": True,
                    "message": "Allowance Category was archived.",
                    "error": None
                }
            else:
                return {
                    "status": False,
                    "message": "Archive of Allowance Category failed.",
                    "error": "Archive Failed"
                }
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def excel_import(self):
        pass


class AllowanceTemplateQueries:
    def __init__(self, requests):
        self.request = requests
        self.body = json.loads(requests.body)

    def create(self):
        try:
            company_id = self.request.COOKIES['company_id']
            header = self.body['headers']

            head_params = {
                "name": header['name'],
                "company_id": company_id
            }
            header_result = Queries(AllowanceTemplate).execute_create(head_params)

            for line in self.body['lines']:
                category_object = AllowanceCategory(id=line['category_id'])
                parse_date = ParseValues([line['date_from'], line['date_to']]).parse_date()

                line_params = {
                    "name": line['name'],
                    "allowance_template_id": header_result[1],
                    "category_id": category_object,
                    "amount": line['amount'],
                    "date_from": parse_date[0],
                    "date_to": parse_date[1],
                    "is_vatable": line['is_vatable']
                }
                res = Queries(AllowanceTemplateLine).execute_create(line_params)

            return header_result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def change(self):
        try:
            header = self.body['headers']
            debug = []

            head_params = {
                "name": header['name']
            }
            head_result = Queries(AllowanceTemplate).execute_change(head_params, header['id'])

            for line in self.body['lines']:
                parse_date = ParseValues([line['date_from'], line['date_to']]).parse_date()

                if line['id'] == "New" or line['id'] is None or line['id'] == "":
                    # Trigger CREATE
                    category_object = AllowanceCategory(id=line['category_id'])
                    header_object = AllowanceTemplate(id=header['id'])

                    line_params = {
                        "allowance_template_id": header_object,
                        "name": line['name'],
                        "category_id": category_object,
                        "amount": line['amount'],
                        "date_from": parse_date[0],
                        "date_to": parse_date[1],
                        "is_vatable": line['is_vatable']
                    }
                    Queries(AllowanceTemplateLine).execute_create(line_params)
                    debug.append("ADD: " + (line['id']))
                else:
                    # Trigger UPDATE
                    line_params = {
                        "allowance_template_id": head_result[0]['id'],
                        "name": line['name'],
                        "category_id": line['category_id'],
                        "amount": line['amount'],
                        "date_from": parse_date[0],
                        "date_to": parse_date[1],
                        "is_vatable": line['is_vatable']
                    }
                    Queries(AllowanceTemplateLine).execute_change(line_params, line['id'])
                    debug.append("Update: " + str(line['id']))

            return [head_result[0], debug]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def deactivate(self):
        try:
            body = self.body['data']

            result = Queries(AllowanceTemplate).execute_deactivate(body['id'])

            return result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def reactivate(self):
        try:
            body = self.body['data']

            result = Queries(AllowanceTemplate).execute_deactivate(body['id'])

            return result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def validate(self):
        pass

    def read(self):
        pass


class AllowanceQueries:
    def __init__(self, requests, employee):
        self.request = requests
        self.body = json.loads(requests.body)
        self.employee = employee

    def create(self):
        try:
            company_id = self.request.COOKIES['company_id']
            allowances = self.body['data']['allowances']
            results = []

            for allowance_det in allowances:
                parse_date = (ParseValues([allowance_det['date_from'], allowance_det['date_to']])
                              .parse_date_from_string())
                category_object = AllowanceCategory(id=allowance_det['allowance_category_id'])
                employee_object = self.employee

                params = {
                    "name": allowance_det['name'],
                    "category_id": category_object,
                    "employee_id": employee_object,
                    "amount": allowance_det['amount'],
                    "date_from": parse_date[0],
                    "date_to": parse_date[1],
                    "is_vatable": allowance_det['is_vatable'],
                    "company_id": company_id
                }

                results.append(Queries(Allowance).execute_create(params))

            return EvaluateQueryResults(results).execute_query_results()
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def change(self):
        try:
            company_id = self.request.COOKIES['company_id']
            allowances = self.body['data']['allowances']
            results = []

            for allowance_det in allowances:
                allowance_id = allowance_det['id']

                parse_date = (ParseValues([allowance_det['date_from'], allowance_det['date_to']])
                              .parse_date_from_string())

                params = {
                    "name": allowance_det['name'],
                    "amount": allowance_det['amount'],
                    "date_from": parse_date[0],
                    "date_to": parse_date[1],
                    "is_vatable": allowance_det['is_vatable'],
                    "company_id": company_id
                }

                if allowance_id == "":
                    params["category_id"] = AllowanceCategory(id=allowance_det['allowance_category_id'])
                    params["employee_id"] = Employee(id=self.employee)
                    results.append(Queries(Allowance).execute_create(params))
                else:
                    params["category_id"] = allowance_det['allowance_category_id']
                    params["employee_id"] = self.employee
                    results.append(Queries(Allowance).execute_change(params, allowance_id))

            return EvaluateQueryResults(results).execute_query_results()
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def deactivate(self):
        try:
            allowances = self.body['archive']['allowances']
            result = []

            if len(allowances) > 0:
                for allowance in allowances:
                    result.append(Queries(Allowance).execute_deactivate(allowance))

            return result
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def reactivate(self):
        try:
            body = self.body['data']

            result = Queries(Allowance).execute_reactivate(body['id'])

            return result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def remove(self):
        pass

    def validate(self):
        pass

    def read(self):
        pass

    def excel_import(self):
        pass
