from django.contrib import admin

from .models import (
    Department,
    Course,
    Semester,
    Subject,
    Faculty,
    Student,
    Attendance,
    Exam,
    Result,
    Fee,
    Notice,
    Event,
    Book,
    BookIssue,

)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "description")
    search_fields = ("code", "name")
    ordering = ("code",)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "department", "duration_years")
    list_filter = ("department", "duration_years")
    search_fields = ("code", "name")
    ordering = ("code",)


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ("number", "name")
    list_filter = ("number",)
    ordering = ("number",)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "course",
        "semester",
        "credits",
    )

    list_filter = (
        "course",
        "semester",
        "credits",
    )

    search_fields = (
        "code",
        "name",
    )

    ordering = (
        "semester",
        "code",
    )


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = (
        "employee_id",
        "name",
        "email",
        "department",
        "designation",
    )

    list_filter = (
        "department",
        "designation",
    )

    search_fields = (
        "employee_id",
        "name",
        "email",
    )

    ordering = (
        "employee_id",
    )


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        "student_id",
        "name",
        "email",
        "course",
        "semester",
        "department",
        "admission_date",
    )

    list_filter = (
        "department",
        "course",
        "semester",
        "gender",
    )

    search_fields = (
        "student_id",
        "name",
        "email",
        "phone",
    )

    ordering = (
        "student_id",
    )


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "subject",
        "faculty",
        "date",
        "status",
    )

    list_filter = (
        "status",
        "date",
        "subject",
        "faculty",
    )

    search_fields = (
        "student__student_id",
        "student__name",
        "subject__code",
        "subject__name",
    )

    ordering = (
        "-date",
    )


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "exam_type",
        "course",
        "semester",
        "start_date",
        "end_date",
    )

    list_filter = (
        "exam_type",
        "course",
        "semester",
        "start_date",
    )

    search_fields = (
        "name",
        "course__code",
        "course__name",
    )

    ordering = (
        "-start_date",
    )
@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "exam",
        "subject",
        "marks_obtained",
        "max_marks",
    )

    list_filter = (
        "exam",
        "subject",
    )

    search_fields = (
        "student__student_id",
        "student__name",
        "exam__name",
        "subject__code",
        "subject__name",
    )

    ordering = (
        "exam",
        "student",
    )
@admin.register(Fee)
class FeeAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "fee_type",
        "amount",
        "paid_amount",
        "status",
        "due_date",
        "payment_date",
    )

    list_filter = (
        "status",
        "fee_type",
        "due_date",
    )

    search_fields = (
        "student__student_id",
        "student__name",
        "fee_type",
    )

    ordering = ("-due_date",)
@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "notice_type",
        "publish_date",
        "expiry_date",
        "is_active",
    )

    list_filter = (
        "notice_type",
        "is_active",
        "publish_date",
    )

    search_fields = (
        "title",
        "content",
    )

    ordering = ("-publish_date",)
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "event_type",
        "date",
        "time",
        "venue",
        "organizer",
    )

    list_filter = (
        "event_type",
        "date",
    )

    search_fields = (
        "title",
        "description",
        "venue",
        "organizer",
    )

    ordering = ("date", "time")
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "isbn",
        "category",
        "total_copies",
        "available_copies",
        "shelf_location",
    )

    search_fields = (
        "title",
        "author",
        "isbn",
    )

    list_filter = (
        "category",
    )


@admin.register(BookIssue)
class BookIssueAdmin(admin.ModelAdmin):
    list_display = (
        "book",
        "student",
        "issue_date",
        "due_date",
        "return_date",
        "status",
    )

    search_fields = (
        "book__title",
        "student__name",
        "student__student_id",
    )

    list_filter = (
        "status",
        "issue_date",
        "due_date",
    )