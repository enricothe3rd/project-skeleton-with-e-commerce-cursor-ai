

select_read_leave_type_list = """
    SELECT
        A.id,
        A.name,
        A.is_paid,
        A.is_reset,
        A.is_convertible,
        A.convert_rate_percent,
        A.accumulate_precision,
        A.convert_precision,
        A.is_applied_straight,
        A.is_granted_upon_employment,
        A.grant_leave_after,
        A.initial_credits
    FROM
        payroll_leavetype A
    WHERE
        {}
"""

select_read_leave_type_one = """
    SELECT
        A.id,
        A.name,
        A.is_paid,
        A.is_reset,
        A.is_convertible,
        A.convert_rate_percent,
        A.accumulate_precision,
        A.convert_precision,
        A.is_applied_straight,
        A.is_granted_upon_employment,
        A.grant_leave_after,
        A.initial_credits
    FROM
        payroll_leavetype A
    WHERE
        A.id = {}
"""


select_read_attendance_category_list = """
    SELECT
        A.id,
        A.name,
        A.company_id,
        A.is_pro_rated,
        A.is_de_minimis,
        A.max_untaxable_amount
    FROM 
        payroll_allowancecategory A
    WHERE
        {}
"""


select_read_attendance_category_one = """
    SELECT
        A.id,
        A.name,
        A.company_id,
        A.is_pro_rated,
        A.is_de_minimis,
        A.max_untaxable_amount
    FROM 
        payroll_allowancecategory A
    WHERE
        A.id = {}
"""


select_read_deduction_category_list = """
    SELECT
        A.id,
        A.name
    FROM
        payroll_deductioncategory A
    WHERE
        {}
"""


select_read_deduction_category_one = """
    SELECT
        A.id,
        A.name
    FROM
        payroll_deductioncategory
    WHERE
        A.id = {}
"""