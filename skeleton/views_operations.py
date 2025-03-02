# import json
# from django.views import View
# from django.http import HttpResponse
# from skeleton.utils.general.BuildHttpResponse import BuildResponse
# from skeleton.utils.authenticate import RequestAuthentication

# class CRUDTemplate(View):
#     def options(self, request, *args, **kwargs):
#         return BuildResponse(None).options_handler()
#
#     def post(self, requests):
#         response = RequestAuthentication(
#             self.execute, requests,
#             ["SUPER", "COMPANY", "IMPLEMENTOR"]
#         ).execute()
#         return BuildResponse(response).post_response()
#
#     @staticmethod
#     def execute(request):
#         return LeaveProcesses(request).leave_template_execute()

