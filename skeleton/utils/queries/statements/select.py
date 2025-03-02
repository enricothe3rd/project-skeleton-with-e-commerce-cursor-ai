

employee_onboarding_details = """
    SELECT 
        id,
        image,
        badge_no, 
        first_name,
        middle_name,
        last_name,
        suffix, 
        professional_extensions, 
        sex, 
        birthday,
        email, 
        mobile, 
        tin, 
        sss_no,
        hdmf_no,
        phic_no,
        is_manager,
        long_name
    FROM 
        payroll_employee A 
    WHERE
        id = {}
"""

employee_contract = """
    SELECT
        A.id,
        A.name,
        A.monthly_rate,
        A.hourly_rate,
        A.daily_work_hours,
        A.is_max_mandatory,
        A.is_require_attendance_approval,
        A.is_monthly_salary,
        A.factor_rate,
        A.date_start,
        A.date_end,
        A.is_regular,
        A.is_contractual,
        A.work_setup_id_id as work_setup_id,
        B.name as work_setup_name,
        A.employee_id_id as employee_id,
        A.department_id,
        C.name as department_name,
        A.employee_positions_id,
        D.name as employee_positions_name
    FROM 
        payroll_employeecontract A 
    LEFT JOIN 
        payroll_worksetup B ON B.id = A.work_setup_id_id 
    LEFT JOIN 
        payroll_department C ON C.id = A.department_id
    LEFT JOIN
        payroll_employeepositions D ON D.id = A.employee_positions_id
    WHERE 
        A.employee_id_id = {}
"""

employee_deduction_rel = """
    SELECT
        A.id,
        A.force_employee_share,
        A,force_employer_share,
        B.id as employee_id,
        C.id as deduction_id,
        C.name as deduction_name,
        C.is_mandatory
    FROM
        payroll_deductionemployeerel A
    LEFT JOIN
        payroll_employee B on B.id = A.employee_id_id
    LEFT JOIN
        payroll_deduction C on C.id = A.deduction_id_id
    WHERE
        A.employee_id_id = {}
"""

employee_positions_details = """
    SELECT
        A.id as id,
        B.id as position_id,
        B.name as position_name,
        B.department_id_id as department_id,
        C.name as department_name,
        A.employee_id_id as employee_id
    FROM 
        payroll_positionsemployeerel A 
    LEFT JOIN 
        payroll_employeepositions B ON B.id = A.position_id_id
    LEFT JOIN 
        payroll_department C ON C.id = B.department_id_id
    WHERE 
        A.employee_id_id = {}
"""

employee_bank_details = """
    SELECT
        id,
        bank_name,
        bank_no
    FROM
        payroll_employeebankdetails
    WHERE
        is_active = True AND employee_id_id = {}
"""

employee_addresses = """
    SELECT
        id,
        line,
        barangay,
        city,
        province,
        zip
    FROM
        payroll_employeeaddress
    WHERE
        employee_id_id = {}
"""

employee_leave_details = """
    SELECT
        A.id,
        A.credits,
        A.leave_type_id_id as leave_type_id,
        B.name as leave_type_name
    FROM
        payroll_leavecredits A
    LEFT JOIN 
        payroll_leavetype B ON B.id = A.leave_type_id_id
    WHERE
        A.is_active = True AND A.employee_id_id = {}
"""

employee_allowance_details = """
    SELECT
        A.id,
        A.name,
        A.amount,
        A.date_from,
        A.date_to,
        A.is_vatable,
        A.category_id_id as allowance_category_id,
        B.name as allowance_category_name,
        A.employee_id_id as employee_id
    FROM
        payroll_allowance A 
    LEFT JOIN
        payroll_allowancecategory B ON B.id = A.category_id_id
    WHERE
        A.is_active = True AND A.employee_id_id = {}
"""

employee_schedule_details_headers = """
    SELECT
        A.id,
        A.name,
        A.date_from,
        A.date_to,
        A.is_flexi,
        A.is_manual_scheduled,
        A.employee_id_id as employee_id
    FROM
        payroll_schedule A
    WHERE
        A.employee_id_id = {}
    ORDER BY A.id DESC
    LIMIT 1
"""

employee_schedule_details_lines = """
    SELECT
        A.id,
        B.id as line_id,
        B.day,
        B.time_from,
        B.time_to,
        B.is_carried,
        B.duration
    FROM
        payroll_schedule A
    LEFT JOIN
        payroll_scheduleline B ON B.schedule_id_id = A.id 
    WHERE
        A.employee_id_id = {}
"""

employee_deductions_details_headers = """
    SELECT
        A.id,
        A.name,
        A.is_mandatory,
        A.date_from,
        A.date_to,
        A.category_id_id as category_id,
        B.name as category_name,
        A.employee_id_id as employee_id
    FROM
        payroll_deduction A
    LEFT JOIN
        payroll_deductioncategory B ON B.id = A.category_id_id
    WHERE
        A.employee_id_id = {}
"""

employee_deductions_details_lines = """
    SELECT
        A.id,
        C.id as line_id,
        C.deduction_type,
        C.fixed_amount,
        C.employee_share,
        C.salary_from,
        C.salary_to,
        C.percentage_amount
    FROM
        payroll_deduction A
    LEFT JOIN
        payroll_deductionmatrix C ON C.deduction_id_id = A.id
    WHERE
        A.employee_id_id = {}
"""

employee_previous_employment = """
    SELECT
        A.id,
        A.previous_employer_name,
        tin,
        A.previous_employer_address,
        zip,
        A.employed_from,
        A.employed_to,
        employment_status,
        separation_reason,
        gross_compensation_income,
        
        statutory_smw,
        holiday_pay,
        overtime,
        night_shift,
        hazard_pay,
        r13th_month,
        de_minimis,
        statutory,
        salaries_other_compensation_non_tax,
        total_non_taxable,
        
        r13th_month_other_benefits,
        salaries_other_compensation_tax,
        A.taxable_amount,
        A.taxes_withheld,
        A.is_fresh_graduate
    FROM 
        payroll_previousemployer A
    WHERE
        A.employee_id = {}
"""

kiosk_get_last = """
    SELECT
        A.id,
        A.time_in,
        A.time_out,
        A.employee_id_id as employee_id,
        B.first_name,
        B.middle_name,
        B.last_name,
        B.suffix,
        B.professional_extensions
    FROM
        payroll_attendance A
    LEFT JOIN
        payroll_employee B ON A.employee_id_id = B.id
    WHERE 
        B.badge_no = '{}' AND A.company_id = {} AND A.is_active = True
    ORDER BY id DESC
    LIMIT 1
"""

kiosk_get_response = """
    SELECT
        A.id,
        A.time_in,
        A.time_out,
        A.employee_id_id as employee_id,
        B.first_name,
        B.middle_name,
        B.last_name,
        B.suffix,
        B.professional_extensions
    FROM
        payroll_attendance A
    LEFT JOIN
        payroll_employee B ON A.employee_id_id = B.id
    WHERE 
        A.id = {}
    ORDER BY id DESC
    LIMIT 1
"""

attendances_get_list = """
    SELECT
        A.id,
        A.time_in,
        A.time_out,
        A.correct_time_in,
        A.correct_time_out,
        A.ot_from,
        A.ot_to,
        A.manual_ot_duration,
        A.manual_tardiness_duration,
        
        A.manual_attendance_type,
        
        A.attendance_approval_status,
        A.correction_approval_status,
        A.ot_approval_status,
        
        A.correction_remarks,
        
        B.id as employee_id,
        B.badge_no as employee_badge_no,
        B.first_name as employee_first_name,
        B.middle_name as employee_middle_name,
        B.last_name as employee_last_name,
        
        C.id as attendance_approved_by_id,
        C.first_name as attendance_approve_first_name,
        C.middle_name as attendance_approve_first_name,
        C.last_name as attendance_approve_first_name,
        
        D.id as correction_approved_by_id,
        D.first_name as correction_approve_first_name,
        D.middle_name as correction_approve_middle_name,
        D.last_name as correction_approve_last_name,
        
        E.id as ot_approved_by_id,
        E.first_name as ot_approve_first_name,
        E.middle_name as ot_approve_middle_name,
        E.last_name as ot_approve_last_name,
        
        G.id as employee_positions_id,
        G.name as employee_position_name,
        
        J.id as timein_source_id,
        J.name as timein_source_name
    FROM 
        payroll_attendance A
    JOIN
        payroll_employee B ON A.employee_id_id = B.id
    LEFT JOIN
        payroll_employee C ON A.attendance_approved_by_id = C.id
    LEFT JOIN
        payroll_employee D ON A.correction_approved_by_id = D.id
    LEFT JOIN
        payroll_employee E ON A.ot_approved_by_id = E.id
    JOIN 
        payroll_employeecontract F ON F.employee_id_id = B.id
    LEFT JOIN
        payroll_employeepositions G ON F.employee_positions_id = G.id
    LEFT JOIN
        payroll_department H ON F.department_id = H.id
    LEFT JOIN
        payroll_team I ON F.team_id = I.id
    LEFT JOIN
        payroll_timeinsource J ON A.timein_source_id_id = J.id
    WHERE
        {}
    ORDER BY time_in DESC
"""

fetch_managed_departments = """
    SELECT
        A.id
    FROM
        payroll_department A
    WHERE
        A.manager_id = {}
"""

fetch_managed_teams = """
    SELECT
        A.id
    FROM
        payroll_team A
    WHERE
        A.manager_id = {}
"""

fetch_managed_positions = """
    SELECT
        A.id
    FROM
        payroll_employeepositions A
    WHERE
        A.supervisor_id = {}
"""

attendances_get_one = """
    SELECT
        A.id,
        A.time_in,
        A.time_out,
        A.correct_time_in,
        A.correct_time_out,
        A.ot_from,
        A.ot_to,
        A.manual_ot_duration,
        A.manual_tardiness_duration,
        
        A.attendance_approval_status,
        A.correction_approval_status,
        A.ot_approval_status,
        
        A.correction_remarks,
        
        B.id as employee_id,
        B.badge_no as employee_badge_no,
        B.first_name as employee_first_name,
        B.middle_name as employee_middle_name,
        B.last_name as employee_last_name,
        
        C.id as attendance_approved_by_id,
        C.first_name as attendance_approve_first_name,
        C.middle_name as attendance_approve_first_name,
        C.last_name as attendance_approve_first_name,
        
        D.id as correction_approved_by_id,
        D.first_name as correction_approve_first_name,
        D.middle_name as correction_approve_middle_name,
        D.last_name as correction_approve_last_name,
        
        E.id as ot_approved_by_id,
        E.first_name as ot_approve_first_name,
        E.middle_name as ot_approve_middle_name,
        E.last_name as ot_approve_last_name,
        
        F.id as employee_positions_id,
        F.name as employee_position_name,
        
        G.id as timein_source_id,
        G.name as timein_source_name
    FROM 
        payroll_attendance A
    LEFT JOIN
        payroll_employee B ON A.employee_id_id = B.id
    LEFT JOIN
        payroll_employee C ON A.attendance_approved_by_id = C.id
    LEFT JOIN
        payroll_employee D ON A.correction_approved_by_id = D.id
    LEFT JOIN
        payroll_employee E ON A.ot_approved_by_id = E.id
    LEFT JOIN
        payroll_employeepositions F ON A.position_id_id = F.id
    LEFT JOIN
        payroll_timeinsource G ON A.timein_source_id_id = G.id
    WHERE
        {}
"""

attendances_get_query = """
    SELECT
        A.id,
        A.time_in,
        A.time_out,
        A.correct_time_in,
        A.correct_time_out,
        A.ot_from,
        A.ot_to,
        A.manual_ot_duration,
        A.manual_tardiness_duration,
        A.manual_undertime_duration,
        A.manual_leave_applied,
        A.manual_is_absent,
        A.manual_is_rest_day_ot,
        A.manual_attendance_type,

        A.attendance_approval_status,
        A.correction_approval_status,
        A.ot_approval_status,

        A.correction_remarks,

        B.id as employee_id,
        B.badge_no as employee_badge_no,
        B.first_name as employee_first_name,
        B.middle_name as employee_middle_name,
        B.last_name as employee_last_name,
        B.long_name,

        C.id as attendance_approved_by_id,
        C.first_name as attendance_approve_first_name,
        C.middle_name as attendance_approve_first_name,
        C.last_name as attendance_approve_first_name,

        D.id as correction_approved_by_id,
        D.first_name as correction_approve_first_name,
        D.middle_name as correction_approve_middle_name,
        D.last_name as correction_approve_last_name,

        E.id as ot_approved_by_id,
        E.first_name as ot_approve_first_name,
        E.middle_name as ot_approve_middle_name,
        E.last_name as ot_approve_last_name,

        F.id as employee_positions_id,
        F.name as employee_position_name,

        G.id as timein_source_id,
        G.name as timein_source_name
    FROM 
        payroll_attendance A
    LEFT JOIN
        payroll_employee B ON A.employee_id_id = B.id
    LEFT JOIN
        payroll_employee C ON A.attendance_approved_by_id = C.id
    LEFT JOIN
        payroll_employee D ON A.correction_approved_by_id = D.id
    LEFT JOIN
        payroll_employee E ON A.ot_approved_by_id = E.id
    LEFT JOIN
        payroll_employeepositions F ON A.position_id_id = F.id
    LEFT JOIN
        payroll_timeinsource G ON A.timein_source_id_id = G.id
    WHERE
        A.is_payroll_released = False AND {}
    ORDER BY time_in DESC
"""

leaves_application_get = """
    SELECT
        A.id,
        A.date,
        A.duration,
        A.approval_status,
        A.approval_remarks,
        A.leave_credit_id,
        
        B.id as leave_type_id,
        E.name as leave_type_name,
        B.credits,
        
        C.id as employee_id,
        C.badge_no as employee_badge_no,
        C.first_name as employee_first_name,
        C.middle_name as employee_middle_name,
        C.last_name as employee_last_name,
        C.suffix as employee_suffix,
        C.professional_extensions as employee_professional_extensions,
        C.long_name,
        
        D.id as approver_id,
        D.first_name as approver_first_name,
        D.middle_name as approver_middle_name,
        D.last_name as approver_last_name,
        D.suffix as approver_suffix,
        D.professional_extensions as approver_professional_extensions
    FROM 
        payroll_leaveapplications A
    LEFT JOIN
        payroll_leavecredits B ON B.id = A.leave_credit_id
    LEFT JOIN
        payroll_employee C ON C.id = A.employee_id_id
    LEFT JOIN
        payroll_employee D ON D.id = A.approved_by_id
    LEFT JOIN 
        payroll_leavetype E ON E.id = B.leave_type_id_id
    JOIN 
        payroll_employeecontract F ON F.employee_id_id = A.employee_id_id
    LEFT JOIN
        payroll_employeepositions G ON F.employee_positions_id = G.id
    LEFT JOIN
        payroll_department H ON F.department_id = H.id
    LEFT JOIN
        payroll_team I ON F.team_id = I.id
    WHERE 
        {}
    ORDER BY date DESC
"""

leave_credit_get = """
    SELECT
        A.id,
        A.credits,
        
        B.id as leave_type_id,
        B.name,
        
        C.id as employee_id,
        C.badge_no as employee_badge_no,
        C.first_name as employee_first_name,
        C.middle_name as employee_middle_name,
        C.last_name as employee_last_name,
        C.suffix as employee_suffix,
        C.professional_extensions as employee_professional_extensions
    FROM
        payroll_leavecredits A
    LEFT JOIN 
        payroll_leavetype B ON B.id = A.leave_type_id_id
    LEFT JOIN
        payroll_employee C ON C.id = A.employee_id_id
    WHERE
        {}
"""

shift_generated_list = """
    SELECT
        id,
        date_from,
        date_to
    FROM
        payroll_employeeshiftsgenerated A
    WHERE
        {}
"""

shift_list_get = """
    SELECT
        A.id,
        A.datetime_from,
        A.datetime_to,
        A.is_autogenerated,
        
        B.id as employee_id,
        B.badge_no as employee_badge_no,
        B.first_name as employee_first_name,
        B.middle_name as employee_middle_name,
        B.last_name as employee_last_name,
        B.suffix as employee_suffix,
        B.professional_extensions as employee_professional_extensions,
        
        C.id as created_by,
        C.first_name as created_by_first_name,
        C.middle_name as created_by_middle_name,
        C.last_name as created_by_last_name,
        C.suffix as created_by_suffix,
        C.professional_extensions as created_by_professional_extensions,
        
        D.id as generate_shift_id,
        D.date_from as generate_shift_date_from,
        D.date_to as generate_shift_date_to
    FROM
        payroll_employeeshifts A
    LEFT JOIN 
        payroll_employee B ON B.id = A.employee_id_id
    LEFT JOIN 
        payroll_employee C ON C.id = A.created_by_id
    LEFT JOIN
        payroll_employeeshiftsgenerated D ON D.id = A.generate_shift_id
    WHERE
        {}
    ORDER BY A.datetime_from DESC
"""

get_employee_count = """
    SELECT
        COUNT(A.badge_no)
    FROM 
        payroll_employee A
    WHERE
        company_id = {} AND A.date_create::text LIKE '{}%'
"""

get_department_usages = """
    SELECT
        A.id
    FROM 
        payroll_employee A
    JOIN
        payroll_employeecontract B ON A.id = B.employee_id_id
    WHERE
        A.company_id = {} AND B.department_id = {} AND A.is_active = True
"""

get_team_usages = """
    SELECT
        A.id
    FROM 
        payroll_employee A
    JOIN
        payroll_employeecontract B ON A.id = B.employee_id_id
    WHERE
        A.company_id = {} AND B.team_id = {} AND A.is_active = True
"""

get_positions_usages = """
    SELECT
        A.id
    FROM 
        payroll_employee A
    JOIN
        payroll_employeecontract B ON A.id = B.employee_id_id
    WHERE
        A.company_id = {} AND B.employee_positions_id = {} AND A.is_active = True
"""

get_other_deductions_per_employee = """
    SELECT
        A.*,
        B.name as deduction_category_name,
        C.long_name
    FROM
        payroll_otherdeductions A
    JOIN
        payroll_deductioncategory B ON A.deduction_category_id = B.id
    JOIN 
        payroll_employee C ON A.employee_id_id = C.id
    WHERE
        A.employee_id_id = {} AND A.is_active = True
"""

get_all_employees = """
    SELECT
        A.id,
        A.first_name,
        A.middle_name,
        A.last_name,
        A.suffix
    FROM 
        payroll_employee A
    WHERE
        company_id = {}
"""

get_all_departments = """
    SELECT
        A.id,
        A.name
    FROM 
        payroll_department A
    WHERE
        A.company_id = {} AND A.is_active = True
"""

get_all_positions = """
    SELECT
        A.id,
        A.name
    FROM 
        payroll_employeepositions A
    WHERE
        A.company_id = {} AND A.is_active = True
"""

get_all_teams = """
    SELECT
        A.id,
        A.name
    FROM 
        payroll_team A
    WHERE
        A.company_id = {} AND A.is_active = True
"""

get_all_schedules = """
    SELECT
        B.id,
        B.name
    FROM 
        payroll_employee A
    JOIN 
        payroll_schedule B ON A.id = B.employee_id_id
    WHERE
        A.company_id = {} AND A.is_active = True
"""

get_all_statutory_deductions = """
    SELECT
        A.id,
        A.name
    FROM
        payroll_deductions A
    WHERE
        A.is_active = True
"""

get_tax_payments = """
    SELECT
        A.id,
        A.date,
        A.amount,
        A.payment_status,
        A.approval_status,
        A.bir_reference_no,
        A.payment_reference_no,
        A.company_id,
        A.is_active
    FROM
        payroll_taxpayments A
    WHERE
        {}
"""