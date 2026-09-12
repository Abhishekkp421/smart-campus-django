from django.shortcuts import redirect


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            not request.user.is_authenticated
            and not request.path.startswith("/students/login/")
            and not request.path.startswith("/students/logout/")
            and not request.path.startswith("/students/api/")
            and not request.path.startswith("/admin/")
        ):
            return redirect(f"/students/login/?next={request.path}")

        return self.get_response(request)