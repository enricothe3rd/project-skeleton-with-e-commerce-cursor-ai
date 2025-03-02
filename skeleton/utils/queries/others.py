import json
from payroll.utils.general.general import Queries, ParseValues
from payroll.models.setup import (TimeInSource, WorkSetup)
from payroll.models.core import (AttendanceCorrectionReason)


class TimeInSourceQueries:
    def __init__(self, requests):
        self.request = requests
        self.body = json.loads(requests.body)

    def create(self):
        try:
            company_id = self.request.COOKIES['company_id']
            body = self.body['data']

            params = {
                "name": body['name'],
                "company_id": company_id
            }
            result = Queries(TimeInSource).execute_create(params)

            return result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def change(self):
        try:
            body = self.body['data']

            params = {
                "name": body['name'],
            }
            result = Queries(TimeInSource).execute_change(params, body['id'])

            return result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def deactivate(self):
        try:
            body = self.body['data']

            result = Queries(TimeInSource).execute_deactivate(body['id'])

            return result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def reactivate(self):
        try:
            body = self.body['data']

            result = Queries(TimeInSource).execute_reactivate(body['id'])

            return result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def read(self):
        pass

    def validate(self):
        pass


class WorkSetupQueries:
    def __init__(self, requests):
        self.request = requests
        self.body = json.loads(requests.body)

    def create(self):
        try:
            company_id = self.request.COOKIES['company_id']
            body = self.body['data']
            time_in_source_object = TimeInSource(id=body['timein_source_id'])

            params = {
                "name": body['name'],
                "timein_source_id": time_in_source_object,
                "company_id": company_id
            }
            result = Queries(WorkSetup).execute_create(params)

            return result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def change(self):
        try:
            body = self.body['data']

            params = {
                "name": body['name'],
                "timein_source_id": body['timein_source_id']
            }
            result = Queries(WorkSetup).execute_change(params, body['id'])

            return result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def deactivate(self):
        try:
            body = self.body['data']

            result = Queries(WorkSetup).execute_deactivate(body['id'])

            return result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def reactivate(self):
        try:
            body = self.body['data']

            result = Queries(WorkSetup).execute_reactivate(body['id'])

            return result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def read(self):
        pass

    def validate(self):
        pass


class AttendanceCorrectionQueries:
    def __init__(self, requests):
        self.request = requests
        self.body = json.loads(requests.body)

    def create(self):
        try:
            company_id = self.request.COOKIES['company_id']
            body = self.body['data']

            params = {
                "name": body['name'],
                "company_id": company_id
            }

            result = Queries(AttendanceCorrectionQueries).execute_create(params)

            return result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def change(self):
        try:
            body = self.body['data']

            params = {
                "name": body['name']
            }

            result = Queries(AttendanceCorrectionQueries).execute_change(params, body['id'])

            return result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def deactivate(self):
        try:
            body = self.body['data']

            result = Queries(AttendanceCorrectionQueries).execute_deactivate(body['id'])

            return result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def reactivate(self):
        try:
            body = self.body['data']

            result = Queries(AttendanceCorrectionQueries).execute_reactivate(body['id'])

            return result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def validate(self):
        pass

    def read(self):
        pass
