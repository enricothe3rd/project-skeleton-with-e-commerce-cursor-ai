import json
from django.http import HttpResponse
from django.conf import settings


class BuildResponse:
    def __init__(self, body):
        self.body = json.dumps(body)

    def get_response(self):
        response = HttpResponse(self.body)
        response['Access-Control-Allow-Origin'] = settings.CLIENT_SERVICE_URL
        response["Access-Control-Allow-Methods"] = "GET"
        response["Access-Control-Allow-Headers"] = "Content-Type,X-Auth-Token,Origin,Authorization,Cookie"
        response["Access-Control-Allow-Credentials"] = "true"
        return response

    def post_response(self):
        response = HttpResponse(self.body)
        response['Access-Control-Allow-Origin'] = settings.CLIENT_SERVICE_URL
        response["Access-Control-Allow-Methods"] = 'POST'
        response["Access-Control-Allow-Headers"] = "Content-Type,X-Auth-Token,Origin,Authorization,Cookie"
        response["Access-Control-Allow-Credentials"] = "true"
        return response

    @staticmethod
    def options_handler():
        response = HttpResponse()
        response['allow'] = 'get,post,put,delete,options'
        response['Access-Control-Allow-Origin'] = settings.CLIENT_SERVICE_URL
        response["Access-Control-Allow-Methods"] = 'POST'
        response["Access-Control-Allow-Headers"] = "Content-Type,X-Auth-Token,Origin,Authorization,Cookie"
        response["Access-Control-Allow-Credentials"] = "true"
        return response
