import requests
from django.conf import settings


class RequestAuthentication:
    def __init__(self, function, request, authorizations):
        self.function = function
        self.authorizations = authorizations
        self.request = request

    def execute(self):
        try:
            params = self.request
            payload = {"authorizations": self.authorizations}
            cookies = {
                'company_id': params.COOKIES['company_id'],
                'token': params.COOKIES['token'],
                'user_id': params.COOKIES['user_id']
            }
            response = requests.post(
                settings.USER_SERVICE_URL + '/users/validate-login',
                json=payload,
                cookies=cookies,
                verify=False
            )
            response_dict = response.json()
            print("Authentication Result: " + str(response_dict["result"]))
            if response_dict["result"]:
                return self.function(self.request)
            else:
                return {"error": "An error occurred!"}
        except ValueError as val_err:
            return {"error": "Value Error"+str(val_err), "message": "Value Error"}
        except KeyError as key_err:
            return {"error": "Key Error: "+str(key_err), "message": "User not logged in"}
