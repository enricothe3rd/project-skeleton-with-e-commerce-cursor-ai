from payroll.utils.general.general import Queries, ParseValues, EvaluateQueryResults, execute_raw_query
from payroll.utils.queries.statements import setup_select


class GetCompanyConfig:
    def __init__(self, company_id):
        self.company_id = company_id

    def execute(self):
        query = setup_select.read_company_config
        raw_value = execute_raw_query(
            query.format(self.company_id)
        )
        if len(raw_value) > 0:
            return raw_value[0]
        else:
            return {}  # LOAD DEFAULT
