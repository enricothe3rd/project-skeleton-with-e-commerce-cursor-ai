import sys
import os
import json
from payroll.utils.general.general import (Queries, ParseValues, EvaluateQueryResults, execute_raw_query,
                                           execute_raw_query_insert, construct_ids_tuple, execute_raw_query_operations)
from payroll.utils.queries.statements import select_payroll_generate as statements
from payroll.models.core import (FiscalYear, FiscalYearLines, Releases, OtherBenefits, OtherBenefitsType,
                                 OtherIncomeType, OtherIncome, EarningAdjustments, Employee)


class PayrollQueries:
    def __init__(self, requests):
        self.request = requests

    def approvals(self):
        try:
            data = self.request["data"]
            params = {
                "approval_status": data["approval_status"],
                "approved_by_id": data["approved_by_id"]
            }

            result = Queries(Releases).execute_change(params, data["sid"])
            return result[0]["message"]
        except KeyError as key_err:
            print("key err: " + str(key_err))
            return {"Key Error": str(key_err)}
        except Exception as e:
            e_type, e_object, e_traceback = sys.exc_info()
            e_filename = os.path.split(
                e_traceback.tb_frame.f_code.co_filename
            )[1]
            e_message = str(e)
            e_line_number = e_traceback.tb_lineno
            return {"Ex Error": {
                "type": str(e_type),
                "filename": str(e_filename),
                "line": str(e_line_number),
                "message": str(e_message)
            }}

    def deactivate(self):
        try:
            body = json.loads(self.request.body)
            data = body["data"]
            result = Queries(Releases).execute_deactivate(data["sid"])
            print(result[0]["message"])
            return result[0]["message"]
        except KeyError as key_err:
            print("key err: " + str(key_err))
            return {"Key Error": str(key_err)}
        except Exception as e:
            e_type, e_object, e_traceback = sys.exc_info()
            e_filename = os.path.split(
                e_traceback.tb_frame.f_code.co_filename
            )[1]
            e_message = str(e)
            e_line_number = e_traceback.tb_lineno
            return {"Ex Error": {
                "type": str(e_type),
                "filename": str(e_filename),
                "line": str(e_line_number),
                "message": str(e_message)
            }}

    def change(self):
        try:
            body = json.loads(self.request.body)
            details = body["data"]
            other_incomes = details["other_income"]
            other_benefits = details["other_benefits"]
            earning_adjustments = details["earning_adjustment"]
            other_income_archived = details["archive_other_income"]
            other_benefits_archived = details["archive_other_benefits"]
            earning_adjustments_archived = details["archive_earning_adjustments"]
            parser = ParseValues

            fiscal_end_raw_obj = FiscalYear.objects.filter(is_active=True, company_id=details["company_id"])
            fiscal_end_values = fiscal_end_raw_obj.values()[0]
            fiscal_line_raw_obj = FiscalYearLines.objects.filter(fiscal_year_id=fiscal_end_values["id"],
                                                                 id=details["fiscal_month"])
            fiscal_line_values = fiscal_line_raw_obj.values()[0]
            date_values = (parser([details["date"], details["cutoff_from"], details["cutoff_to"]])
                           .parse_date_from_string())
            releases_params = {
                "date": date_values[0],
                "cutoff_date_from": date_values[1],
                "cutoff_date_to": date_values[2],
                "payroll_cycle": details["payroll_cycle"],
                "is_reviewed": False,
                "fiscal_year": fiscal_end_values["id"],
                "fiscal_year_line": fiscal_line_values["id"],
                "produce_gross_deductions": details["produce_gross_deductions"],
                "produce_basic_deductions": details["produce_basic_deductions"],
                "company_id": details["company_id"],
            }
            result_release = Queries(Releases).execute_change(releases_params, details["sid"])

            if result_release[0]["status"]:
                for other_income in other_incomes:
                    if other_income["id"] == 0 or other_income["id"] is None or other_income["id"] == "":
                        other_income_params = {
                            "employee_id": other_income["employee_id"],
                            "releases_id": result_release[0]["id"],
                            "other_income_type_id": other_income["other_income_type_id"],
                            "amount": other_income["amount"]
                        }
                        Queries(OtherIncome).execute_create(other_income_params)
                    else:
                        other_income_params = {
                            "employee_id": other_income["employee_id"],
                            "releases_id": result_release[0]["id"],
                            "other_income_type_id": other_income["other_income_type_id"],
                            "amount": other_income["amount"]
                        }
                        Queries(OtherIncome).execute_change(other_income_params, other_income["id"])

                for other_benefit in other_benefits:
                    if other_benefit["id"] == 0 or other_benefit["id"] is None or other_benefit["id"] == "":
                        other_benefits_params = {
                            "employee_id": other_benefit["employee_id"],
                            "releases_id": result_release[0]["id"],
                            "other_benefit_type": OtherBenefitsType(id=other_benefit["other_benefit_type_id"]),
                            "untaxable_threshold": other_benefit["untaxable_threshold"],
                            "amount": other_benefit["amount"]
                        }
                        Queries(OtherBenefits).execute_create(other_benefits_params)
                    else:
                        other_benefits_params = {
                            "employee_id": other_benefit["employee_id"],
                            "releases_id": result_release[0]["id"],
                            "other_benefit_type": other_benefit["other_benefit_type_id"],
                            "untaxable_threshold": other_benefit["untaxable_threshold"],
                            "amount": other_benefit["amount"]
                        }
                        Queries(OtherBenefits).execute_change(other_benefits_params, other_benefit["id"])

                for earning_adjustment in earning_adjustments:
                    if (earning_adjustment["id"] == 0 or earning_adjustment["id"] is None or
                            earning_adjustment["id"] == ""):
                        earning_adjustment_params = {
                            "employee_id": earning_adjustment["employee_id"],
                            "releases_id": result_release[0]["id"],
                            "adjustment_remarks": earning_adjustment["adjustment_remarks"],
                            "amount": earning_adjustment["amount"]
                        }
                        Queries(EarningAdjustments).execute_create(earning_adjustment_params)
                    else:
                        earning_adjustment_params = {
                            "employee_id": earning_adjustment["employee_id"],
                            "releases_id": result_release[0]["id"],
                            "adjustment_remarks": earning_adjustment["adjustment_remarks"],
                            "amount": earning_adjustment["amount"]
                        }
                        Queries(EarningAdjustments).execute_change(earning_adjustment_params, earning_adjustment["id"])

                for id_num in other_income_archived:
                    Queries(OtherIncome).execute_unrestricted_delete(id_num)

                for id_num in other_benefits_archived:
                    Queries(OtherBenefits).execute_unrestricted_delete(id_num)

                for id_num in earning_adjustments_archived:
                    Queries(EarningAdjustments).execute_unrestricted_delete(id_num)

            return str(result_release[0]["message"])
        except KeyError as key_err:
            print("key err: " + str(key_err))
            return {"Key Error": str(key_err)}
        except Exception as e:
            e_type, e_object, e_traceback = sys.exc_info()
            e_filename = os.path.split(
                e_traceback.tb_frame.f_code.co_filename
            )[1]
            e_message = str(e)
            e_line_number = e_traceback.tb_lineno
            return {"Ex Error": {
                "type": str(e_type),
                "filename": str(e_filename),
                "line": str(e_line_number),
                "message": str(e_message)
            }}

    def create(self):
        try:
            body = json.loads(self.request.body)
            details = body["data"]
            other_incomes = details["other_income"]
            other_benefits = details["other_benefits"]
            earning_adjustments = details["earning_adjustment"]
            parser = ParseValues

            fiscal_end_raw_obj = FiscalYear.objects.filter(is_active=True, company_id=details["company_id"])
            fiscal_end_values = fiscal_end_raw_obj.values()[0]
            fiscal_line_raw_obj = FiscalYearLines.objects.filter(fiscal_year_id=fiscal_end_values["id"],
                                                                 month=details["fiscal_month"])
            fiscal_line_values = fiscal_line_raw_obj.values()[0]
            fiscal_end_obj = FiscalYear(id=fiscal_end_values["id"])
            fiscal_line_obj = FiscalYearLines(id=fiscal_line_values["id"])
            date_values = (parser([details["date"], details["cutoff_from"], details["cutoff_to"]])
                           .parse_date_from_string())

            releases_params = {
                "date": date_values[0],
                "cutoff_date_from": date_values[1],
                "cutoff_date_to": date_values[2],
                "payroll_cycle": details["payroll_cycle"],
                "is_reviewed": False,
                "fiscal_year": fiscal_end_obj,
                "fiscal_year_line": fiscal_line_obj,
                "produce_gross_deductions": details["produce_gross_deductions"],
                "produce_basic_deductions": details["produce_basic_deductions"],
                "company_id": details["company_id"],
            }
            result_release = Queries(Releases).execute_create(releases_params)

            if result_release[0]["status"]:
                for other_income in other_incomes:
                    other_income_params = {
                        "employee_id": other_income["employee_id"],
                        "releases_id": result_release[0]["id"],
                        "other_income_type_id": other_income["other_income_type_id"],
                        "amount": other_income["amount"]
                    }
                    Queries(OtherIncome).execute_create(other_income_params)

                for other_benefit in other_benefits:
                    other_benefits_params = {
                        "employee_id": other_benefit["employee_id"],
                        "releases_id": result_release[0]["id"],
                        "other_benefit_type_id": other_benefit["other_benefit_type_id"],
                        "untaxable_threshold": other_benefit["untaxable_threshold"],
                        "amount": other_benefit["amount"]
                    }
                    Queries(OtherBenefits).execute_create(other_benefits_params)

                for earning_adjustment in earning_adjustments:
                    earning_adjustment_params = {
                        "employee_id": earning_adjustment["employee_id"],
                        "releases_id": result_release[0]["id"],
                        "adjustment_remarks": earning_adjustment["adjustment_remarks"],
                        "amount": earning_adjustment["amount"]
                    }
                    Queries(EarningAdjustments).execute_create(earning_adjustment_params)

            return str(result_release[0]["message"])
        except KeyError as key_err:
            print("key err: " + str(key_err))
            return {"Key Error": str(key_err)}
        except Exception as e:
            e_type, e_object, e_traceback = sys.exc_info()
            e_filename = os.path.split(
                e_traceback.tb_frame.f_code.co_filename
            )[1]
            e_message = str(e)
            e_line_number = e_traceback.tb_lineno
            return {"Ex Error": {
                "type": str(e_type),
                "filename": str(e_filename),
                "line": str(e_line_number),
                "message": str(e_message)
            }}

    @staticmethod
    def create_auto(data):
        try:
            details = data
            parser = ParseValues
            fiscal_end_obj = FiscalYear(id=data["fiscal_year_id"])
            fiscal_line_obj = FiscalYearLines(id=data["fiscal_month_id"])
            date_values = (parser([details["date"], details["cutoff_from"], details["cutoff_to"]])
                           .parse_date_from_string())

            releases_params = {
                "date": date_values[0],
                "cutoff_date_from": date_values[1],
                "cutoff_date_to": date_values[2],
                "payroll_cycle": details["payroll_cycle"],
                "is_reviewed": False,
                "fiscal_year": fiscal_end_obj,
                "fiscal_year_line": fiscal_line_obj,
                "produce_gross_deductions": True,
                "produce_basic_deductions": True,
                "company_id": details["company_id"],
            }
            result_release = Queries(Releases).execute_create(releases_params)
            return result_release
        except KeyError as key_err:
            print("key err: " + str(key_err))
            return {"status": False, "message": str(key_err)}
        except Exception as e:
            e_type, e_object, e_traceback = sys.exc_info()
            e_filename = os.path.split(
                e_traceback.tb_frame.f_code.co_filename
            )[1]
            e_message = str(e)
            e_line_number = e_traceback.tb_lineno
            return {
                "status": False,
                "message": {
                    "type": str(e_type),
                    "filename": str(e_filename),
                    "line": str(e_line_number),
                    "message": str(e_message)
                }
            }

    @staticmethod
    def toggle_is_generated(sid):
        try:
            payload = {
                "is_generated": True
            }

            Queries(Releases).execute_change(payload, sid)

        except KeyError as key_err:
            return {"Key Error": str(key_err)}
        except Exception as e:
            e_type, e_object, e_traceback = sys.exc_info()
            e_filename = os.path.split(
                e_traceback.tb_frame.f_code.co_filename
            )[1]
            e_message = str(e)
            e_line_number = e_traceback.tb_lineno
            return {"Ex Error": {
                "type": str(e_type),
                "filename": str(e_filename),
                "line": str(e_line_number),
                "message": str(e_message)
            }}

    def create_employee_line_data(self):
        values = self.request
        employee_query = self._construct_employee_queries(
            values["employee_totals"], values["release_id"]
        )
        employee_totals_ids = execute_raw_query(employee_query)
        self._construct_and_execute_other_queries(
            employee_totals_ids,
            values
        )

    def create_totals(self):
        try:
            data = self.request["figures"]
            release_id = self.request["release_id"]
            employee_total_query = statements.insert_payroll_totals

            values = """(
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s
            )""" % (
                release_id,

                round(data['undertime_gross'], 2),
                round(data['tardiness_gross'], 2),
                round(data['absent_gross'], 2),
                round(data['paid_leave_gross'], 2),
                round(data['unpaid_leave_gross'], 2),

                round(data['other_income'], 2),
                round(data['other_benefits'], 2),
                round(data['earnings_adjustment'], 2),
                round(data['other_deductions'], 2),

                round(data['ordinary_gross'], 2),
                round(data['ordinary_holiday_gross'], 2),
                round(data['ordinary_overtime_gross'], 2),
                round(data['night_diff_gross'], 2),
                round(data['night_diff_ot_gross'], 2),

                round(data['rest_day_gross'], 2),
                round(data['rest_day_overtime_gross'], 2),
                round(data['rest_day_night_diff_gross'], 2),
                round(data['rest_day_night_diff_ot_gross'], 2),

                round(data['regular_holiday'], 2),
                round(data['special_holiday'], 2),
                round(data['double_regular_holiday'], 2),
                round(data['double_special_holiday'], 2),

                round(data['night_regular_holiday'], 2),
                round(data['night_special_holiday'], 2),
                round(data['night_double_regular_holiday'], 2),
                round(data['night_double_special_holiday'], 2),

                round(data['ot_regular_holiday'], 2),
                round(data['ot_special_holiday'], 2),
                round(data['ot_double_regular_holiday'], 2),
                round(data['ot_double_special_holiday'], 2),

                round(data['ot_night_regular_holiday'], 2),
                round(data['ot_night_special_holiday'], 2),
                round(data['ot_night_double_regular_holiday'], 2),
                round(data['ot_night_double_special_holiday'], 2),

                round(data['rest_day_regular_holiday'], 2),
                round(data['rest_day_special_holiday'], 2),
                round(data['rest_day_double_regular_holiday'], 2),
                round(data['rest_day_double_special_holiday'], 2),

                round(data['rest_day_night_regular_holiday'], 2),
                round(data['rest_day_night_special_holiday'], 2),
                round(data['rest_day_night_double_regular_holiday'], 2),
                round(data['rest_day_night_double_special_holiday'], 2),

                round(data['rest_day_ot_regular_holiday'], 2),
                round(data['rest_day_ot_special_holiday'], 2),
                round(data['rest_day_ot_double_regular_holiday'], 2),
                round(data['rest_day_ot_double_special_holiday'], 2),

                round(data['rest_day_ot_night_regular_holiday'], 2),
                round(data['rest_day_ot_night_special_holiday'], 2),
                round(data['rest_day_ot_night_double_regular_holiday'], 2),
                round(data['rest_day_ot_night_double_special_holiday'], 2),

                round(data['basic_gross'], 2),
                round(data['earnings_total'], 2),
                round(data['deducted_gross'], 2),
                round(data['deductions_total'], 2),
                round(data['allowance_gross'], 2),
                round(data['taxable_allowance'], 2),
                round(data['deducted_employee_gross'], 2),
                round(data['deducted_employer_gross'], 2),
                round(data['salary_gross'], 2),
                round(data['taxes_total'], 2),
                round(data['net_total'], 2)
            )
            return execute_raw_query_insert(employee_total_query.format(values))
        except KeyError as key_err:
            print(str(key_err))
            return {"Key Error": str(key_err)}
        except Exception as e:
            e_type, e_object, e_traceback = sys.exc_info()
            e_filename = os.path.split(
                e_traceback.tb_frame.f_code.co_filename
            )[1]
            e_message = str(e)
            e_line_number = e_traceback.tb_lineno
            print(str(e_message))
            return {"Ex Error": {
                "type": str(e_type),
                "filename": str(e_filename),
                "line": str(e_line_number),
                "message": str(e_message)
            }}

    @staticmethod
    def _construct_and_execute_other_queries(ids, data):
        try:
            attendances_insert_query = statements.insert_payroll_attendances
            allowances_insert_query = statements.insert_payroll_allowance
            deductions_insert_query = statements.insert_payroll_deductions
            other_deductions_insert_query = statements.insert_payroll_other_deductions
            attendances_values = ""
            allowances_values = ""
            deductions_values = ""
            other_deductions_values = ""

            for val in ids:
                if len(data["attendances"]) > 0:
                    for attendance in data["attendances"]:
                        if val["employee_id"] == attendance["employee_id"]:
                            attendance_id = attendance["attendance_id"]
                            if attendance_id == -1 or attendance_id == 0:
                                attendance_id = 'NULL'
                            attendances_values += """(
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                %s, %s
                            ),""" % (
                                val["id"],
                                attendance_id,

                                attendance["total_absent_hrs"],
                                attendance["undertime_hrs"],
                                attendance["tardiness_hrs"],
                                attendance["total_paid_leave_hrs"],
                                attendance["total_unpaid_leave_hrs"],

                                attendance["total_ordinary_hrs"],
                                attendance["total_ordinary_ot_hrs"],
                                attendance["total_night_diff_hrs"],
                                attendance["total_ordinary_ot_night_diff_hrs"],

                                attendance["total_rest_day_hrs"],
                                attendance["total_rest_day_ot_hrs"],
                                attendance["total_rest_day_night_diff_hrs"],
                                attendance["total_rest_day_ot_night_diff_hrs"],

                                attendance["total_regular_holiday_hrs"],
                                attendance["total_double_regular_holiday_hrs"],
                                attendance["total_special_holiday_hrs"],
                                attendance["total_double_special_holiday_hrs"],

                                attendance["total_night_regular_holiday_hrs"],
                                attendance["total_night_double_regular_holiday_hrs"],
                                attendance["total_night_special_holiday_hrs"],
                                attendance["total_night_double_special_holiday_hrs"],

                                attendance["total_ot_regular_holiday_hrs"],
                                attendance["total_ot_double_regular_holiday_hrs"],
                                attendance["total_ot_special_holiday_hrs"],
                                attendance["total_ot_double_special_holiday_hrs"],

                                attendance["total_night_ot_regular_holiday_hrs"],
                                attendance["total_night_ot_double_regular_holiday_hrs"],
                                attendance["total_night_ot_special_holiday_hrs"],
                                attendance["total_night_ot_double_special_holiday_hrs"],

                                attendance["rest_day_total_regular_holiday_hrs"],
                                attendance["rest_day_total_double_regular_holiday_hrs"],
                                attendance["rest_day_total_special_holiday_hrs"],
                                attendance["rest_day_total_double_special_holiday_hrs"],

                                attendance["rest_day_total_night_regular_holiday_hrs"],
                                attendance["rest_day_total_night_double_regular_holiday_hrs"],
                                attendance["rest_day_total_night_special_holiday_hrs"],
                                attendance["rest_day_total_night_double_special_holiday_hrs"],

                                attendance["rest_day_total_ot_regular_holiday_hrs"],
                                attendance["rest_day_total_ot_double_regular_holiday_hrs"],
                                attendance["rest_day_total_ot_special_holiday_hrs"],
                                attendance["rest_day_total_ot_double_special_holiday_hrs"],

                                attendance["rest_day_total_night_ot_regular_holiday_hrs"],
                                attendance["rest_day_total_night_ot_double_regular_holiday_hrs"],
                                attendance["rest_day_total_night_ot_special_holiday_hrs"],
                                attendance["rest_day_total_night_ot_double_special_holiday_hrs"],

                                attendance["tardiness"],
                                attendance["undertime"],
                                attendance["absent"],
                                attendance["paid_leave"],
                                attendance["unpaid_leave"],

                                attendance["ordinary"],
                                attendance["ordinary_ot"],
                                attendance["night_diff"],
                                attendance["night_diff_ot"],

                                attendance["rest_day"],
                                attendance["rest_day_ot"],
                                attendance["rest_day_night_diff"],
                                attendance["rest_day_night_diff_ot"],

                                attendance["regular_holiday"],
                                attendance["double_regular_holiday"],
                                attendance["special_holiday"],
                                attendance["double_special_holiday"],

                                attendance["ot_regular_holiday"],
                                attendance["ot_double_regular_holiday"],
                                attendance["ot_special_holiday"],
                                attendance["ot_double_special_holiday"],

                                attendance["night_regular_holiday"],
                                attendance["night_double_regular_holiday"],
                                attendance["night_special_holiday"],
                                attendance["night_double_special_holiday"],

                                attendance["ot_night_regular_holiday"],
                                attendance["ot_night_double_regular_holiday"],
                                attendance["ot_night_special_holiday"],
                                attendance["ot_night_double_special_holiday"],

                                attendance["rest_day_regular_holiday"],
                                attendance["rest_day_double_regular_holiday"],
                                attendance["rest_day_special_holiday"],
                                attendance["rest_day_double_special_holiday"],

                                attendance["rest_day_ot_regular_holiday"],
                                attendance["rest_day_ot_double_regular_holiday"],
                                attendance["rest_day_ot_special_holiday"],
                                attendance["rest_day_ot_double_special_holiday"],

                                attendance["rest_day_night_regular_holiday"],
                                attendance["rest_day_night_double_regular_holiday"],
                                attendance["rest_day_night_special_holiday"],
                                attendance["rest_day_night_double_special_holiday"],

                                attendance["rest_day_ot_night_regular_holiday"],
                                attendance["rest_day_ot_night_double_regular_holiday"],
                                attendance["rest_day_ot_night_special_holiday"],
                                attendance["rest_day_ot_night_double_special_holiday"]
                            )

                if len(data["allowances"]) > 0:
                    for allowance in data["allowances"]:
                        if val["employee_id"] == allowance["employee_id"]:
                            allowances_values += """(
                                    %s, %s, %s
                                ),""" % (
                                allowance["amount"],
                                allowance["id"],
                                val["id"]
                            )

                if len(data["deductions"]) > 0:
                    for deduction in data["deductions"]:
                        if val["employee_id"] == deduction["employee_id"]:
                            deductions_values += """(
                                %s, %s, %s, %s, %s
                            ),""" % (
                                deduction["deduction_id"],
                                val["id"],
                                deduction["employer_share"],
                                deduction["employee_share"],
                                False
                            )
                if len(data["other_deductions"]) > 0:
                    for other_deduction in data["other_deductions"]:
                        if val["employee_id"] == other_deduction["employee_id"]:
                            other_deductions_values += """(
                                %s, %s, %s
                            ),""" % (
                                other_deduction["id"],
                                val["id"],
                                other_deduction["amount_per_month"],
                            )
            if attendances_values != "":
                execute_raw_query_insert(attendances_insert_query.format(attendances_values[:-1]))
            if allowances_values != "":
                execute_raw_query_insert(allowances_insert_query.format(allowances_values[:-1]))
            if deductions_values != "":
                execute_raw_query_insert(deductions_insert_query.format(deductions_values[:-1]))
            if other_deductions_values != "":
                execute_raw_query_insert(other_deductions_insert_query.format(other_deductions_values[:-1]))
        except Exception as e:
            e_type, e_object, e_traceback = sys.exc_info()
            e_filename = os.path.split(
                e_traceback.tb_frame.f_code.co_filename
            )[1]
            e_message = str(e)
            e_line_number = e_traceback.tb_lineno
            print(e_message, e_line_number)
            return {"Ex Error": {
                "type": str(e_type),
                "filename": str(e_filename),
                "line": str(e_line_number),
                "message": str(e_message)
            }}

    @staticmethod
    def _construct_employee_queries(employee, release_id):
        try:
            employee_total_query = statements.insert_payroll_employee
            values = ""
            iterate = 1
            for data in employee:
                values += """(
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s
                    )""" % (
                    data["employee_id"],
                    release_id,

                    data["hourly_rate"],
                    data["daily_rate"],
                    data["monthly_rate"],

                    data["undertime_hrs"],
                    data["tardiness_hrs"],
                    data["absent_hrs"],
                    data["paid_leave_hrs"],
                    data["unpaid_leave_hrs"],

                    data["ordinary_hrs"],
                    data["ordinary_holiday_hrs"],
                    data["ordinary_overtime_hrs"],
                    data["night_diff_hrs"],
                    data["night_diff_ot_hrs"],

                    data["rest_day_hrs"],
                    data["rest_day_overtime_hrs"],
                    data["rest_day_night_diff_hrs"],
                    data["rest_day_night_diff_ot_hrs"],

                    data["regular_holiday_hrs"],
                    data["special_holiday_hrs"],
                    data["double_regular_holiday_hrs"],
                    data["double_special_holiday_hrs"],

                    data["night_regular_holiday_hrs"],
                    data["night_special_holiday_hrs"],
                    data["night_double_regular_holiday_hrs"],
                    data["night_double_special_holiday_hrs"],

                    data["ot_regular_holiday_hrs"],
                    data["ot_special_holiday_hrs"],
                    data["ot_double_regular_holiday_hrs"],
                    data["ot_double_special_holiday_hrs"],

                    data["ot_night_regular_holiday_hrs"],
                    data["ot_night_special_holiday_hrs"],
                    data["ot_night_double_regular_holiday_hrs"],
                    data["ot_night_double_special_holiday_hrs"],

                    data["rest_day_regular_holiday_hrs"],
                    data["rest_day_special_holiday_hrs"],
                    data["rest_day_double_regular_holiday_hrs"],
                    data["rest_day_double_special_holiday_hrs"],

                    data["rest_day_night_regular_holiday_hrs"],
                    data["rest_day_night_special_holiday_hrs"],
                    data["rest_day_night_double_regular_holiday_hrs"],
                    data["rest_day_night_double_special_holiday_hrs"],

                    data["rest_day_ot_regular_holiday_hrs"],
                    data["rest_day_ot_special_holiday_hrs"],
                    data["rest_day_ot_double_regular_holiday_hrs"],
                    data["rest_day_ot_double_special_holiday_hrs"],

                    data["rest_day_ot_night_regular_holiday_hrs"],
                    data["rest_day_ot_night_special_holiday_hrs"],
                    data["rest_day_ot_night_double_regular_holiday_hrs"],
                    data["rest_day_ot_night_double_special_holiday_hrs"],

                    data["undertime_gross"],
                    data["tardiness_gross"],
                    data["absent_gross"],
                    data["paid_leave"],
                    data["unpaid_leave"],

                    data["other_income"],
                    data["other_benefits"],
                    data["earnings_adjustment"],
                    data["other_deductions"],

                    data["ordinary_gross"],
                    data["ordinary_holiday_gross"],
                    data["ordinary_overtime_gross"],
                    data["night_diff_gross"],
                    data["night_diff_ot_gross"],

                    data["rest_day_gross"],
                    data["rest_day_overtime_gross"],
                    data["rest_day_night_diff_gross"],
                    data["rest_day_night_diff_ot_gross"],

                    data["regular_holiday"],
                    data["special_holiday"],
                    data["double_regular_holiday"],
                    data["double_special_holiday"],

                    data["night_regular_holiday"],
                    data["night_special_holiday"],
                    data["night_double_regular_holiday"],
                    data["night_double_special_holiday"],

                    data["ot_regular_holiday"],
                    data["ot_special_holiday"],
                    data["ot_double_regular_holiday"],
                    data["ot_double_special_holiday"],

                    data["ot_night_regular_holiday"],
                    data["ot_night_special_holiday"],
                    data["ot_night_double_regular_holiday"],
                    data["ot_night_double_special_holiday"],

                    data["rest_day_regular_holiday"],
                    data["rest_day_special_holiday"],
                    data["rest_day_double_regular_holiday"],
                    data["rest_day_double_special_holiday"],

                    data["rest_day_night_regular_holiday"],
                    data["rest_day_night_special_holiday"],
                    data["rest_day_night_double_regular_holiday"],
                    data["rest_day_night_double_special_holiday"],

                    data["rest_day_ot_regular_holiday"],
                    data["rest_day_ot_special_holiday"],
                    data["rest_day_ot_double_regular_holiday"],
                    data["rest_day_ot_double_special_holiday"],

                    data["rest_day_ot_night_regular_holiday"],
                    data["rest_day_ot_night_special_holiday"],
                    data["rest_day_ot_night_double_regular_holiday"],
                    data["rest_day_ot_night_double_special_holiday"],

                    data["basic_gross"],
                    data["earnings_total"],
                    data["deducted_gross"],
                    data["deductions_total"],

                    data["allowance_gross"],
                    data["taxable_allowance"],

                    data["deducted_employee_gross"],
                    data["deducted_employer_gross"],

                    data["salary_gross"],
                    data["taxes_total"],
                    data["net_total"]
                )
                if len(employee) != iterate:
                    values += ", "
                iterate += 1
            return employee_total_query.format(values)
        except Exception as e:
            e_type, e_object, e_traceback = sys.exc_info()
            e_filename = os.path.split(
                e_traceback.tb_frame.f_code.co_filename
            )[1]
            e_message = str(e)
            e_line_number = e_traceback.tb_lineno
            print("TOTAL QUERY: ", e_message, e_line_number)
            return {"Ex Error": {
                "type": str(e_type),
                "filename": str(e_filename),
                "line": str(e_line_number),
                "message": str(e_message)
            }}

    def reset_payout_records(self):
        try:
            body = json.loads(self.request.body)
            details = body["data"]
            query = statements.select_payroll_releases_employee_ids
            raw_releases_employee_ids = execute_raw_query(query.format(details["id"]))
            releases_employee_ids = construct_ids_tuple(raw_releases_employee_ids)[0]

            if len(releases_employee_ids) > 0:
                query_set = """
                            DELETE FROM payroll_releasesemployeetotals WHERE releases_id = {0};
                            DELETE FROM payroll_releasestotals WHERE releases_id = {0};
                            DELETE FROM payroll_releasesaccumulatedallowance WHERE releases_employee_id IN {1};
                            DELETE FROM payroll_releasesaccumulatedattendances WHERE releases_employee_id IN {1};
                            DELETE FROM payroll_releasesaccumulateddeductions WHERE releases_employee_id IN {1};
                            DELETE FROM payroll_releasesaccumulatedotherdeductions WHERE releases_employee_id IN {1};
                        """.format(details["id"], releases_employee_ids)
                execute_raw_query_operations(query_set)
                return True
        except Exception:
            return False
