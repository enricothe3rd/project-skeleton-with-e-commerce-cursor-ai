import json
from payroll.utils.general.general import Queries, ParseValues, EvaluateQueryResults, execute_raw_query
from payroll.utils.queries.statements import select as statements
from payroll.models.setup import (DeductionCategory, DeductionTemplateGroup,
                                  DeductionTemplate, DeductionMatrixTemplate, DeductionGroupTemplateRel)
from payroll.models.core import (DeductionMatrix, Deduction, Employee, DeductionEmployeeRel)


class DeductionCategoryQueries:
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
            result = Queries(DeductionCategory).execute_create(params)

            return result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def change(self):
        try:
            body = self.body['data']

            params = {
                "name": body['name']
            }
            result = Queries(DeductionCategory).execute_change(params, body['id'])

            return result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def deactivate(self):
        try:
            body = self.body['data']
            result = Queries(DeductionCategory).execute_deactivate(body['id'])

            return result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def reactivate(self):
        try:
            body = self.body['data']
            result = Queries(DeductionCategory).execute_reactivate(body['id'])

            return result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def read(self):
        pass

    def validate(self):
        pass

    def create_update(self):
        try:
            data = self.body
            results = []
            for values in data:
                if values["id"] != "" and values["id"] and not None and values["id"] != 0:
                    params = {
                        "name": values["name"],
                    }
                    results.append(Queries(DeductionCategory).execute_change(params, values["id"]))
                else:
                    params = {
                        "name": values["name"],
                        "company_id": self.request.COOKIES['company_id']
                    }
                    results.append(Queries(DeductionCategory).execute_create(params))
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
            result = Queries(DeductionCategory).execute_deactivate(data["id"])

            if result[0]["status"]:
                return {
                    "status": True,
                    "message": "Deduction Category was archived.",
                    "error": None
                }
            else:
                return {
                    "status": False,
                    "message": "Archive of Deduction Category failed.",
                    "error": "Archive Failed"
                }
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def excel_import(self):
        pass


class DeductionTemplateQueries:
    def __init__(self, requests):
        self.request = requests
        self.body = json.loads(requests.body)

    def create(self):
        try:
            company_id = self.request.COOKIES['company_id']
            header = self.body['header']
            category_object = DeductionCategory(id=header['category_id'])

            head_params = {
                "name": header['name'],
                "category_id": category_object,
                "is_mandatory": header['is_mandatory'],
                "company_id": company_id
            }
            head_result = Queries(DeductionTemplate).execute_create(head_params)

            for line in self.body['lines']:
                parse_date = ParseValues([line['date_from'], line['date_to']]).parse_date()

                line_params = {
                    "deduction_template_id": head_result[1],
                    "deduction_type": line['deduction_type'],
                    "fixed_amount": line['fixed_amount'],
                    "salary_from": line['salary_from'],
                    "salary_to": line['salary_to'],
                    "percentage_amount": line['percentage_amount'],
                    "date_from": parse_date[0],
                    "date_to": parse_date[1]
                }
                Queries(DeductionMatrixTemplate).execute_create(line_params)

            return head_result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def change(self):
        try:
            header = self.body['header']

            head_params = {
                "name": header['name'],
                "category_id": header['category_id'],
                "is_mandatory": header['is_mandatory'],
            }
            head_result = Queries(DeductionTemplate).execute_change(head_params, header['id'])

            for line in self.body['line']:
                parse_date = ParseValues([line['date_from'], line['date_to']]).parse_date()

                if line['id'] == "New" or line['id'] is not None or line['id'] == "":
                    # TRIGGER CREATE
                    header_object = DeductionTemplate(id=head_result[0]['id'])
                    line_params = {
                        "deduction_template_id": header_object,
                        "deduction_type": line['deduction_type'],
                        "fixed_amount": line['fixed_amount'],
                        "salary_from": line['salary_from'],
                        "salary_to": line['salary_to'],
                        "percentage_amount": line['percentage_amount'],
                        "date_from": parse_date[0],
                        "date_to": parse_date[1],
                    }
                    Queries(DeductionMatrixTemplate).execute_create(line_params)
                else:
                    # TRIGGER UPDATE
                    line_params = {
                        "deduction_template_id": head_result[0]['id'],
                        "deduction_type": line['deduction_type'],
                        "fixed_amount": line['fixed_amount'],
                        "salary_from": line['salary_from'],
                        "salary_to": line['salary_to'],
                        "percentage_amount": line['percentage_amount'],
                        "date_from": parse_date[0],
                        "date_to": parse_date[1],
                    }
                    Queries(DeductionMatrixTemplate).execute_change(line_params, line['id'])

            return head_result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def deactivate(self):
        try:
            body = self.body['header']

            result = Queries(DeductionTemplate).execute_deactivate(body['id'])

            return result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def reactivate(self):
        try:
            body = self.body['header']

            result = Queries(DeductionTemplate).execute_reactivate(body['id'])

            return result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def read(self):
        pass

    def validate(self):
        pass


class DeductionGroupQueries:
    def __init__(self, requests):
        self.request = requests
        self.body = json.loads(requests.body)

    def create(self):
        try:
            company_id = self.request.COOKIES['company_id']
            header = self.body['header']

            head_params = {
                "name": header['name'],
                "company_id": company_id
            }
            head_result = Queries(DeductionTemplateGroup).execute_create(head_params)

            # VALIDATE THERE SHALL BE NO DUPLICATE DEDUCTION TEMPLATE
            for line in self.body['line']:
                deduction_template_object = DeductionTemplate(id=line['template_id'])
                line_params = {
                    "deduction_template_group_id": head_result[1],
                    "deduction_template_id": deduction_template_object
                }
                Queries(DeductionGroupTemplateRel).execute_create(line_params)

            return head_result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def change(self):
        try:
            header = self.body['header']

            params = {
                "name": header['name']
            }
            result = Queries(DeductionTemplateGroup).execute_change(params, header['id'])

            return result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def delete_line(self):
        try:
            line = self.body['line']

            result = Queries(DeductionGroupTemplateRel).execute_unrestricted_delete(line['id'])

            return result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def read(self):
        pass

    def validate(self):
        pass


class DeductionQueries:
    def __init__(self, requests, employee):
        self.request = requests
        self.body = json.loads(requests.body)
        self.employee_obj = employee

    def create(self):
        try:
            company_id = self.request.COOKIES['company_id']
            deductions = self.body['data']['deductions']
            results = []

            for deductions_det in deductions:
                header = deductions_det['headers']
                category_object = DeductionCategory(id=header['category_id'])
                parse_date = ParseValues([header['date_from'], header['date_to']]).parse_date_from_string()

                params = {
                    "name": header['name'],
                    "employee_id": self.employee_obj,
                    "category_id": category_object,
                    "is_mandatory": header['is_mandatory'],
                    "date_from": parse_date[0],
                    "date_to": parse_date[1],
                    "company_id": company_id
                }

                head_result = Queries(Deduction).execute_create(params)
                results.append(head_result)

                for line in deductions_det['lines']:
                    line_params = {
                        "deduction_id": head_result[1],
                        "deduction_type": line['deduction_type'],
                        "fixed_amount": line['fixed_amount'],
                        "employee_share": line['employee_share'],
                        "salary_from": line['salary_from'],
                        "salary_to": line['salary_to'],
                        "percentage_amount": line['percentage_amount']
                    }
                    results.append(Queries(DeductionMatrix).execute_create(line_params))

            return EvaluateQueryResults(results).execute_query_results()
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def change(self):
        try:
            company_id = self.request.COOKIES['company_id']
            header = self.body['header']

            employee_object = Employee(id=header['id'])
            category_object = DeductionCategory(id=header['category_id'])

            params = {
                "name": header['name'],
                "employee_id": employee_object,
                "category_id": category_object,
                "is_mandatory": header['is_mandatory'],
                "company_id": company_id
            }

            head_result = Queries(Deduction).execute_change(params, header['id'])

            for line in self.body['lines']:
                parse_date = ParseValues(([line['date_from'], line['date_to']])).parse_date()

                if line['id'] == "New" or line['id'] is not None or line['id'] == "":
                    # TRIGGER CREATE
                    header_object = Deduction(id=head_result[0]['id'])
                    line_params = {
                        "deduction_template_id": header_object,
                        "deduction_type": line['deduction_type'],
                        "fixed_amount": line['fixed_amount'],
                        "salary_from": line['salary_from'],
                        "salary_to": line['salary_to'],
                        "percentage_amount": line['percentage_amount'],
                        "date_from": parse_date[0],
                        "date_to": parse_date[1],
                    }
                    Queries(DeductionMatrix).execute_create(line_params)
                else:
                    # TRIGGER UPDATE
                    line_params = {
                        "deduction_template_id": head_result[0]['id'],
                        "deduction_type": line['deduction_type'],
                        "fixed_amount": line['fixed_amount'],
                        "salary_from": line['salary_from'],
                        "salary_to": line['salary_to'],
                        "percentage_amount": line['percentage_amount'],
                        "date_from": parse_date[0],
                        "date_to": parse_date[1],
                    }
                    Queries(DeductionMatrix).execute_change(line_params, line['id'])

            return head_result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def deactivate(self):
        try:
            body = self.body['header']

            result = Queries(Deduction).execute_deactivate(body['id'])

            return result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def reactivate(self):
        try:
            body = self.body['header']

            result = Queries(Deduction).execute_reactivate(body['id'])

            return result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def delete_line(self):
        try:
            data = self.body['line']

            result = Queries(Deduction).execute_unrestricted_delete(data['id'])

            return result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def validate(self):
        pass

    def read(self):
        pass


class DeductionEmployeeRelQueries:
    def __init__(self, requests, employee):
        self.request = requests
        self.body = json.loads(requests.body)
        self.employee = employee

    def create(self):
        try:
            deductions = self.body['data']['deductions']
            results = []

            for deduction in deductions:
                deduction_object = Deduction(id=deduction['deduction_id'])

                params = {
                    "deduction_id": deduction_object,
                    "employee_id": self.employee
                }

                results.append(Queries(DeductionEmployeeRel).execute_create(params))

            return EvaluateQueryResults(results).execute_query_results()

        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def change(self):
        try:
            deductions = self.body['data']['deductions']
            results = []

            for deduction in deductions:
                rel_id = deduction['id']

                params = {}

                if rel_id == "":
                    params["deduction_id"] = Deduction(id=deduction['deduction_id'])
                    params["employee_id"] = Employee(id=self.employee)
                    results.append(Queries(DeductionEmployeeRel).execute_create(params))
                else:
                    params["deduction_id"] = deduction['deduction_id']
                    params["employee_id"] = self.employee
                    results.append(Queries(DeductionEmployeeRel).execute_change(params, rel_id))

            return EvaluateQueryResults(results).execute_query_results()

        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def deactivate(self):
        pass

    def reactivate(self):
        pass

    def remove(self):
        try:
            deductions_rel = self.body['archive']['deductions']
            result = []

            if len(deductions_rel) > 0:
                for deduction_rel in deductions_rel:
                    result.append(Queries(DeductionEmployeeRel).execute_unrestricted_delete(deduction_rel))

            return result
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def delete_line(self):
        pass

    def excel_import(self):
        try:
            deductions = self.body["data"]
            results = []
            matching_status = True
            compare_list_raw = self._fetch_related_data()

            for deduction in deductions:
                relational_validations = {"employee": False, "statutory": False}
                for employee in compare_list_raw["employees"]:
                    employee_name = "{}{}{}{}".format(employee["first_name"], employee["middle_name"],
                                                      employee["last_name"], employee["suffix"])
                    if deduction["employee_id"].replace(' ', '') == employee_name.replace(' ', '')\
                            and deduction["employee_id"] is not None:
                        deduction["employee_id"] = employee["id"]
                        relational_validations["employee"] = True
                        break
                for statutory in compare_list_raw["deductions"]:
                    if deduction["department_id"] == statutory["name"] and deduction["department_id"] is not None:
                        deduction["department_id"] = statutory["id"]
                        relational_validations["departments"] = True
                        break
                if not relational_validations["statutory"]:
                    deduction["deduction_id"] = None
                if not relational_validations["employee"]:
                    matching_status = False
                    break
            if matching_status:
                for deduction in deductions:
                    params = {
                        "deduction_id_id": deduction["deduction_id"],
                        "employee_id_id": deduction["employee_id"],
                        "force_employee_share": deduction["force_employee_share"],
                        "force_employer_share": deduction["force_employer_share"]
                    }
                    result = Queries(DeductionEmployeeRelQueries).execute_create(params)
                    results.append(result[0]["result"])
                return results
            else:
                return {"result": False, "message": "Error in the Deductions template."}
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def _fetch_related_data(self):
        company_id = self.body["company_id"]
        return {
            "employees": execute_raw_query(statements.get_all_employees.format(company_id)),
            "deductions": execute_raw_query(statements.get_all_statutory_deductions),
        }
