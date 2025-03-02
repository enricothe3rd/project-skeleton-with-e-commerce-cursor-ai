import json
import sys
import os
from payroll.utils.general.payroll_computation import PayrollGenerateAutomations


class GeneratePayroll:
    def __init__(self, requests):
        self.request = requests
        self.body = json.loads(requests.body)

    def execute(self):
        try:
            company_id = self.request.COOKIES['company_id']
            body = self.body['data']

            generated_payroll = PayrollGenerateAutomations(
                sid=body["id"],
                date=body["date"],
                cutoff_from=body["cutoff_from"],
                cutoff_to=body["cutoff_to"],
                payroll_cycle=body["payroll_cycle"],
                fiscal_month=body["fiscal_month"],
                produce_gross_deductions=body["produce_gross_deductions"],
                produce_basic_deductions=body["produce_basic_deductions"],
                other_income=body["other_income"],
                other_benefits=body["other_benefits"],
                earning_adjustment=body["earning_adjustment"],
                company_id=company_id
            ).execute()
            return str(generated_payroll)
            # print(body)
            # return str(body)

        except KeyError as key_err:
            print(str(key_err))
            return {"Key Error": str(key_err)}
        except Exception as e:
            e_type, e_object, e_traceback = sys.exc_info()
            e_filename = os.path.split(
                e_traceback.tb_frame.f_code.co_filename
            )[1]
            e_message = str(e)
            e_line_number = e_traceback.tb_lineno
            print(e_message)
            return {"Ex Error": {
                "type": str(e_type),
                "filename": str(e_filename),
                "line": str(e_line_number),
                "message": str(e_message)
            }}
