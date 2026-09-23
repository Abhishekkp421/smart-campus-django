from django.urls import resolve, Resolver404
from django.shortcuts import redirect
import re


class LoginRequiredMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        path = request.path

        # =========================
        # PUBLIC / SYSTEM PATHS
        # =========================

        if (
            path.startswith("/students/login/")
            or path.startswith("/students/logout/")
            or path.startswith("/students/api/")
            or path.startswith("/admin/")
        ):
            return self.get_response(request)

        # =========================
        # LOGIN REQUIRED
        # =========================

        if not request.user.is_authenticated:
            return redirect(
                f"/students/login/?next={path}"
            )

        # =========================
        # LET DJANGO HANDLE 404
        # =========================

        try:
            resolve(path)
        except Resolver404:
            return self.get_response(request)

        # =========================
        # ADMIN
        # =========================

        if request.user.is_staff:
            return self.get_response(request)

        # =========================
        # STUDENT
        # =========================

        if request.user.groups.filter(name="Student").exists():

            student_allowed_paths = [
                "/students/my-attendance/",
                "/students/my-results/",
                "/students/my-fees/",
                "/students/my-assignments/",
                "/students/my-notices/",
                "/students/my-events/",
                "/students/my-library/",
                "/students/student-settings/",
                "/students/student-change-password/",
                "/students/notifications/",
                "/students/my-timetable/",
                "/students/my-leaves/",
                "/students/apply-leave/",
                "/students/my-complaints/",
                "/students/create-complaint/",
            ]

            # Student dashboard
            if path == "/students/":
                return self.get_response(request)

            # Student allowed pages
            if any(
                path == allowed or path.startswith(allowed)
                for allowed in student_allowed_paths
            ):
                return self.get_response(request)

            # Assignment submission
            if re.match(
                r"^/students/assignments/\d+/submit/$",
                path
            ):
                return self.get_response(request)

            # Everything else
            return redirect("/students/")

        # =========================
        # FACULTY
        # =========================

        if request.user.groups.filter(name="Faculty").exists():

            faculty_allowed_paths = [
                "/students/faculty-attendance/",
                "/students/faculty-results/",
                "/students/faculty-assignments/",
                "/students/faculty-notices/",
                "/students/faculty-settings/",
                "/students/faculty-change-password/",
                "/students/faculty-events/",
                "/students/faculty-reports/",
                "/students/faculty-timetable/",
                "/students/faculty-leaves/",
                "/students/my-complaints/",
                "/students/create-complaint/",
                "/students/notifications/",
            ]

            # Faculty dashboard
            if path == "/students/":
                return self.get_response(request)

            # Faculty allowed pages
            if any(
                path == allowed or path.startswith(allowed)
                for allowed in faculty_allowed_paths
            ):
                return self.get_response(request)

            # Faculty assignment submissions
            if re.match(
                r"^/students/faculty-assignments/\d+/submissions/$",
                path
            ):
                return self.get_response(request)

            # Everything else
            return redirect("/students/")

        # =========================
        # UNKNOWN ROLE
        # =========================

        return redirect("/students/")