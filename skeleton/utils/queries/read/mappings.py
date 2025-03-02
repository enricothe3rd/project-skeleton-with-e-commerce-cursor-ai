# KEY = TABLE HEADER (USED IN DYNAMIC DATATABLES)
# INDEX 0 => INDEX OF FIELD IN QUERY RESULT; INDEX 1 => WIDGET/ TABLE VALUE IDENTIFIER
# INDEX 2 => VALID VALUES; INDEX 3 => IDENTIFY FORM CONTROL;
# INDEX 4 => RELATIONAL DATA ID -- INDEX OF FIELD IN QUERY RESULT;
# INDEX 5 => RELATIONAL TABLE; INDEX 6 => TECHNICAL NAME; INDEX 7 => IS REQUIRED?

leave_type_list_view = {
    "id":
        [0, 'integer', None, "pkey", None, None, "id", False],
    "Leave Type":
        [1, 'string', None, "text", None, None, "name", True],
    "Is Paid?":
        [2, 'bool', 'YesNo', "checkbox", None, None, "is_paid", True],
    "Value Resets":
        [4, 'bool', 'YesNo', "checkbox", None, None, "is_reset", True],
    "Convertible?":
        [5, 'bool', 'YesNo', "checkbox", None, None, "is_convertible", True],
    "Conversion Rate":
        [6, 'percent', None, "number", None, None, "conversion_rate", True],
}

leave_template_list_view = {
    "id":
        [0, 'integer', None, "pkey", None, None, "id", False],
    "Leave Template":
        [1, 'string', None, "text", None, None, "leave_template", True]
}

leave_template_line_view = {
    "id":
        [0, 'integer', None, "pkey", None, None, "id", False],
    "Name":
        [1, 'string', None, "text", None, None, "name", True],
    "Credits":
        [3, 'integer', None, "number", None, None, "credits", True],
    "Leave Type":
        [10, 'string', None, "select", 9, "leave_type", "leave_type_id", True],
}

allowance_category_list_view = {
    "id":
        [0, 'integer', None, "pkey", None, None, "id", False],
    "Name":
        [1, 'string', None, "text", None, None, "name", True],
}

allowance_template_list_view = {
    "id":
        [0, 'integer', None, "pkey", None, None, "id", False],
    "Name":
        [1, 'string', None, "text", None, None, "name", True],
}

deduction_category_list_view = {
    "id":
        [0, 'integer', None, "pkey", None, None, "id", False],
    "Name":
        [1, 'string', None, "text", None, None, "name", True],
}

allowance_template_line_view = {
    "id":
        [0, 'integer', None, "pkey", None, None, "id", False],
    "Name":
        [1, 'string', None, "text", None, None, "name", True],
    "Allowance Category":
        [13, 'string', None, "select", 12, "allowance_category", "category_id", True],
    "Amount":
        [4, "integer", None, "number", None, None, "amount", True],
    "Date From":
        [5, "date", None, "date", None, None, "date_from", False],
    "Date To":
        [6, "date", None, "date", None, None, "date_to", False],
    "Is Vatable?":
        [7, "bool", "YesNo", "checkbox", None, None, "is_vatable", True],
}

deduction_template_list_view = {
    "id":
        [0, 'integer', None, "pkey", None, None, "id", False],
    "Deduction Category":
        [7, 'string', None, "select", 6, "deduction_category", "category_id", True],
    "Is Mandatory?":
        [4, "bool", "YesNo", "checkbox", None, None, "is_mandatory", True],
}

deduction_template_line_view = {
    "id":
        [0, 'integer', None, "pkey", None, None, "id", False],
    "Fixed Amount":
        [3, 'integer', None, "number", None, None, "fixed_amount", True],
    "Employer Share":
        [4, 'integer', None, "number", None, None, "employer_share", True],
    "Salary From":
        [5, 'integer', None, "number", None, None, "salary_from", True],
    "Salary To":
        [6, 'integer', None, "number", None, None, "salary_to", True],
    "Percentage Amount":
        [7, 'integer', None, "number", None, None, "percentage_amount", True],
    "Date From":
        [8, "date", None, "date", None, None, "date_from", False],
    "Date To":
        [9, "date", None, "date", None, None, "date_to", False],
}

schedule_template_list_view = {
    "id":
        [0, 'integer', None, "pkey", None, None, "id", False],
    "Name":
        [1, 'string', None, "text", None, None, "name", True],
    "Date From":
        [2, "date", None, "date", None, None, "date_from", False],
    "Date To":
        [3, "date", None, "date", None, None, "date_to", False],
    "Is Flexi?":
        [4, "bool", "YesNo", "checkbox", None, None, "is_flexi", True],
    "Is Manual Scheduled?":
        [5, "bool", "YesNo", "checkbox", None, None, "is_manual_scheduled", True],
}

schedule_template_line_view = {
    "id":
        [0, 'integer', None, "pkey", None, None, "id", False],
    "Day":
        [1, 'string', None, "text", None, None, "name", True],
    "Time From":
        [2, "time", None, "time", None, None, "time_from", False],
    "Time To":
        [3, "time", None, "time", None, None, "time_to", False],
    # CARRIED TO OTHER DAY
    "Is Carried?":
        [4, "bool", "YesNo", "checkbox", None, None, "is_carried", True],
    "Duration":
        [5, 'integer', None, "number", None, None, "duration", True],
}

employee_contracts_template_list_view = {
    "id":
        [0, 'integer', None, "pkey", None, None, "id", False],
    "Name":
        [1, 'string', None, "text", None, None, "name", True],
    "Hourly Rate":
        [2, 'float', None, "number", None, None, "hourly_rate", True],
    "Work Hours":
        [3, "float", None, "number", None, None, "daily_work_hours", True],
    "Max Mandatory Contribution?":
        [4, "bool", "YesNo", "checkbox", None, None, "is_max_mandatory", True],
    "Leave Template":
        [14, "string", None, "select", 13, "leave_template", "leave_template_id", True],
    "Allowance Template":
        [18, 'string', None, "select", 17, "allowance_template", "allowance_template_id", True],
    "Deduction Template":
        [22, 'string', None, "select", 21, "deduction_template", "deduction_template_header_id", True],
    "Schedule Template":
        [25, 'string', None, "select", 24, "schedule_template", "schedule_template_id", True],
    "Require Attendance Approval?":
        [9, 'bool', "YesNo", "checkbox", None, None, "is_require_attendance_approval", True],
    "Work Setup":
        [33, 'string', None, "select", 32, "work_setup", "work_setup_id", True],
}

pre_requisite_response = {
    "value": 0,
    "label": 1,
}
