from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from . import views

from .api_views import (
    StudentListCreateAPIView,
    StudentDetailAPIView,
    FacultyListCreateAPIView,
    FacultyDetailAPIView,
    AttendanceListCreateAPIView,
    AttendanceDetailAPIView,
    ResultListCreateAPIView,
    ResultDetailAPIView,
    ExamListCreateAPIView,
    ExamDetailAPIView,
    AssignmentListCreateAPIView,
    AssignmentDetailAPIView,
    FeeListCreateAPIView,
    FeeDetailAPIView,
    NoticeListCreateAPIView,
    NoticeDetailAPIView,
    EventListCreateAPIView,
    EventDetailAPIView,
)

urlpatterns = [
    path("api/students/", StudentListCreateAPIView.as_view(), name="api-student-list"),
    path("api/students/<int:student_id>/", StudentDetailAPIView.as_view(), name="api-student-detail"),
    path("api/faculty/", FacultyListCreateAPIView.as_view(), name="api-faculty-list"),
    path("api/faculty/<int:faculty_id>/", FacultyDetailAPIView.as_view(), name="api-faculty-detail"),
    path("api/attendance/", AttendanceListCreateAPIView.as_view(), name="api-attendance-list"),
    path("api/attendance/<int:attendance_id>/", AttendanceDetailAPIView.as_view(), name="api-attendance-detail"),
    path("", views.dashboard, name="student-dashboard"),

    path("list/", views.student_list, name="student-list"),

    path("add/", views.add_student, name="add-student"),
    path("attendance/", views.attendance, name="attendance"),
    path("assignments/", views.assignment_list, name="assignment-list"),
    path("assignments/add/", views.add_assignment, name="add-assignment"),
    path("assignments/<int:assignment_id>/edit/", views.edit_assignment, name="edit-assignment"),
    path("assignments/<int:assignment_id>/delete/", views.delete_assignment, name="delete-assignment"),
    path("results/", views.result_list, name="result-list"),
    path("results/add/", views.add_result, name="add-result"),
    path("results/marksheet/", views.marksheet_list, name="marksheet-list"),
    path("results/<int:result_id>/edit/", views.edit_result, name="edit-result"),
    path("results/<int:result_id>/delete/", views.delete_result, name="delete-result"),
    path("attendance/history/", views.attendance_history, name="attendance-history"),
    path("exams/", views.exam_list, name="exam-list"),
    path("exams/add/", views.add_exam, name="add-exam"),
    path("exams/<int:exam_id>/edit/", views.edit_exam, name="edit-exam"),
    path("exams/<int:exam_id>/delete/", views.delete_exam, name="delete-exam"),
    path("faculty/", views.faculty_list, name="faculty-list"),
    path("faculty/add/", views.add_faculty, name="add-faculty"),
    path("fees/", views.fee_list, name="fee-list"),
    path("fees/<int:fee_id>/edit/", views.edit_fee, name="edit-fee"),
    path("fees/<int:fee_id>/delete/", views.delete_fee, name="delete-fee"),
    path("fees/add/", views.add_fee, name="add-fee"),
    path("notices/", views.notice_list, name="notice-list"),
    path("notices/add/", views.add_notice, name="add-notice"),
    path("notices/<int:notice_id>/edit/", views.edit_notice, name="edit-notice"),
    path("notices/<int:notice_id>/delete/", views.delete_notice, name="delete-notice"),
    path("events/", views.event_list, name="event-list"),
    path("events/add/", views.add_event, name="add-event"),
    path("events/<int:event_id>/edit/", views.edit_event, name="edit-event"),
    path("events/<int:event_id>/delete/", views.delete_event, name="delete-event"),
    path("library/", views.book_list, name="book-list"),
    path("library/add/", views.add_book, name="add-book"),
    path("library/<int:book_id>/edit/", views.edit_book, name="edit-book"),
    path("library/<int:book_id>/delete/", views.delete_book, name="delete-book"),
    path("library/issues/", views.book_issue_list, name="book-issue-list"),
    path("library/issues/add/", views.issue_book, name="issue-book"),
    path("library/issues/<int:issue_id>/return/", views.return_book, name="return-book"),
    path("reports/", views.reports, name="reports"),
    path("api/students/", views.student_api, name="student-api"),
    path(
    "api/results/",
    ResultListCreateAPIView.as_view(),
    name="api-result-list"
),
path(
    "api/fees/",
    FeeListCreateAPIView.as_view(),
    name="api-fee-list"
),

path(
    "api/fees/<int:fee_id>/",
    FeeDetailAPIView.as_view(),
    name="api-fee-detail"
),

path(
    "api/notices/",
    NoticeListCreateAPIView.as_view(),
    name="api-notice-list"
),

path(
    "api/notices/<int:notice_id>/",
    NoticeDetailAPIView.as_view(),
    name="api-notice-detail"
),
path(
    "settings/",
    views.settings_view,
    name="settings"
),
path(
    "login/",
    LoginView.as_view(template_name="registration/login.html"),
    name="login",
),

path(
    "logout/",
    LogoutView.as_view(),
    name="logout",
),

path(
    "api/events/",
    EventListCreateAPIView.as_view(),
    name="api-event-list"
),

path(
    "api/events/<int:event_id>/",
    EventDetailAPIView.as_view(),
    name="api-event-detail"
),

path(
    "api/results/<int:result_id>/",
    ResultDetailAPIView.as_view(),
    name="api-result-detail"
),

path(
    "api/exams/",
    ExamListCreateAPIView.as_view(),
    name="api-exam-list"
),

path(
    "api/exams/<int:exam_id>/",
    ExamDetailAPIView.as_view(),
    name="api-exam-detail"
),

path(
    "api/assignments/",
    AssignmentListCreateAPIView.as_view(),
    name="api-assignment-list"
),

path(
    "api/assignments/<int:assignment_id>/",
    AssignmentDetailAPIView.as_view(),
    name="api-assignment-detail"
),
    path(
    "faculty/<int:faculty_id>/edit/",
    views.edit_faculty,
    name="edit-faculty"
),
path(
    "faculty/<int:faculty_id>/delete/",
    views.delete_faculty,
    name="delete-faculty"
),
    path(
    "faculty/<int:faculty_id>/",
    views.faculty_detail,
    name="faculty-detail"
),


    path(
        "<int:student_id>/",
        views.student_detail,
        name="student-detail"
    ),

    path(
        "<int:student_id>/edit/",
        views.edit_student,
        name="edit-student"
    ),

    path(
        "<int:student_id>/delete/",
        views.delete_student,
        name="delete-student"
    ),
    path(
    "assignments/<int:assignment_id>/edit/",
    views.edit_assignment,
    name="edit-assignment"
),

path(
    "assignments/<int:assignment_id>/delete/",
    views.delete_assignment,
    name="delete-assignment"
),
path(
    "api/students/<int:student_id>/",
    views.student_detail_api,
    name="student-detail-api"
),
]