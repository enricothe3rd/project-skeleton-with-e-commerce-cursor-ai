
department_filters = """
    SELECT
        A.id as value,
        A.name as label
    FROM 
        payroll_department A
    WHERE 
        {}
"""

team_filters = """
    SELECT
        A.id as value,
        A.name as label
    FROM 
        payroll_team A
    WHERE 
        {}
"""

position_filters = """
    SELECT
        A.id as value,
        A.name as label
    FROM 
        payroll_employeepositions A
    WHERE 
        {}
"""

employee_filters = """
    SELECT
        A.id as value,
        A.long_name as label
    FROM 
        payroll_employee A
    WHERE 
        {}
    LIMIT 10
"""

fiscal_year_filters = """
    SELECT
        A.id as value,
        A.fiscal_year_code as label
    FROM 
        payroll_fiscalyear A
    WHERE 
        A.company_id = {}
"""