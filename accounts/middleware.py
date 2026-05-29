from django.shortcuts import redirect
from django.urls import reverse


class RoleBasedRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.user.is_authenticated and request.path == reverse("accounts:login"):
            if request.user.is_unit_head():
                return redirect("dashboard:home")
            return redirect("patients:search")
