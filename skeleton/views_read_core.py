# from django.views import View
# from skeleton.utils.general.BuildHttpResponse import BuildResponse
# from skeleton.utils.authenticate import RequestAuthentication


# class ReadTemplateClass(View):
#     def get(self, requests):
#         response_body = RequestAuthentication(
#             self.execute,
#             requests,
#             ["SUPER", "MANAGER", "COMPANY", "EMPLOYEE", "DEPARTMENT", "IMPLEMENTOR"]
#         ).execute()
#         return BuildResponse(response_body).get_response()
#
#     @staticmethod
#     def execute(request):
#         return EmployeeOnboardingResponse(None).build_parameter(request)
