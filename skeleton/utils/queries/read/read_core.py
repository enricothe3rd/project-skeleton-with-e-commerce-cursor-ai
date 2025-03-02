import django.utils.timezone
from django.db import connection
import requests
from django.conf import settings
from payroll.utils.general.general import (execute_raw_query, fetchall_dictionary, ConstructSelectQuery,
                                           build_conditions, calculate_offset, generate_condition_level_based,
                                           get_field_value_from_raw_values, GenerateConditionLevelBased)
from payroll.utils.general.response_payload_core import (BuildEmployeeResponse, BuildAttendancesResponse,
                                                         BuildLeaveApplicationResponse, BuildLeaveCreditsResponse,
                                                         BuildPayrollReleaseDataResponse, BuildBadgeNo,
                                                         BuildOtherDeductions, BuildTaxPayments)
from payroll.utils.queries.statements import select as statements
from payroll.utils.queries.statements import select_payroll_generate as payroll_statements
from payroll.models.core import Employee


class EmployeeOnboardingResponse:
    def __init__(self, employee):
        self.employee = employee

    def build_parameter(self, request):
        self.employee = request.GET.get('id')

        return self.execute()

    def execute(self):
        raw_data = self.fetch_data(self.employee)
        response = BuildEmployeeResponse(raw_data).execute()

        return response

    @staticmethod
    def fetch_data(employee_id):
        try:
            results = {}

            queries = {
                'details':
                    statements.employee_onboarding_details,
                'contract':
                    statements.employee_contract,
                'banks':
                    statements.employee_bank_details,
                'positions':
                    statements.employee_positions_details,
                'addresses':
                    statements.employee_addresses,
                'leaves':
                    statements.employee_leave_details,
                'allowances':
                    statements.employee_allowance_details,
                'deductions':
                    statements.employee_deduction_rel,
                'schedules_headers':
                    statements.employee_schedule_details_headers,
                'schedules_lines':
                    statements.employee_schedule_details_lines,
                'previous_employer':
                    statements.employee_previous_employment,
                # 'deductions_headers':
                #     statements.employee_deductions_details_headers,
                # 'deductions_lines':
                #     statements.employee_deductions_details_lines,
            }

            with connection.cursor() as cursor:
                for key in queries.keys():
                    cursor.execute(str(queries[key]).format(str(employee_id)))

                    results[key] = fetchall_dictionary(cursor)
            # print(results)
            return results
        except KeyError as key_err:
            return {'status': False, 'message': "KEY ERROR: " + str(key_err)}
        except Exception as ex:
            return {'status': False, 'message': "GENERAL EXCEPTION ERROR: " + str(ex)}


class ReadEmployees:
    def __init__(self, request):
        self.requests = request

    def read_list(self):
        conditions = self.requests.GET.get("filters")
        level = self.requests.GET.get("level")  # Change to cookies

        raw_query = ConstructSelectQuery(Employee, conditions, level).search()
        raw_values = execute_raw_query(raw_query)

        values = BuildEmployeeResponse(raw_values).build_employee_detail()

        return {"value": values}


class ReadAttendances:
    def __init__(self, request):
        self.requests = request

    def read_list(self):
        conditions = self.requests.GET.get("filters")
        level_condition = generate_condition_level_based(
            self.requests.COOKIES['level'], self.requests.COOKIES['eid']
        )
        raw_query = statements.attendances_get_list
        raw_values = execute_raw_query(
            raw_query.format(build_conditions(
                "%s%s" % (level_condition, conditions)
            ))
        )
        values = BuildAttendancesResponse(raw_values).build_attendances_detail()
        return {"value": values}

    def read_one(self):
        conditions = self.requests.GET.get("filters")
        raw_query = statements.attendances_get_query
        raw_values = execute_raw_query(
            raw_query.format(build_conditions(conditions))
        )
        values = BuildAttendancesResponse(raw_values).build_attendances_detail()

        return {"values": values}

    def read_approvals(self):
        conditions = self.requests.GET.get("filters")
        level_condition = GenerateConditionLevelBased(
            self.requests.COOKIES['level'], self.requests.COOKIES['eid']
        ).execute()
        raw_query = statements.attendances_get_list
        raw_values = execute_raw_query(
            raw_query.format(level_condition + build_conditions(conditions))
        )
        values = BuildAttendancesResponse(raw_values).build_attendances_detail()
        return {"value": values}


class ReadLeaves:
    def __init__(self, request):
        self.requests = request

    def read_list(self):
        conditions = self.requests.GET.get("filters")
        level_condition = generate_condition_level_based(
            self.requests.COOKIES['level'], self.requests.COOKIES['eid']
        )
        raw_query = statements.leaves_application_get
        raw_values = execute_raw_query(
            raw_query.format(build_conditions(
                "%s%s" % (level_condition, conditions)
            ))
        )

        values = BuildLeaveApplicationResponse(raw_values).execute()

        return {"value": values}

    def read_one(self):
        conditions = self.requests.GET.get("filters")

        raw_query = statements.leaves_application_get
        raw_values = execute_raw_query(
            raw_query.format(build_conditions(conditions))
        )

        values = BuildLeaveApplicationResponse(raw_values).execute()

        return {"values": values}

    def read_approvals(self):
        conditions = self.requests.GET.get("filters")
        level_condition = GenerateConditionLevelBased(
            self.requests.COOKIES['level'], self.requests.COOKIES['eid']
        ).execute()
        raw_query = statements.leaves_application_get
        raw_values = execute_raw_query(
            raw_query.format(level_condition + build_conditions(conditions))
        )
        values = BuildLeaveApplicationResponse(raw_values).execute()
        return {"value": values}


class ReadLeaveCredits:
    def __init__(self, request):
        self.requests = request

    def read_one(self):
        conditions = self.requests.GET.get("filters")

        raw_query = statements.leave_credit_get
        raw_values = execute_raw_query(
            raw_query.format(build_conditions(conditions))
        )

        values = BuildLeaveCreditsResponse(raw_values).execute()

        return {"values": values}


class ReadPayrollReleases:
    def __init__(self, request):
        self.requests = request

    def read_list(self):
        page = calculate_offset(self.requests.GET.get("page"), self.requests.GET.get("batch_size"))
        batch_size = self.requests.GET.get("batch_size")
        conditions = self.requests.GET.get("filters")
        # level = self.requests.GET.get("level")  # Change to cookies
        raw_query = payroll_statements.select_releases_list
        raw_values = execute_raw_query(
            raw_query.format(build_conditions(conditions), batch_size, page)
        )
        values = BuildPayrollReleaseDataResponse(raw_values).build_list()
        return {"value": values}

    def read_one(self):
        sid = self.requests.GET.get("id")
        # level = self.requests.GET.get("level")  # Change to cookies
        raw_query = payroll_statements.select_releases_one
        other_income_raw_query = payroll_statements.select_other_income
        other_benefits_raw_query = payroll_statements.select_other_benefits
        earnings_adjustments_raw_query = payroll_statements.select_earning_adjustments

        raw_values = execute_raw_query(
            raw_query.format(sid)
        )
        other_income_raw_values = execute_raw_query(
            other_income_raw_query.format(sid)
        )
        other_benefits_raw_values = execute_raw_query(
            other_benefits_raw_query.format(sid)
        )
        earnings_adjustments_raw_values = execute_raw_query(
            earnings_adjustments_raw_query.format(sid)
        )

        values = BuildPayrollReleaseDataResponse(raw_values[0]).build_one()

        final = {
            "details": values,
            "other_income": other_income_raw_values,
            "other_benefits": other_benefits_raw_values,
            "earnings_adjustment": earnings_adjustments_raw_values
        }
        print(final)
        return {"value": final}

    def read_employee_list(self):
        page = calculate_offset(self.requests.GET.get("page"), self.requests.GET.get("batch_size"))
        batch_size = self.requests.GET.get("batch_size")
        conditions = self.requests.GET.get("filters")
        raw_query = payroll_statements.select_payroll_employee_list
        raw_values = execute_raw_query(
            raw_query.format(build_conditions(conditions), batch_size, page)
        )
        values = BuildPayrollReleaseDataResponse(raw_values).employee_build_list()
        return {"value": values}

    def read_employee_one(self):
        sid = self.requests.GET.get("id")
        header_query = payroll_statements.select_payroll_employee_one
        attendances_query = payroll_statements.select_payroll_employee_attendances_one
        allowances_query = payroll_statements.select_payroll_employee_allowances_one
        deductions_query = payroll_statements.select_payroll_employee_deductions_one
        header_raw_values = execute_raw_query(
            header_query.format(sid)
        )
        attendances_raw_values = execute_raw_query(
            attendances_query.format(sid)
        )
        allowances_raw_values = execute_raw_query(
            allowances_query.format(sid)
        )
        deductions_raw_values = execute_raw_query(
            deductions_query.format(sid)
        )
        header_processed_values = BuildPayrollReleaseDataResponse(header_raw_values[0]).employee_build_one()
        attendance_processed_values = BuildPayrollReleaseDataResponse(attendances_raw_values).employee_attendance_one()
        return {
            "value": {
                "header": header_processed_values,
                "attendances": attendance_processed_values,
                "allowances": allowances_raw_values,
                "deductions": deductions_raw_values
            }
        }

    def read_employee_list_details(self):
        sid = self.requests.GET.get("id")
        ids_str = ""
        values = []
        employee_release_list_query = payroll_statements.select_payroll_employee_details_list
        allowances_query = payroll_statements.select_payroll_employee_allowances_list_for_pdf
        deductions_query = payroll_statements.select_payroll_employee_deductions_list_for_pdf
        employee_release_list_raw = execute_raw_query(
            employee_release_list_query.format(sid)
        )
        for employee_release in employee_release_list_raw:
            if employee_release["id"] == employee_release_list_raw[-1]["id"]:
                ids_str += "%s" % employee_release["id"]
            else:
                ids_str += "%s, " % employee_release["id"]
        allowances_raw = execute_raw_query(
            allowances_query.format(ids_str)
        )
        deductions_raw = execute_raw_query(
            deductions_query.format(ids_str)
        )

        employee_releases_processed = BuildPayrollReleaseDataResponse(employee_release_list_raw).employee_build_list()

        for employee_release in employee_releases_processed:
            init_dict = {"employee_release": employee_release, "allowances": [], "deductions": []}
            for allowances in allowances_raw:
                if allowances["releases_employee_id"] == employee_release["id"]:
                    init_dict["allowances"].append(allowances)
            for deductions in deductions_raw:
                if deductions["releases_employee_id"] == employee_release["id"]:
                    init_dict["deductions"].append(deductions)
            values.append(init_dict)
        print(values)
        return {"value": values}

    def read_own(self):
        page = calculate_offset(self.requests.GET.get("page"), self.requests.GET.get("batch_size"))
        batch_size = self.requests.GET.get("batch_size")
        conditions = self.requests.GET.get("filters")
        raw_query = payroll_statements.select_own_payroll_list
        raw_values = execute_raw_query(
            raw_query.format(build_conditions(conditions), batch_size, page, self.requests.COOKIES['eid'])
        )
        values = BuildPayrollReleaseDataResponse(raw_values).build_list()
        return {"value": values}


class ReadAutoGenerateBadgeNo:
    def __init__(self, request):
        self.requests = request

    def read(self):
        company_id = self.requests.GET.get("company_id")
        year_raw = django.utils.timezone.now()
        raw_query = statements.get_employee_count

        raw_values = execute_raw_query(
            raw_query.format(company_id, year_raw.year)
        )

        values = BuildBadgeNo([year_raw.year, raw_values[0]["count"]]).badge_num()
        return {"value": values}


class ReadOldPassword:
    def __init__(self, request):
        self.requests = request

    def read(self):
        data = self.requests
        old_password = data.GET.get("old_password")
        uid = data.GET.get("uid")
        cookies = {
            'company_id': data.COOKIES['company_id'],
            'token': data.COOKIES['token'],
            'user_id': data.COOKIES['user_id'],
        }
        response = requests.get(
            settings.USER_SERVICE_URL + "/users/check-old-password?old_password=%s&uid=%s" % (old_password, uid),
            cookies=cookies,
            verify=False
        )
        response_dict = response.json()
        print(response_dict)
        return response_dict
        # return [old_password, uid]


class ReadOtherDeductionsPerEmployeeList:
    def __init__(self, request):
        self.requests = request

    def read(self):
        sid = self.requests.GET.get("sid")
        query = statements.get_other_deductions_per_employee
        raw_values = execute_raw_query(query.format(sid))
        return {"value": BuildOtherDeductions(raw_values).build_list()}


class ReadTaxPayments:
    def __init__(self, request):
        self.requests = request

    def read_list(self):
        filters = self.requests.GET.get("filters")
        query = statements.get_tax_payments
        raw_values = execute_raw_query(query.format(build_conditions(filters)))
        return BuildTaxPayments(raw_values).build()

    def read_one(self):
        sid = self.requests.GET.get("id")
        query = statements.get_tax_payments
        raw_values = execute_raw_query(query.format("A.id = %s" % sid))
        return BuildTaxPayments(raw_values).build()
