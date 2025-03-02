
deductions_async = """
    SELECT
        A.id as value,
        A.name as label
    FROM
        payroll_deduction A
"""

positions_async = """
    SELECT
        A.id as value,
        A.name as label
    FROM
        payroll_employeepositions A
    WHERE
        {}
"""

departments_async = """
    SELECT
        A.id as value,
        A.name as label
    FROM
        payroll_department A
    WHERE
        is_active = True AND A.company_id = {}
"""

leave_credits_async = """
    SELECT
        A.id as value,
        B.name as label
    FROM
        payroll_leavecredits A
    LEFT JOIN 
        payroll_leavetype B ON B.id = A.leave_type_id_id
    WHERE
        A.is_active = True AND {}
"""

fiscal_lines_async = """
    SELECT
        B.month as value,
        B.month as label
    FROM
        payroll_fiscalyear A
    LEFT JOIN 
        payroll_fiscalyearlines B ON B.fiscal_year_id = A.id
    WHERE
        A.is_active = True AND {}
"""

unassociated_users_async = """
    SELECT
        A.id as value,
        A.long_name as label
    FROM
        payroll_employee A
    WHERE
         {}
"""

other_income_types_async = """
    SELECT
        A.id as value,
        A.name as label
    FROM
        payroll_otherincometype A
    WHERE
         {}
"""

other_benefits_types_async = """
    SELECT
        A.id as value,
        A.name as label
    FROM
        payroll_otherbenefitstype A
    WHERE
         {}
"""