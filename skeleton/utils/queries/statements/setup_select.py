

read_positions_list_header = """
    SELECT
        A.id,
        A.name,
        B.id as department_id,
        B.name as department_name,
        C.id as supervisor_id,
        C.first_name,
        C.middle_name,
        C.last_name,
        C.suffix,
        C.professional_extensions,
        A.company_id
    FROM
        payroll_employeepositions A
    LEFT JOIN
        payroll_department B ON B.id = A.department_id_id
    LEFT JOIN
        payroll_employee C ON C.id = A.supervisor_id
    WHERE 
        {}
"""

read_positions_line = """
    SELECT
        *
    FROM
        payroll_employeepositionsline A 
    LEFT JOIN
        payroll_employeepositions B ON B.id = A.position_id_id
    WHERE
        {}
"""

read_departments = """
    SELECT
        A.*,
        B.id as manager_id,
        B.first_name,
        B.middle_name,
        B.last_name,
        B.suffix,
        B.professional_extensions,
        B.associated_user_id
    FROM
         payroll_department A
    LEFT JOIN
        payroll_employee B ON B.id = A.manager_id
    WHERE
        {}
"""

read_teams = """
    SELECT
        A.*,
        B.id as manager_id,
        B.first_name,
        B.middle_name,
        B.last_name,
        B.suffix,
        B.professional_extensions,
        B.associated_user_id,
        C.id as department_id,
        C.name as department_name
    FROM
         payroll_team A 
    LEFT JOIN
        payroll_employee B ON B.id = A.manager_id
    LEFT JOIN
        payroll_department C ON C.id = A.department_id
    WHERE
        {}
"""

read_holidays = """
    SELECT
        A.id,
        A.name,
        A.date,
        A.holiday_type,
        B.id as origin_id,
        B.name as origin_name,
        C.id as fiscal_year_id,
        C.fiscal_year_code as fiscal_year_name
    FROM
        payroll_holidays A
    LEFT JOIN
        payroll_countries B ON B.id = A.origin_id
    LEFT JOIN
        payroll_fiscalyear C ON C.id = A.fiscal_year_id
    WHERE
        {}
"""

read_users_list = """
    SELECT
        A.id,
        A.long_name,
        A.image
    FROM
        payroll_employee A
    WHERE
        {}
"""

read_associated_user = """
    SELECT
        A.id
    FROM
        payroll_employee A
    WHERE
        A.associated_user_id = {}
"""

read_company_config = """
    SELECT
        *
    FROM 
        payroll_config A
    WHERE
        A.company_id = {}
"""

read_all_company_with_config = """
    SELECT 
        A.*
    FROM
        payroll_config A
    WHERE
        A.id = {}
"""

read_last_payroll_release = """
    SELECT
        *
    FROM 
        payroll_releases A
    WHERE
        A.company_id = {} AND A.is_active = True
    ORDER BY A.date DESC
    LIMIT 1
"""

read_matching_fiscal_year = """
    SELECT
        id
    FROM
        payroll_fiscalyear
    WHERE
        fiscal_year_code = '{}'
    LIMIT 1
"""

read_matching_fiscal_month = """
    SELECT
        id
    FROM
        payroll_fiscalyearlines
    WHERE
        month = '{}' AND fiscal_year_id = {}
    LIMIT 1
"""
