
select_payroll_report = """
    SELECT
        A.date,
        A.payroll_cycle,
        A.fiscal_year_id,
        I.fiscal_year_code as fiscal_year_name,
        A.fiscal_year_line_id,
        J.month as fiscal_line_name,
        C.id as employee_id,
        F.id as position_id,
        G.id as department_id,
        H.id as team_id,
        C.long_name,
        F.name as position,
        G.name as department,
        H.name as team,
        B.*
    FROM
        payroll_releases A
    JOIN
        payroll_releasesemployeetotals B ON A.id = B.releases_id
    JOIN 
        payroll_employee C ON C.id = B.employee_id
    JOIN 
        payroll_employeecontract D ON D.employee_id_id = C.id
    LEFT JOIN 
        payroll_employeepositions F ON F.id = D.employee_positions_id
    LEFT JOIN
        payroll_department G ON G.id = D.department_id
    LEFT JOIN
        payroll_team H ON H.id = D.department_id
    JOIN
        payroll_fiscalyear I ON I.id = A.fiscal_year_id
    JOIN
        payroll_fiscalyearlines J ON J.id = A.fiscal_year_line_id
    WHERE
        {} A.approval_status = 'APPROVED' AND A.is_active = True
"""

select_employee_data = """
    SELECT
        A.id,
        A.long_name,
        B.hourly_rate,
        B.monthly_rate,
        B.daily_work_hours,
        B.factor_rate,
        B.date_start,
        B.is_monthly_salary
    FROM 
        payroll_employee A
    JOIN
        payroll_employeecontract B ON A.id = B.employee_id_id
    WHERE 
        {} A.is_active = True
"""

select_allowances_data = """
    SELECT
        A.date,
        A.fiscal_year_id,
        E.fiscal_year_code as fiscal_year_name,
        A.fiscal_year_line_id,
        F.month as fiscal_line_name,
        C.id as employee_id,
        C.long_name, 
        G.daily_gross,
        A.payroll_cycle,
        H.amount as allowance_amount,
        I.max_untaxable_amount as annual_untaxable_amount,
        I.tag_2316_id,
        J.code
    FROM
        payroll_releases A
    JOIN
        payroll_releasesemployeetotals B ON A.id = B.releases_id
    JOIN 
        payroll_employee C ON C.id = B.employee_id
    JOIN 
        payroll_employeecontract D ON D.employee_id_id = C.id
    JOIN
        payroll_fiscalyear E ON E.id = A.fiscal_year_id
    JOIN
        payroll_fiscalyearlines F ON F.id = A.fiscal_year_line_id
    JOIN
        payroll_releasesaccumulatedallowance G ON B.id = G.releases_employee_id
    JOIN
        payroll_allowance H ON H.id = G.employee_allowance_id_id
    JOIN
        payroll_allowancecategory I ON I.id = H.category_id_id
    LEFT JOIN
        payroll_tags2316 J ON J.id = I.tag_2316_id
    WHERE
        {} A.approval_status = 'APPROVED' AND A.is_active = True
"""

fetch_annual_tax_table = """
    SELECT
        A.id,
        A.amount,
        A.salary_from,
        A.salary_to,
        A.amount_to_add
    FROM 
        payroll_tax A
    WHERE
        A.is_active = True AND A.payroll_schedule = '{}'
"""

fetch_employee_deductions = """
    SELECT
        A.long_name,
        B.deduction_id_id,
        B.force_employee_share
    FROM 
        payroll_employee A
    JOIN
        payroll_deductionemployeerel B ON A.id = B.employee_id_id
    WHERE
        {} A.is_active = True
"""

fetch_deduction_matrix = """
    SELECT
        A.id,
        B.employee_max_contrib,
        B.salary_from,
        B.salary_to,
        B.employee_fixed_amount,
        B.employer_fixed_amount,
        B.employee_percent_amount,
        B.employer_percent_amount,
        B.employer_max_contrib
    FROM
        payroll_deduction A
    JOIN 
        payroll_deductionmatrix B ON B.deduction_id_id = A.id
    WHERE 
        A.is_active = True
"""

fetch_employee_allowance = """
    SELECT
        A.long_name,
        B.amount,
        C.is_de_minimis,
        C.max_untaxable_amount
    FROM
        payroll_employee A
    JOIN 
        payroll_allowance B ON A.id = B.employee_id_id AND B.is_active = True
    JOIN 
        payroll_allowancecategory C ON C.id = B.category_id_id
    WHERE
        {} A.is_active = True
"""

fetch_employee_basic_info = """
    SELECT
        A.id as employee_id,
        A.first_name,
        A.middle_name,
        A.last_name,
        A.suffix,
        A.professional_extensions,
        A.birthday,
        A.mobile,
        A.tin,
        B.date_start,
        B.hourly_rate,
        B.monthly_rate,
        B.is_monthly_salary,
        B.factor_rate,
        B.daily_work_hours,
        C.line,
        C.barangay,
        C.city,
        C.province,
        C.zip,
        D.is_fresh_graduate,
        D.previous_employer_name,
        D.previous_employer_address,
        D.tin as prev_tin,
        D.zip as prev_zip,
        D.employed_from,
        D.employed_to,
        D.employment_status as employment_status_prev,
        D.separation_reason as separation_reason_prev,
        D.gross_compensation_income,
        D.statutory_smw,
        D.holiday_pay,
        D.overtime,
        D.night_shift,
        D.hazard_pay,
        D.r13th_month,
        D.de_minimis,
        D.statutory,
        D.salaries_other_compensation_non_tax,
        D.total_non_taxable,
        D.r13th_month_other_benefits,
        D.salaries_other_compensation_tax,
        D.taxable_amount,
        D.taxes_withheld
    FROM 
        payroll_employee A
    JOIN
        payroll_employeecontract B ON B.employee_id_id = A.id
    LEFT JOIN
        payroll_employeeaddress C ON C.employee_id_id = A.id
    LEFT JOIN
        payroll_previousemployer D ON D.employee_id = A.id
    {}
"""

fetch_employee_generated_13th_month = """
    SELECT 
        A.employee_id,
        A.amount,
        A.approval_status
    FROM
        payroll_r13thmonthpay A
    WHERE
        {} A.is_active = True AND A.fiscal_year_id = {}
"""

fetch_other_benefits = """
    SELECT
        A.payroll_cycle,
        B.employee_id,
        B.amount,
        B.employee_id,
        B.untaxable_threshold,
        C.name
    FROM
        payroll_releases A
    JOIN
        payroll_otherbenefits B ON B.releases_id = A.id
    JOIN 
        payroll_otherbenefitstype C ON C.id = B.other_benefit_type_id
    WHERE
        {} A.is_active = True AND A.approval_status = 'APPROVED' AND A.fiscal_year_id = {}
"""

fetch_other_income = """
    SELECT
        B.employee_id,
        B.amount,
        B.employee_id,
        C.name,
        C.tag_2316_id,
        D.code
    FROM
        payroll_releases A
    JOIN
        payroll_otherincome B ON B.releases_id = A.id
    JOIN
        payroll_otherincometype C ON C.id = B.other_income_type_id
    LEFT JOIN
        payroll_tags2316 D ON C.tag_2316_id = D.id
    WHERE
        {} A.is_active = True AND A.approval_status = 'APPROVED' AND A.fiscal_year_id = {}
"""

fetch_earnings_adjustment = """
    SELECT
        B.employee_id,
        B.amount,
        B.employee_id
    FROM
        payroll_releases A
    JOIN
        payroll_earningadjustments B ON B.releases_id = A.id
    WHERE
        {} A.is_active = True AND A.approval_status = 'APPROVED' AND A.fiscal_year_id = {}
"""

# DASHBOARD QUERIES
total_employees = """
    SELECT 
        COUNT(A.id)
    FROM 
        payroll_employee A
    WHERE 
        A.company_id = {} and A.is_active = True
"""

new_employees = """
    SELECT
        COUNT(A.id)
    FROM 
        payroll_employee A
    JOIN
        payroll_employeecontract B ON A.id = B.employee_id_id
    WHERE 
        A.company_id = {} AND B.date_start > '{}' AND A.is_active = True
"""

monthly_on_leave = """
    SELECT
        COUNT(A.id)
    FROM
        payroll_leaveapplications A
    WHERE
        A.company_id = {} AND A.date > '{}' AND A.approval_status = 'APPROVED'
"""

daily_on_leave = """
    SELECT
        COUNT(A.id)
    FROM 
        payroll_leaveapplications A
    WHERE
        A.company_id = {} AND A.date = '{}' AND A.approval_status = 'APPROVED'
"""

daily_attendance = """
    SELECT
        COUNT(A.id)
    FROM 
        payroll_attendance A
    WHERE
        A.company_id = {} AND A.time_in::text LIKE '{}%' AND A.attendance_approval_status = 'APPROVED'
"""

attendance_correction_status_counts = """
    SELECT
        COUNT(A.id) as Pending, 0 as Approved, 0 as Declined
    FROM 
        payroll_attendance A
    WHERE 
        A.correct_time_in is not null AND A.attendance_approval_status = 'PENDING' AND 
        A.timein_source_id_id = 1 AND A.time_in > '{1}' AND {0}
    UNION ALL
    SELECT
        0 as Pending, COUNT(A.id) as Approved, 0 as Declined
    FROM
        payroll_attendance A
    WHERE
         A.correct_time_in is not null AND A.attendance_approval_status = 'APPROVED' AND 
         A.timein_source_id_id = 1 AND A.time_in > '{1}' AND {0}
    UNION ALL
    SELECT
        0 as Pending, 0 as Approved, COUNT(A.id) as Declined
    FROM
        payroll_attendance A
    WHERE
         A.correct_time_in is not null AND A.attendance_approval_status = 'DECLINED' AND 
         A.timein_source_id_id = 1 AND A.time_in > '{1}' AND {0}
"""

overtime_requests_status_counts = """
    SELECT
        COUNT(A.id) as Pending, 0 as Approved, 0 as Declined
    FROM 
        payroll_attendance A
    WHERE
         A.ot_from is not null AND A.ot_approval_status = 'PENDING' AND
         A.time_in > '{1}' AND {0}
    UNION ALL
    SELECT
        0 as Pending, COUNT(A.id) as Approved, 0 as Declined
    FROM
        payroll_attendance A
    WHERE
         A.ot_from is not null AND A.ot_approval_status = 'APPROVED' AND
         A.time_in > '{1}' AND {0}
    UNION ALL
    SELECT
        0 as Pending, 0 as Approved, COUNT(A.id) as Declined
    FROM
        payroll_attendance A
    WHERE
         A.ot_from is not null AND A.ot_approval_status = 'DECLINED' AND
         A.time_in > '{1}' AND {0}
"""

leave_application_requests_status_counts = """
    SELECT
        COUNT(A.id) as pending, 0 as approved, 0 as declined
    FROM 
        payroll_leaveapplications A
    WHERE
        A.approval_status = 'PENDING' AND A.is_active = True AND
        A.date > '{1}' AND {0}
    UNION ALL
    SELECT
        0 as pending, COUNT(A.id) as approved, 0 as declined
    FROM
        payroll_leaveapplications A
    WHERE
        A.approval_status = 'APPROVED' AND A.is_active = True AND
        A.date > '{1}' AND {0}
    UNION ALL
    SELECT
        0 as pending, 0 as approved, COUNT(A.id) as declined
    FROM
        payroll_leaveapplications A
    WHERE
        A.approval_status = 'DECLINED' AND A.is_active = True AND
        A.date > '{1}' AND {0}
"""

fetch_all_departments = """
    SELECT
        A.id,
        A.name
    FROM 
        payroll_department A
    WHERE
        A.company_id = {}
"""

fetch_employees_count = """
    SELECT
        COUNT(A.id),
        C.name
    FROM
        payroll_employee A
    LEFT JOIN
        payroll_employeecontract B ON A.id = B.employee_id_id
    LEFT JOIN
        payroll_department C ON B.department_id = C.id
    WHERE 
        A.company_id = {} AND B.date_start::text LIKE '{}%' AND A.is_active = True
    GROUP BY
        C.name
"""

fetch_department_salaries = """
    SELECT
        SUM(A.net_total) as net_total,
        D.name
    FROM
        payroll_releasesemployeetotals A
    JOIN
        payroll_employee B ON A.employee_id = B.id
    LEFT JOIN
        payroll_employeecontract C ON C.employee_id_id = B.id
    LEFT JOIN
        payroll_department D ON D.id = C.department_id
    JOIN
        payroll_releases E ON E.id = A.releases_id
    JOIN
        payroll_fiscalyear F ON F.id = E.fiscal_year_id
    WHERE
        E.company_id = {} AND F.fiscal_year_code = '{}' AND E.is_active = True
    GROUP BY
        D.name
"""


fetch_employee_five_attendances = """
    SELECT
        CAST(
            CASE
                WHEN A.correction_approval_status = 'APPROVED'
                    THEN A.correct_time_in
                ELSE A.time_in
            END as timestamp
        ) as time_in,
        CAST(
            CASE
                WHEN A.correction_approval_status = 'APPROVED'
                    THEN A.correct_time_out
                ELSE A.time_out
            END as timestamp
        ) as time_out
    FROM
        payroll_attendance A
    WHERE 
        A.employee_id_id = {} AND A.is_active = True
    ORDER BY
        A.time_in DESC
    LIMIT 
        5
"""
