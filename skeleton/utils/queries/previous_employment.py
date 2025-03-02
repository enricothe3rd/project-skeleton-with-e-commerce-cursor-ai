import json
from payroll.models.setup import (EmployeeContractTemplate, LeaveTemplate, AllowanceTemplate,
                                  DeductionTemplateGroup, WorkSetup, ScheduleTemplate)
from payroll.models.core import PreviousEmployer, Employee
from payroll.utils.general.general import Queries, ParseValues, EvaluateQueryResults


class PreviousEmploymentQueries:
    def __init__(self, requests, employee_id):
        self.request = requests
        self.body = json.loads(requests.body)
        self.employee = employee_id

    def create(self):
        try:
            data = self.body['data']['previous_employment']
            parse_date = ParseValues([data['employed_from'], data['employed_to']]).parse_date_from_string()
            result = []
            params = {
                "employee": self.employee,
                "previous_employer_name": data["previous_employer_name"],
                "previous_employer_address": data["previous_employer_address"],
                "tin": data["tin"],
                "zip": data["zip"],
                "separation_reason": data["separation_reason"],
                "employment_status": data["employment_status"],
                "employed_from": parse_date[0],
                "employed_to": parse_date[1],
                "gross_compensation_income": data["gross_compensation_income"],
                "statutory_smw": data["statutory_smw"],
                "holiday_pay": data["holiday_pay"],
                "overtime": data["overtime"],
                "night_shift": data["night_shift"],
                "hazard_pay": data["hazard_pay"],
                "r13th_month": data["r13th_month"],
                "de_minimis": data["de_minimis"],
                "statutory": data["statutory"],
                "salaries_other_compensation_non_tax": data["salaries_other_compensation_non_tax"],
                "total_non_taxable": data["total_non_taxable"],
                "r13th_month_other_benefits": data["r13th_month_other_benefits"],
                "salaries_other_compensation_tax": data["salaries_other_compensation_tax"],
                "taxable_amount": data["taxable_amount"],
                "taxes_withheld": data["taxes_withheld"],
                "is_fresh_graduate": data["is_fresh_graduate"],
            }
            result.append(Queries(PreviousEmployer).execute_create(params))
            return EvaluateQueryResults(result).execute_query_results()
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def change(self):
        try:
            data = self.body['data']['previous_employment']
            employee = self.employee

            if data['id'] == '':
                self.employee = Employee(id=employee)
                return self.create()
            else:
                parse_date = ParseValues([data['employed_from'], data['employed_to']]).parse_date_from_string()
                result = []
                params = {
                    "employee": self.employee,
                    "previous_employer_name": data["previous_employer_name"],
                    "previous_employer_address": data["previous_employer_address"],
                    "tin": data["tin"],
                    "zip": data["zip"],
                    "separation_reason": data["separation_reason"],
                    "employment_status": data["employment_status"],
                    "employed_from": parse_date[0],
                    "employed_to": parse_date[1],
                    "gross_compensation_income": data["gross_compensation_income"],
                    "statutory_smw": data["statutory_smw"],
                    "holiday_pay": data["holiday_pay"],
                    "overtime": data["overtime"],
                    "night_shift": data["night_shift"],
                    "hazard_pay": data["hazard_pay"],
                    "r13th_month": data["r13th_month"],
                    "de_minimis": data["de_minimis"],
                    "statutory": data["statutory"],
                    "salaries_other_compensation_non_tax": data["salaries_other_compensation_non_tax"],
                    "total_non_taxable": data["total_non_taxable"],
                    "r13th_month_other_benefits": data["r13th_month_other_benefits"],
                    "salaries_other_compensation_tax": data["salaries_other_compensation_tax"],
                    "taxable_amount": data["taxable_amount"],
                    "taxes_withheld": data["taxes_withheld"],
                    "is_fresh_graduate": data["is_fresh_graduate"],
                }
                result.append(Queries(PreviousEmployer).execute_change(params, data['id']))
                return EvaluateQueryResults(result).execute_query_results()
        except KeyError as key_err:
            print(str(key_err))
            return {"error": str(key_err)}
        except Exception as ex:
            print(str(ex))
            return {"error": str(ex)}

    def deactivate(self):
        pass

    def reactivate(self):
        pass

    def excel_import(self):
        pass
