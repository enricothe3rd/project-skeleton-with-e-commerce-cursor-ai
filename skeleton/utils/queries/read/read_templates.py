from payroll.utils.general.general import (ProcessHeaderInfo, extract_queryset, ConstructSelectQuery, ExtractAndBuildFromRawSQL)
from payroll.utils.queries.read import mappings
from payroll.models.setup import (LeaveType, LeaveTemplate, LeaveTemplateLine, AllowanceCategory, AllowanceTemplate,
                                  AllowanceTemplateLine, DeductionTemplate, DeductionCategory, DeductionMatrixTemplate,
                                  ScheduleTemplate, ScheduleTemplateLine, EmployeeContractTemplate, WorkSetup)
from payroll.utils.queries.statements import select_types_categories as statements
from payroll.utils.general.general import ParseValues, build_conditions, execute_raw_query


class SkeletonRead:
    def __init__(self, requests):
        self.requests = requests

    def read_skeleton(self):
        key = self.requests.GET.get("key")
        return eval("mappings."+key)


class LeaveTypeRead:
    def __init__(self, requests):
        self.requests = requests

    def read_leave_type_list(self):
        conditions = self.requests.GET.get("filters")
        level = self.requests.GET.get("level")  # Change to cookies
        queries = statements.select_read_leave_type_list
        types = execute_raw_query(
            queries.format(build_conditions(conditions))
        )
        return {"value": types}

    def read_leave_type_one(self):
        level = "company"  # Change to cookies
        sid = self.requests.GET.get("id")
        queries = statements.select_read_leave_type_one
        types = execute_raw_query(
            queries.format(sid)
        )
        return {"value": types}

    def read_as_pre_requisites(self):
        conditions = "is_active,=,True,None"
        level = self.requests.GET.get("level")  # Change to cookies
        map_values = mappings.pre_requisite_response

        raw_query = ConstructSelectQuery(LeaveType, conditions, level).search()
        values = ExtractAndBuildFromRawSQL(map_values).execute_for_async_select(raw_query)

        return {"value": values}


class LeaveTemplateRead:
    def __init__(self, requests):
        self.requests = requests

    def read_list(self):
        conditions = self.requests.GET.get("filters")
        level = self.requests.GET.get("level")  # Change to cookies
        map_values = mappings.leave_template_list_view

        raw_query = ConstructSelectQuery(LeaveTemplate, conditions, level).search()
        values = ExtractAndBuildFromRawSQL(map_values).execute_string(raw_query)

        return {"value": values}

    def read_one(self):
        level = "company"  # Change to cookies
        sid = self.requests.GET.get("id")
        result = LeaveTemplate.objects.filter(id=sid).values()

        conditions = "leave_template_id_id,=,"+sid+",None"
        map_values = mappings.leave_template_line_view
        line_query = ConstructSelectQuery(LeaveTemplateLine, conditions, level).search()
        line_result = ExtractAndBuildFromRawSQL(map_values).execute_string(line_query)

        return {
            "header": extract_queryset(result)[0],
            "line": extract_queryset(line_result),
            "skeleton": mappings.leave_template_line_view,
        }

    def read_as_pre_requisites(self):
        filters = self.requests.GET.get("filters")
        conditions = filters + "is_active,=,True,None"
        level = self.requests.GET.get("level")  # Change to cookies
        map_values = mappings.pre_requisite_response

        raw_query = ConstructSelectQuery(LeaveTemplate, conditions, level).search()
        values = ExtractAndBuildFromRawSQL(map_values).execute_for_async_select(raw_query)

        return {"value": values}


class AllowanceCategoryRead:
    def __init__(self, requests):
        self.requests = requests

    def read_leave_type_list(self):
        conditions = self.requests.GET.get("filters")
        level = self.requests.GET.get("level")  # Change to cookies
        queries = statements.select_read_attendance_category_list
        values = execute_raw_query(
            queries.format(build_conditions(conditions))
        )
        return {"value": values}

    def read_one(self):
        level = "company"  # Change to cookies
        sid = self.requests.GET.get("id")
        queries = statements.select_read_leave_type_one
        types = execute_raw_query(
            queries.format(sid)
        )
        return {"value": types}

    def read_as_pre_requisites(self):
        conditions = "is_active,=,True,None"
        level = self.requests.GET.get("level")  # Change to cookies
        map_values = mappings.pre_requisite_response

        raw_query = ConstructSelectQuery(AllowanceCategory, conditions, level).search()
        values = ExtractAndBuildFromRawSQL(map_values).execute_for_async_select(raw_query)

        return {"value": values}


class AllowanceTemplateRead:
    def __init__(self, requests):
        self.requests = requests

    def read_leave_type_list(self):
        conditions = self.requests.GET.get("filters")
        level = self.requests.GET.get("level")  # Change to cookies
        map_values = mappings.allowance_template_list_view

        raw_query = ConstructSelectQuery(AllowanceTemplate, conditions, level).search()
        values = ExtractAndBuildFromRawSQL(map_values).execute_string(raw_query)

        return {"value": values}

    def read_one(self):
        try:
            level = "company"  # Change to cookies
            sid = self.requests.GET.get("id")
            result = AllowanceTemplate.objects.filter(id=sid).values()

            conditions = "allowance_template_id_id,=," + sid + ",None"

            map_values = mappings.allowance_template_line_view
            line_query = ConstructSelectQuery(AllowanceTemplateLine, conditions, level).search()
            line_result = ExtractAndBuildFromRawSQL(map_values).execute_string(line_query)

            return {
                "header": extract_queryset(result)[0],
                "line": extract_queryset(line_result),
                "skeleton": mappings.allowance_template_line_view,
                # "query": line_query,
            }
        except IndexError as ie:
            return {
                'error': "Index Error", 'message': str(ie)
            }

    def read_as_pre_requisites(self):
        filters = self.requests.GET.get("filters")
        conditions = filters + "is_active,=,True,None"
        level = self.requests.GET.get("level")  # Change to cookies
        map_values = mappings.pre_requisite_response

        raw_query = ConstructSelectQuery(AllowanceTemplate, conditions, level).search()
        values = ExtractAndBuildFromRawSQL(map_values).execute_for_async_select(raw_query)

        return {"value": values}


class DeductionsCategoryRead:
    def __init__(self, requests):
        self.requests = requests

    def read_list(self):
        conditions = self.requests.GET.get("filters")
        queries = statements.select_read_deduction_category_list
        values = execute_raw_query(
            queries.format(build_conditions(conditions))
        )
        return {"value": values}

    def read_one(self):
        sid = self.requests.GET.get("id")
        queries = statements.select_read_deduction_category_list
        types = execute_raw_query(
            queries.format(sid)
        )
        return {"value": types}

    def read_as_pre_requisites(self):
        filters = self.requests.GET.get("filters")
        conditions = filters + "is_active,=,True,None"
        level = self.requests.GET.get("level")  # Change to cookies
        map_values = mappings.pre_requisite_response

        raw_query = ConstructSelectQuery(DeductionCategory, conditions, level).search()
        values = ExtractAndBuildFromRawSQL(map_values).execute_for_async_select(raw_query)

        return {"value": values}


class DeductionsTemplateRead:
    def __init__(self, requests):
        self.requests = requests

    def read_leave_type_list(self):
        conditions = self.requests.GET.get("filters")
        level = self.requests.GET.get("level")  # Change to cookies
        map_values = mappings.deduction_template_list_view

        raw_query = ConstructSelectQuery(DeductionTemplate, conditions, level).search()
        values = ExtractAndBuildFromRawSQL(map_values).execute_string(raw_query)

        return {"value": values}
        # return {"value": raw_query}

    def read_one(self):
        try:
            level = "company"  # Change to cookies
            sid = self.requests.GET.get("id")
            result = DeductionTemplate.objects.filter(id=sid).values()

            conditions = "deduction_template_id_id,=," + sid + ",None"

            map_values = mappings.deduction_template_line_view
            line_query = ConstructSelectQuery(DeductionMatrixTemplate, conditions, level).search()
            line_result = ExtractAndBuildFromRawSQL(map_values).execute_string(line_query)

            return {
                "header": extract_queryset(result)[0],
                "line": extract_queryset(line_result),
                "skeleton": mappings.deduction_template_line_view,
                # "query": line_query,
            }
        except IndexError as ie:
            return {
                'error': "Index Error", 'message': str(ie)
            }

    def read_as_pre_requisites(self):
        filters = self.requests.GET.get("filters")
        conditions = filters + "is_active,=,True,None"
        level = self.requests.GET.get("level")  # Change to cookies
        map_values = mappings.pre_requisite_response

        raw_query = ConstructSelectQuery(DeductionCategory, conditions, level).search()
        values = ExtractAndBuildFromRawSQL(map_values).execute_for_async_select(raw_query)

        return {"value": values}


class ScheduleTemplateRead:
    def __init__(self, requests):
        self.requests = requests

    def read_leave_type_list(self):
        conditions = self.requests.GET.get("filters")
        level = self.requests.GET.get("level")  # Change to cookies
        map_values = mappings.schedule_template_list_view

        raw_query = ConstructSelectQuery(ScheduleTemplate, conditions, level).search()
        values = ExtractAndBuildFromRawSQL(map_values).execute_string(raw_query)

        return {"value": values}
        # return {"value": raw_query}

    def read_one(self):
        try:
            level = "company"  # Change to cookies
            sid = self.requests.GET.get("id")
            line_conditions = "schedule_template_id_id,=," + sid + ",None"
            head_conditions = "id,=," + sid + ",None"

            # result = ScheduleTemplate.objects.filter(id=sid).values()
            head_map_values = mappings.schedule_template_list_view
            head_query = ConstructSelectQuery(ScheduleTemplate, head_conditions, level).search()
            head_result = ExtractAndBuildFromRawSQL(head_map_values).execute_string(head_query)
            head_process = ProcessHeaderInfo(extract_queryset(head_result)).execute()

            line_map_values = mappings.schedule_template_line_view
            line_query = ConstructSelectQuery(ScheduleTemplateLine, line_conditions, level).search()
            line_result = ExtractAndBuildFromRawSQL(line_map_values).execute_string(line_query)

            return {
                "header": head_process,
                "line": extract_queryset(line_result),
                "skeleton": mappings.schedule_template_line_view,
                # "query": line_query,
            }
        except IndexError as ie:
            return {
                'error': "Index Error", 'message': str(ie)
            }

    def read_as_pre_requisites(self):
        filters = self.requests.GET.get("filters")
        conditions = filters + "is_active,=,True,None"
        level = self.requests.GET.get("level")  # Change to cookies
        map_values = mappings.pre_requisite_response

        raw_query = ConstructSelectQuery(ScheduleTemplate, conditions, level).search()
        values = ExtractAndBuildFromRawSQL(map_values).execute_for_async_select(raw_query)

        return {"value": values}


class WorkSetupRead:
    def __init__(self, requests):
        self.requests = requests

    def read_as_pre_requisites(self):
        filters = self.requests.GET.get("filters")
        conditions = filters + "is_active,=,True,None"
        level = self.requests.GET.get("level")  # Change to cookies
        map_values = mappings.pre_requisite_response

        raw_query = ConstructSelectQuery(WorkSetup, conditions, level).search()
        values = ExtractAndBuildFromRawSQL(map_values).execute_for_async_select(raw_query)

        return {"value": values}


class EmployeeContractsTemplateRead:
    def __init__(self, requests):
        self.requests = requests

    def read_list(self):
        conditions = self.requests.GET.get("filters")
        level = self.requests.GET.get("level")  # Change to cookies
        map_values = mappings.employee_contracts_template_list_view

        raw_query = ConstructSelectQuery(EmployeeContractTemplate, conditions, level).search()
        values = ExtractAndBuildFromRawSQL(map_values).execute_string(raw_query)

        return {"value": values}
        # return {"value": raw_query}

    def read_one(self):
        try:
            level = "company"  # Change to cookies
            sid = self.requests.GET.get("id")
            head_conditions = "id,=," + sid + ",None"

            # result = ScheduleTemplate.objects.filter(id=sid).values()
            head_map_values = mappings.employee_contracts_template_list_view
            head_query = ConstructSelectQuery(EmployeeContractTemplate, head_conditions, level).search()
            head_result = ExtractAndBuildFromRawSQL(head_map_values).execute_string(head_query)
            head_process = ProcessHeaderInfo(extract_queryset(head_result)).execute()

            return {
                "header": head_process,
                "skeleton": mappings.employee_contracts_template_list_view,
                # "query": line_query,
            }
        except IndexError as ie:
            return {
                'error': "Index Error", 'message': str(ie)
            }
