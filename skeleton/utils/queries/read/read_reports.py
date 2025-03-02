import datetime
from django.db import connection
from django.utils import timezone
from payroll.utils.general.general import (fetchall_dictionary, execute_raw_query, ParseValues, build_conditions)
from payroll.utils.queries.statements import select_reports as statement
from payroll.utils.general.reports import payroll_accumulated as methods
from payroll.utils.general.reports.annualized_wtax import AnnualizedWTaxReportMethods
from payroll.utils.general.reports.r13th_month import R13thMonthMethods
from payroll.utils.general.reports.employee_2316 import Employee2316Methods
from payroll.utils.general.reports.employee_alphalist import EmployeeAlphalistReport
from payroll.utils.general import response_payload_report as builder
from payroll.utils.general.reports.report_general_methods import GeneralMethods as General


class ReadPayrollReports:
    def __init__(self, requests):
        self.requests = requests

    def execute(self):
        payroll_methods = methods.PayrollReportMethods(self.requests)
        people_conditions = General(self.requests).build_people_conditions()
        query = statement.select_payroll_report.format(people_conditions)

        with connection.cursor() as cursor:
            cursor.execute(str(query))

            results = fetchall_dictionary(cursor)
        built_raw_result = builder.BuildPayrollReport(results).build_query_response()
        built_chart_payload = payroll_methods.build_payroll_report_payload(built_raw_result)
        # print(built_chart_payload)
        return {"values": built_chart_payload}


class ReadAttendanceReports:
    def __init__(self, requests):
        self.requests = requests

    def execute(self):
        payroll_methods = methods.PayrollReportMethods(self.requests)
        people_conditions = General(self.requests).build_people_conditions()
        query = statement.select_payroll_report.format(people_conditions)

        with connection.cursor() as cursor:
            cursor.execute(str(query))

            results = fetchall_dictionary(cursor)
        built_raw_result = builder.BuildPayrollReport(results).build_query_response()
        built_chart_payload = payroll_methods.build_attendance_report_payload(built_raw_result)
        # print(built_chart_payload)
        return {"values": built_chart_payload}


class ReadAnnualizedWTaxReports:
    def __init__(self, requests):
        self.requests = requests

    def execute(self):
        fiscal_year_id = self.requests.GET.get("fiscal_year")
        values = AnnualizedWTaxReportMethods(self.requests).execute()
        return {"values": values}


class ReadForecasted13thMonthReports:
    def __init__(self, requests):
        self.requests = requests

    def execute(self):
        values = R13thMonthMethods(self.requests).execute()
        return {"values": values}


class ReadEmployee2316Reports:
    def __init__(self, requests):
        self.requests = requests

    def execute(self):
        values = Employee2316Methods(self.requests).execute()
        return {"values": values}


class ReadEmployeeAlphalistReports:
    def __init__(self, requests):
        self.requests = requests

    def execute(self):
        values = EmployeeAlphalistReport(self.requests).execute()
        return {"values": values}


class ReadDashboardCardsReports:
    def __init__(self, requests):
        self.requests = requests

    def execute(self):
        company_id = self.requests.COOKIES["company_id"]
        current_date_obj = timezone.now()
        past_30_days = ParseValues(current_date_obj - datetime.timedelta(days=30)).parse_date_to_string_ymd()
        past_5_days = ParseValues(current_date_obj - datetime.timedelta(days=5)).parse_date_to_string_ymd()
        current_date = ParseValues(current_date_obj).parse_date_to_string_ymd()
        total_employees_query = statement.total_employees.format(company_id)
        new_employees_query = statement.new_employees.format(company_id, past_5_days)
        monthly_on_leave_query = statement.monthly_on_leave.format(company_id, past_30_days)
        daily_on_leave_query = statement.daily_on_leave.format(company_id, current_date)
        daily_attendance_query = statement.daily_attendance.format(company_id, current_date)

        final = {
            "total_employees": execute_raw_query(total_employees_query)[0]["count"],
            "new_employees": execute_raw_query(new_employees_query)[0]["count"],
            "monthly_on_leave": execute_raw_query(monthly_on_leave_query)[0]["count"],
            "daily_on_leave": execute_raw_query(daily_on_leave_query)[0]["count"],
            "daily_attendance": execute_raw_query(daily_attendance_query)[0]["count"],
        }

        return final


class ReadDashboardMyRequestsReports:
    def __init__(self, requests):
        self.requests = requests

    def execute(self):
        filters = self.requests.GET.get("filters")
        current_date_obj = timezone.now()
        past_30_days = ParseValues(current_date_obj - datetime.timedelta(days=60)).parse_date_to_string_ymd()

        attendance_corrections_query = statement.attendance_correction_status_counts.format(
            build_conditions(filters), past_30_days
        )
        overtime_requests_query = statement.overtime_requests_status_counts.format(
            build_conditions(filters), past_30_days
        )
        leave_applications_query = statement.leave_application_requests_status_counts.format(
            build_conditions(filters), past_30_days
        )

        attendance_corrections_raw = execute_raw_query(attendance_corrections_query)
        overtime_requests_raw = execute_raw_query(overtime_requests_query)
        leave_applications_raw = execute_raw_query(leave_applications_query)

        attendance_corrections = {"pending": 0, "approved": 0, "declined": 0, "total": 0}
        overtime_requests = {"pending": 0, "approved": 0, "declined": 0, "total": 0}
        leave_applications = {"pending": 0, "approved": 0, "declined": 0, "total": 0}

        for value in attendance_corrections_raw:
            attendance_corrections["pending"] += value["pending"]
            attendance_corrections["approved"] += value["approved"]
            attendance_corrections["declined"] += value["declined"]
        for value in overtime_requests_raw:
            overtime_requests["pending"] += value["pending"]
            overtime_requests["approved"] += value["approved"]
            overtime_requests["declined"] += value["declined"]
        for value in leave_applications_raw:
            leave_applications["pending"] += value["pending"]
            leave_applications["approved"] += value["approved"]
            leave_applications["declined"] += value["declined"]
        attendance_corrections["total"] = sum([
            attendance_corrections["pending"], attendance_corrections["approved"], attendance_corrections["declined"]
        ])
        overtime_requests["total"] = sum([
            overtime_requests["pending"], overtime_requests["approved"], overtime_requests["declined"]
        ])
        leave_applications["total"] = sum([
            leave_applications["pending"], leave_applications["approved"], leave_applications["declined"]
        ])

        return {
            "attendance_corrections": attendance_corrections,
            "overtime_requests": overtime_requests,
            "leave_applications": leave_applications
        }


class ReadFiscalYearEmployeeCountReports:
    def __init__(self, requests):
        self.requests = requests

    def execute(self):
        final = []
        fiscal_year = self.requests.GET.get("fiscal_year")
        company_id = self.requests.COOKIES["company_id"]
        departments_query = statement.fetch_all_departments.format(company_id)
        employee_query = statement.fetch_employees_count.format(company_id, fiscal_year)
        departments_raw = execute_raw_query(departments_query)
        employees_raw = execute_raw_query(employee_query)
        departments = General.get_unique(departments_raw, "name")
        departments.append("Undefined")

        for department in departments:
            temp = {"name": department, "count": 0}
            for employee in employees_raw:
                if employee["name"] == department:
                    temp["count"] = employee["count"]
                    break
                if department == "Undefined" and employee["name"] is None:
                    temp["count"] = employee["count"]
                    break
            final.append(temp)
        return {
            "data": final,
            "skeleton": departments
        }


class ReadDashboardFiscalEmployeeSalariesReports:
    def __init__(self, requests):
        self.requests = requests

    def execute(self):
        final = []
        fiscal_year = self.requests.GET.get("fiscal_year")
        company_id = self.requests.COOKIES["company_id"]
        department_salaries_query = statement.fetch_department_salaries.format(company_id, fiscal_year)
        department_salaries_raw = execute_raw_query(department_salaries_query)
        for department in department_salaries_raw:
            temp = {"name": department["name"], "net_total": round(department["net_total"], 2)}
            if department["name"] is None:
                temp["name"] = "Undefined"
            final.append(temp)
        return final


class ReadDashboardFiveAttendancesReports:
    def __init__(self, requests):
        self.requests = requests

    def execute(self):
        final = []
        sid = self.requests.GET.get("sid")
        employee_attendances_query = statement.fetch_employee_five_attendances.format(sid)
        employee_attendances_raw = execute_raw_query(employee_attendances_query)
        for attendances in employee_attendances_raw:
            final.append({
                "time_in": ParseValues([attendances["time_in"]]).parse_datetime_to_string()[0],
                "time_out": ParseValues([attendances["time_out"]]).parse_datetime_to_string()[0]
            })
        return final
