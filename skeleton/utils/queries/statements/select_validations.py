
check_badge_no = """
    SELECT
        id,
        first_name,
        middle_name,
        last_name,
        suffix,
        professional_extensions
    FROM 
        payroll_employee
    WHERE
        badge_no = '{}' AND company_id = {}
"""

validate_shift_generate = """
    SELECT
        *
    FROM
        payroll_employeeshiftsgenerated A
    WHERE
        {}
    LIMIT 5
"""

shift_generate_simulate = """
    SELECT
        A.id,
        A.badge_no as employee_badge_no,
        A.first_name as employee_first_name,
        A.middle_name as employee_middle_name,
        A.last_name as employee_last_name,
        A.suffix as employee_suffix,
        A.professional_extensions as employee_professional_extensions,
        
        B.name as schedule_name
    FROM
        payroll_employee A
    LEFT JOIN
        payroll_schedule B ON B.employee_id_id = A.id
    WHERE
        B.is_manual_attendance = false AND {0}
    LIMIT {1} OFFSET {2}
"""

shift_regenerate_simulate = """
    SELECT
        A.id,
        A.badge_no as employee_badge_no,
        A.first_name as employee_first_name,
        A.middle_name as employee_middle_name,
        A.last_name as employee_last_name,
        A.suffix as employee_suffix,
        A.professional_extensions as employee_professional_extensions,

        B.name as schedule_name
    FROM
        payroll_employee A
    LEFT JOIN
        payroll_schedule B ON B.employee_id_id = A.id
    WHERE
        B.is_manual_attendance = false AND {0}
"""

shift_generate_fetch_unique_id = """
    SELECT
        B.employee_id_id as id
    FROM 
        payroll_employeeshiftsgenerated A
    LEFT JOIN 
        payroll_employeeshifts B ON A.id = B.generate_shift_id
    LEFT JOIN
        payroll_employee C ON C.id = B.employee_id_id
    WHERE
        {}
    GROUP BY 
        B.employee_id_id
"""

shift_generate_fetch = """
    SELECT
        A.date_from,
        A.date_to
    FROM 
        payroll_employeeshiftsgenerated A
    WHERE
        {}
"""

shift_fetch_employee_schedules = """
    SELECT
        A.id,
        
        B.name as schedule_name,
        
        C.time_from,
        C.time_to,
        C.day,
        C.is_carried
    FROM
        payroll_employee A
    LEFT JOIN
        payroll_schedule B ON B.employee_id_id = A.id
    LEFT JOIN
        payroll_scheduleline C ON C.schedule_id_id = B.id
    WHERE
        A.is_active = true AND {} 
"""

shift_generate_suggest_value = """
    SELECT
        MAX(date_to) as date_to
    FROM
        payroll_employeeshiftsgenerated A
    WHERE
        {}
"""

validate_leave_to_schedule = """
    SELECT
        A.datetime_from,
        A.employee_id_id
    FROM
        payroll_employeeshifts A
    WHERE
        A.datetime_from::text LIKE '{}%'
        AND  A.employee_id_id = {}
"""

validate_duplicate = """
    SELECT
        A.date::text,
        A.employee_id_id
    FROM
        payroll_leaveapplications A
    WHERE
        A.date::text LIKE '{}%' AND  
        A.employee_id_id = {} AND 
        A.is_active = True AND 
        A.approval_status != 'DECLINED'
"""

validate_time_entry = """
    SELECT
        A.id,
        A.time_in::text
    FROM
        payroll_attendance A 
    JOIN 
        payroll_employee B ON B.id = A.employee_id_id
    WHERE
        (A.time_in::text LIKE '{0}%' OR 
        (A.correct_time_in::text LIKE '{0}%' AND correction_approval_status = 'APPROVED')) AND  
        B.badge_no = '{1}'
"""

validate_ot_if_has_shift = """
    SELECT
        A.datetime_from,
        A.datetime_to,
        A.employee_id_id
    FROM
        payroll_employeeshifts A
    WHERE
        A.datetime_from::text LIKE '{}%'
        AND  A.employee_id_id = {}
"""

check_leave_type = """
    SELECT
        B.is_applied_straight
    FROM
        payroll_leavecredits A
    JOIN
        payroll_leavetype B ON B.id = A.leave_type_id_id
    WHERE 
        A.id = {}
"""

fetch_credits_number = """
    SELECT
        A.credits
    FROM
        payroll_leavecredits A
    WHERE
        A.id = {}
"""

fetch_origin_date = """
    SELECT
        A.origin_date
    FROM
        payroll_leaveapplications A
    WHERE
        A.id = {}
"""

fetch_core_leave = """
    SELECT
        A.id
    FROM
        payroll_leaveapplications A
    WHERE
        A.origin_date::text LIKE '{}%' AND A.employee_id_id = {} AND leave_credit_id = {}
"""
# A.origin_date::text LIKE '{}%'