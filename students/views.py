from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash

from .forms import StudentForm,FacultyForm,StudentProfileForm,FacultyProfileForm,PasswordChangeForm,FacultySubjectMappingForm
from .models import Student, Faculty, Course, Department, Semester, Subject, Attendance,Exam,Result,Assignment,Fee,Notice,Event,Book,BookIssue,AssignmentSubmission,Notification,Timetable,LeaveRequest,Complaint
from django.utils.dateparse import parse_date

@login_required
def dashboard(request):

    # -------------------------------------------------
    # STUDENT DASHBOARD
    # -------------------------------------------------

    if request.user.groups.filter(name="Student").exists():

        student = request.user.student_profile

        context = {
            "student": student,
        }

        return render(
            request,
            "students/dashboard.html",
            context
        )

    # -------------------------------------------------
    # FACULTY DASHBOARD
    # -------------------------------------------------

    if request.user.groups.filter(name="Faculty").exists():

        faculty = request.user.faculty_profile

        total_my_assignments = Assignment.objects.filter(
            faculty=faculty
        ).count()

        total_attendance_records = Attendance.objects.filter(
            faculty=faculty
        ).count()

        recent_assignments = Assignment.objects.filter(
            faculty=faculty
        ).select_related(
            "subject"
        ).order_by("-created_at")[:5]

        context = {
            "faculty": faculty,
            "total_my_assignments": total_my_assignments,
            "total_attendance_records": total_attendance_records,
            "recent_assignments": recent_assignments,
        }

        return render(
            request,
            "students/dashboard.html",
            context
        )

    # -------------------------------------------------
    # ADMIN DASHBOARD
    # -------------------------------------------------

    total_students = Student.objects.count()
    total_faculty = Faculty.objects.count()
    total_courses = Course.objects.count()

    recent_students = Student.objects.order_by("-created_at")[:5]

    context = {
        "total_students": total_students,
        "total_faculty": total_faculty,
        "total_courses": total_courses,
        "recent_students": recent_students,
    }

    return render(
        request,
        "students/dashboard.html",
        context
    )
@login_required
def my_fees(request):

    if not request.user.groups.filter(name="Student").exists():
        return redirect("student-dashboard")


    student = request.user.student_profile
    fees = Fee.objects.filter(
       student=student
    ).order_by("-due_date")

    for fee in fees:
        fee.remaining_amount = fee.amount - fee.paid_amount

    total_fee = sum(
        fee.amount for fee in fees
    )

    paid_amount = sum(
        fee.paid_amount for fee in fees
    )

    remaining_amount = total_fee - paid_amount

    context = {
        "student": student,
        "fees": fees,
        "total_fee": total_fee,
        "paid_amount": paid_amount,
        "remaining_amount": remaining_amount,
    }

    return render(
        request,
        "students/my_fees.html",
        context
    )
@login_required
def my_assignments(request):

    if not request.user.groups.filter(name="Student").exists():
        return redirect("student-dashboard")


    student = request.user.student_profile

    assignments = Assignment.objects.filter(
        subject__course=student.course,
        subject__semester=student.semester
    ).select_related(
        "subject",
        "faculty"
    ).prefetch_related(
        "submissions"
    ).order_by("-due_date")

    for assignment in assignments:

        assignment.student_submission = (
            assignment.submissions.filter(
                student=student
            ).first()
        )

    context = {
        "student": student,
        "assignments": assignments,
    }

    return render(
        request,
        "students/my_assignments.html",
        context
    )
@login_required
def notifications(request):

    user_notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by("-created_at")

    unread_count = user_notifications.filter(
        is_read=False
    ).count()

    context = {
        "notifications": user_notifications,
        "unread_count": unread_count,
    }

    return render(
        request,
        "students/notifications.html",
        context
    )
@login_required
def mark_notification_read(request, notification_id):

    if request.method != "POST":
        return redirect("notifications")

    notification = get_object_or_404(
        Notification,
        id=notification_id,
        recipient=request.user
    )

    notification.is_read = True
    notification.save(
        update_fields=["is_read"]
    )

    return redirect("notifications")
@login_required
def submit_assignment(request, assignment_id):

    if not request.user.groups.filter(name="Student").exists():
        return redirect("student-dashboard")

    student = request.user.student_profile

    assignment = get_object_or_404(
        Assignment,
        id=assignment_id,
        subject__course=student.course,
        subject__semester=student.semester
    )

    submission = AssignmentSubmission.objects.filter(
        assignment=assignment,
        student=student
    ).first()

    if request.method == "POST":

        submission_file = request.FILES.get(
            "submission_file"
        )

        # =========================
        # FILE REQUIRED
        # =========================

        if not submission_file:

            return render(
                request,
                "students/submit_assignment.html",
                {
                    "student": student,
                    "assignment": assignment,
                    "submission": submission,
                    "error": "Please select a file to upload.",
                }
            )
                # =========================
        # DUE DATE VALIDATION
        # =========================

        if timezone.now().date() > assignment.due_date:

            return render(
                request,
                "students/submit_assignment.html",
                {
                    "student": student,
                    "assignment": assignment,
                    "submission": submission,
                    "error": (
                        "Submission deadline has passed. "
                        "You can no longer submit this assignment."
                    ),
                }
            )
        # =========================
        # FILE SIZE VALIDATION
        # Maximum 5 MB
        # =========================

        max_file_size = 5 * 1024 * 1024

        if submission_file.size > max_file_size:

            return render(
                request,
                "students/submit_assignment.html",
                {
                    "student": student,
                    "assignment": assignment,
                    "submission": submission,
                    "error": "File size must not exceed 5 MB.",
                }
            )

        # =========================
        # FILE TYPE VALIDATION
        # =========================

        allowed_extensions = [
            ".pdf",
            ".doc",
            ".docx",
        ]

        allowed_content_types = [
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ]

        file_name = submission_file.name.lower()

        file_extension = ""

        if "." in file_name:
            file_extension = "." + file_name.rsplit(".", 1)[1]

        # Extension check
        if file_extension not in allowed_extensions:

            return render(
                request,
                "students/submit_assignment.html",
                {
                    "student": student,
                    "assignment": assignment,
                    "submission": submission,
                    "error": (
                        "Invalid file type. "
                        "Only PDF, DOC and DOCX files are allowed."
                    ),
                }
            )

        # MIME type check
        if submission_file.content_type not in allowed_content_types:

            return render(
                request,
                "students/submit_assignment.html",
                {
                    "student": student,
                    "assignment": assignment,
                    "submission": submission,
                    "error": (
                        "Invalid file format. "
                        "Please upload a valid PDF, DOC or DOCX file."
                    ),
                }
            )

        # =========================
        # SAVE / UPDATE SUBMISSION
        # =========================

        if submission:

            submission.submission_file = submission_file
            submission.submitted_at = timezone.now()
            submission.marks_obtained = None
            submission.feedback = ""
            submission.status = "Submitted"

            submission.save()

        else:

            AssignmentSubmission.objects.create(
                assignment=assignment,
                student=student,
                submission_file=submission_file,
                status="Submitted"
            )

        # =========================
        # FACULTY NOTIFICATION
        # =========================

        if assignment.faculty and assignment.faculty.user:

            Notification.objects.create(
                recipient=assignment.faculty.user,
                title="New Assignment Submission",
                message=(
                    f"{student.name} has submitted "
                    f"the assignment '{assignment.title}'."
                )
            )

        return redirect("my-assignments")

    return render(
        request,
        "students/submit_assignment.html",
        {
            "student": student,
            "assignment": assignment,
            "submission": submission,
        }
    )
@login_required
def student_list(request):
    if not request.user.is_staff:
        return redirect("student-dashboard")

    students = Student.objects.select_related(
        "department",
        "course",
        "semester"
    ).order_by("-created_at")

    search_query = request.GET.get("search", "").strip()
    department_filter = request.GET.get("department", "")
    course_filter = request.GET.get("course", "")

    if search_query:
        students = students.filter(
            Q(student_id__icontains=search_query)
            | Q(name__icontains=search_query)
            | Q(email__icontains=search_query)
            | Q(phone__icontains=search_query)
        )

    if department_filter:
        students = students.filter(
            department_id=department_filter
        )

    if course_filter:
        students = students.filter(
            course_id=course_filter
        )

    paginator = Paginator(students, 5)
    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    departments = Department.objects.all().order_by("name")
    courses = Course.objects.all().order_by("name")

    context = {
        "page_obj": page_obj,
        "departments": departments,
        "courses": courses,
        "search_query": search_query,
        "department_filter": department_filter,
        "course_filter": course_filter,
    }

    return render(
        request,
        "students/student_list.html",
        context
    )
@login_required
def student_detail(request, student_id):
    if not request.user.is_staff:
        return redirect("student-dashboard")

    student = get_object_or_404(
        Student.objects.select_related(
            "department",
            "course",
            "semester"
        ),
        id=student_id
    )

    return render(
        request,
        "students/student_detail.html",
        {"student": student}
    )
@login_required
def my_notices(request):

    if not request.user.groups.filter(name="Student").exists():
        return redirect("student-dashboard")

    notices = Notice.objects.all().order_by("-created_at")

    context = {
        "notices": notices,
    }

    return render(
        request,
        "students/my_notices.html",
        context
    )
@login_required
def my_events(request):

    if not request.user.groups.filter(name="Student").exists():
        return redirect("student-dashboard")


    events = Event.objects.all().order_by("date", "time")

    context = {
        "events": events,
    }

    return render(
        request,
        "students/my_events.html",
        context
    )
@login_required
def my_library(request):

    if not request.user.groups.filter(name="Student").exists():
        return redirect("student-dashboard")


    student = request.user.student_profile

    books = Book.objects.all().order_by("title")

    issued_books = BookIssue.objects.filter(
        student=student
    ).select_related(
        "book"
    ).order_by("-issue_date")

    context = {
        "student": student,
        "books": books,
        "issued_books": issued_books,
    }

    return render(
        request,
        "students/my_library.html",
        context
    )
@login_required
def student_settings(request):

    if not request.user.groups.filter(name="Student").exists():
        return redirect("student-dashboard")


    student = request.user.student_profile

    if request.method == "POST":

        form = StudentProfileForm(
            request.POST,
            instance=student
        )

        if form.is_valid():

            form.save()

            return redirect("student-settings")

    else:

        form = StudentProfileForm(
            instance=student
        )

    context = {
        "student": student,
        "form": form,
    }

    return render(
        request,
        "students/student_settings.html",
        context
    )
@login_required
def student_change_password(request):

    if not request.user.groups.filter(name="Student").exists():
        return redirect("student-dashboard")


    if request.method == "POST":

        form = PasswordChangeForm(
            user=request.user,
            data=request.POST
        )

        if form.is_valid():

            user = form.save()

            update_session_auth_hash(
                request,
                user
            )

            return redirect("student-settings")

    else:

        form = PasswordChangeForm(
            user=request.user
        )

    context = {
        "form": form,
    }

    return render(
        request,
        "students/student_change_password.html",
        context
    )
@login_required
def faculty_settings(request):

    if not request.user.groups.filter(name="Faculty").exists():
        return redirect("student-dashboard")


    faculty = request.user.faculty_profile

    if request.method == "POST":

        form = FacultyProfileForm(
            request.POST,
            instance=faculty
        )

        if form.is_valid():
            form.save()
            return redirect("faculty-settings")

    else:

        form = FacultyProfileForm(
            instance=faculty
        )

    context = {
        "faculty": faculty,
        "form": form,
    }

    return render(
        request,
        "students/faculty_settings.html",
        context
    )
@login_required
def faculty_change_password(request):

    if not request.user.groups.filter(name="Faculty").exists():
        return redirect("student-dashboard")


    if request.method == "POST":

        form = PasswordChangeForm(
            user=request.user,
            data=request.POST
        )

        if form.is_valid():

            user = form.save()

            update_session_auth_hash(
                request,
                user
            )

            return redirect("faculty-settings")

    else:

        form = PasswordChangeForm(
            user=request.user
        )

    context = {
        "form": form,
    }

    return render(
        request,
        "students/faculty_change_password.html",
        context
    )
@login_required
def edit_student(request, student_id):
    if not request.user.is_staff:
        return redirect("student-dashboard")

    student = get_object_or_404(Student, id=student_id)

    if request.method == "POST":
        form = StudentForm(request.POST, instance=student)

        if form.is_valid():
            form.save()
            return redirect(
                "student-detail",
                student_id=student.id
            )

    else:
        form = StudentForm(instance=student)

    return render(
        request,
        "students/edit_student.html",
        {
            "form": form,
            "student": student
        }
    )

@login_required
def delete_student(request, student_id):
    if not request.user.is_staff:
        return redirect("student-dashboard")

    student = get_object_or_404(Student, id=student_id)

    if request.method == "POST":
        student.delete()
        return redirect("student-list")

    return render(
        request,
        "students/delete_student.html",
        {"student": student}
    )
@login_required
def add_student(request):
    if not request.user.is_staff:
        return redirect("student-dashboard")


    if request.method == "POST":
        form = StudentForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("student-dashboard")

    else:
        form = StudentForm()

    return render(
        request,
        "students/add_student.html",
        {"form": form}
    )
@login_required
def faculty_list(request):
    if not request.user.is_staff:
        return redirect("student-dashboard")

    faculties = Faculty.objects.select_related(
        "department"
    ).order_by("employee_id")

    search_query = request.GET.get("search", "").strip()
    department_filter = request.GET.get("department", "")

    if search_query:
        faculties = faculties.filter(
            Q(employee_id__icontains=search_query)
            | Q(name__icontains=search_query)
            | Q(email__icontains=search_query)
            | Q(phone__icontains=search_query)
            | Q(designation__icontains=search_query)
        )

    if department_filter:
        faculties = faculties.filter(
            department_id=department_filter
        )

    departments = Department.objects.all().order_by("name")

    context = {
        "faculties": faculties,
        "departments": departments,
        "search_query": search_query,
        "department_filter": department_filter,
    }

    return render(
        request,
        "students/faculty_list.html",
        context
    )
@login_required
def faculty_detail(request, faculty_id):
    if not request.user.is_staff:
        return redirect("student-dashboard")

    faculty = get_object_or_404(
        Faculty.objects.select_related("department"),
        id=faculty_id
    )

    return render(
        request,
        "students/faculty_detail.html",
        {"faculty": faculty}
    )
@login_required
def edit_faculty(request, faculty_id):
    if not request.user.is_staff:
        return redirect("student-dashboard")

    faculty = get_object_or_404(Faculty, id=faculty_id)

    if request.method == "POST":
        form = FacultyForm(request.POST, instance=faculty)

        if form.is_valid():
            form.save()
            return redirect(
                "faculty-detail",
                faculty_id=faculty.id
            )

    else:
        form = FacultyForm(instance=faculty)

    return render(
        request,
        "students/edit_faculty.html",
        {
            "form": form,
            "faculty": faculty
        }
    )
@login_required
def delete_faculty(request, faculty_id):
    if not request.user.is_staff:
        return redirect("student-dashboard")

    faculty = get_object_or_404(Faculty, id=faculty_id)

    if request.method == "POST":
        faculty.delete()
        return redirect("faculty-list")

    return render(
        request,
        "students/delete_faculty.html",
        {"faculty": faculty}
    )
@login_required
def add_faculty(request):
    if not request.user.is_staff:
        return redirect("student-dashboard")

    if request.method == "POST":
        form = FacultyForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("faculty-list")

    else:
        form = FacultyForm()

    return render(
        request,
        "students/add_faculty.html",
        {"form": form}
    )
@login_required
def attendance(request):
    if not request.user.is_staff:
        return redirect("student-dashboard")


    courses = Course.objects.all().order_by("name")
    semesters = Semester.objects.all().order_by("number")
    subjects = Subject.objects.all().order_by("code")
    faculties = Faculty.objects.all().order_by("employee_id")

    # =========================
    # SAVE ATTENDANCE
    # =========================
    if request.method == "POST":

        selected_date = request.POST.get("date", "").strip()
        selected_course = request.POST.get("course", "").strip()
        selected_semester = request.POST.get("semester", "").strip()
        selected_subject = request.POST.get("subject", "").strip()
        selected_faculty = request.POST.get("faculty", "").strip()

        attendance_date = parse_date(selected_date)

        # Validate required fields
        if not attendance_date:
            error = "Please select a valid date."

            return render(
                request,
                "students/attendance.html",
                {
                    "courses": courses,
                    "semesters": semesters,
                    "subjects": subjects,
                    "faculties": faculties,
                    "students": Student.objects.none(),
                    "selected_date": selected_date,
                    "selected_course": selected_course,
                    "selected_semester": selected_semester,
                    "selected_subject": selected_subject,
                    "selected_faculty": selected_faculty,
                    "error": error,
                }
            )

        if not (
            selected_course
            and selected_semester
            and selected_subject
            and selected_faculty
        ):
            error = "Please select Course, Semester, Subject and Faculty."

            return render(
                request,
                "students/attendance.html",
                {
                    "courses": courses,
                    "semesters": semesters,
                    "subjects": subjects,
                    "faculties": faculties,
                    "students": Student.objects.none(),
                    "selected_date": selected_date,
                    "selected_course": selected_course,
                    "selected_semester": selected_semester,
                    "selected_subject": selected_subject,
                    "selected_faculty": selected_faculty,
                    "error": error,
                }
            )

        students = Student.objects.filter(
            course_id=selected_course,
            semester_id=selected_semester
        ).order_by("student_id")

        subject = get_object_or_404(
            Subject,
            id=selected_subject
        )

        faculty = get_object_or_404(
            Faculty,
            id=selected_faculty
        )

        # Save attendance for every student
        for student in students:

            status = request.POST.get(
                f"student_{student.id}",
                "Present"
            )

            Attendance.objects.update_or_create(
                student=student,
                subject=subject,
                date=attendance_date,
                defaults={
                    "faculty": faculty,
                    "status": status,
                }
            )

        # IMPORTANT:
        # Redirect with all selected values
        return redirect(
            f"/students/attendance/"
            f"?date={selected_date}"
            f"&course={selected_course}"
            f"&semester={selected_semester}"
            f"&subject={selected_subject}"
            f"&faculty={selected_faculty}"
        )

    # =========================
    # LOAD ATTENDANCE
    # =========================

    selected_date = request.GET.get("date", "").strip()
    selected_course = request.GET.get("course", "").strip()
    selected_semester = request.GET.get("semester", "").strip()
    selected_subject = request.GET.get("subject", "").strip()
    selected_faculty = request.GET.get("faculty", "").strip()

    students = Student.objects.none()

    if (
        selected_course
        and selected_semester
        and selected_subject
        and selected_faculty
    ):

        students = Student.objects.filter(
            course_id=selected_course,
            semester_id=selected_semester
        ).order_by("student_id")

        attendance_date = parse_date(selected_date)

        if attendance_date:

            attendance_records = Attendance.objects.filter(
                student__in=students,
                subject_id=selected_subject,
                date=attendance_date
            )

            attendance_map = {
                record.student_id: record.status
                for record in attendance_records
            }

            for student in students:
                student.attendance_status = attendance_map.get(
                    student.id,
                    "Present"
                )

    context = {
        "courses": courses,
        "semesters": semesters,
        "subjects": subjects,
        "faculties": faculties,
        "students": students,
        "selected_date": selected_date,
        "selected_course": selected_course,
        "selected_semester": selected_semester,
        "selected_subject": selected_subject,
        "selected_faculty": selected_faculty,
    }

    return render(
        request,
        "students/attendance.html",
        context
    )
@login_required
def faculty_attendance(request):

    if not request.user.groups.filter(name="Faculty").exists():
        return redirect("student-dashboard")


    faculty = request.user.faculty_profile

    # -----------------------------------------
    # ONLY SUBJECTS ASSIGNED TO THIS FACULTY
    # -----------------------------------------

    faculty_subjects = faculty.subjects.all().order_by("code")

    # -----------------------------------------
    # SAVE ATTENDANCE
    # -----------------------------------------

    if request.method == "POST":

        selected_date = request.POST.get(
            "date",
            ""
        ).strip()

        selected_subject = request.POST.get(
            "subject",
            ""
        ).strip()

        attendance_date = parse_date(
            selected_date
        )

        # Validate date
        if not attendance_date:

            return render(
                request,
                "students/faculty_attendance.html",
                {
                    "faculty": faculty,
                    "subjects": faculty_subjects,
                    "students": Student.objects.none(),
                    "selected_date": selected_date,
                    "selected_subject": selected_subject,
                    "error": "Please select a valid date.",
                }
            )

        # Validate subject
        if not selected_subject:

            return render(
                request,
                "students/faculty_attendance.html",
                {
                    "faculty": faculty,
                    "subjects": faculty_subjects,
                    "students": Student.objects.none(),
                    "selected_date": selected_date,
                    "selected_subject": selected_subject,
                    "error": "Please select a subject.",
                }
            )

        # -----------------------------------------
        # SECURITY CHECK
        # Faculty can access ONLY mapped subjects
        # -----------------------------------------

        subject = get_object_or_404(
            faculty_subjects,
            id=selected_subject
        )

        # -----------------------------------------
        # GET STUDENTS
        # Students must belong to subject's
        # course and semester
        # -----------------------------------------

        students = Student.objects.filter(
            course=subject.course,
            semester=subject.semester
        ).order_by(
            "student_id"
        )

        # -----------------------------------------
        # SAVE ATTENDANCE
        # -----------------------------------------

        for student in students:

            status = request.POST.get(
                f"student_{student.id}",
                "Present"
            )

            Attendance.objects.update_or_create(
                student=student,
                subject=subject,
                date=attendance_date,
                defaults={
                    "faculty": faculty,
                    "status": status,
                }
            )
        # =========================================
        # LOW ATTENDANCE ALERT
        # =========================================

        for student in students:

            total_classes = Attendance.objects.filter(
                student=student,
                subject=subject
            ).count()

            present_classes = Attendance.objects.filter(
                student=student,
                subject=subject,
                status="Present"
            ).count()

            if total_classes == 0 or not student.user:
                continue

            attendance_percentage = (
                present_classes / total_classes
            ) * 100

            if attendance_percentage < 75:

                # Avoid duplicate unread notifications
                existing_notification = Notification.objects.filter(
                    recipient=student.user,
                    title="Low Attendance Alert",
                    is_read=False
                ).first()

                if not existing_notification:
                    Notification.objects.create(
                        recipient=student.user,
                        title="Low Attendance Alert",
                        message=(
                            f"Your current attendance in {subject.code} is "
                            f"{attendance_percentage:.2f}%. "
                            f"Please maintain at least 75% attendance."
                        )
                    )
        # -----------------------------------------
        # REDIRECT AFTER SAVE
        # -----------------------------------------

        return redirect(
            f"/students/faculty-attendance/"
            f"?date={selected_date}"
            f"&subject={selected_subject}"
        )

    # -----------------------------------------
    # LOAD ATTENDANCE
    # -----------------------------------------

    selected_date = request.GET.get(
        "date",
        ""
    ).strip()

    selected_subject = request.GET.get(
        "subject",
        ""
    ).strip()

    students = Student.objects.none()

    # -----------------------------------------
    # LOAD STUDENTS FOR SELECTED SUBJECT
    # -----------------------------------------

    if selected_date and selected_subject:

        attendance_date = parse_date(
            selected_date
        )

        if attendance_date:

            subject = faculty_subjects.filter(
                id=selected_subject
            ).first()

            if subject:

                students = Student.objects.filter(
                    course=subject.course,
                    semester=subject.semester
                ).order_by(
                    "student_id"
                )

                # Existing attendance
                attendance_records = Attendance.objects.filter(
                    student__in=students,
                    subject=subject,
                    date=attendance_date,
                    faculty=faculty
                )

                attendance_map = {
                    record.student_id: record.status
                    for record in attendance_records
                }

                # Attach status to students
                for student in students:

                    student.attendance_status = (
                        attendance_map.get(
                            student.id,
                            "Present"
                        )
                    )

    # -----------------------------------------
    # CONTEXT
    # -----------------------------------------

    context = {
        "faculty": faculty,
        "subjects": faculty_subjects,
        "students": students,
        "selected_date": selected_date,
        "selected_subject": selected_subject,
    }

    return render(
        request,
        "students/faculty_attendance.html",
        context
    )
@login_required
def faculty_results(request):

    if not request.user.groups.filter(name="Faculty").exists():
        return redirect("student-dashboard")


    faculty = request.user.faculty_profile

    # ONLY SUBJECTS ASSIGNED TO THIS FACULTY
    faculty_subjects = faculty.subjects.all().order_by("code")

    exams = Exam.objects.select_related(
        "course",
        "semester"
    ).order_by("-start_date")

    # =========================
    # SAVE RESULTS
    # =========================

    if request.method == "POST":

        selected_exam = request.POST.get(
            "exam",
            ""
        ).strip()

        selected_subject = request.POST.get(
            "subject",
            ""
        ).strip()

        max_marks_input = request.POST.get(
            "max_marks",
            ""
        ).strip()

        # Required fields
        if not selected_exam or not selected_subject or not max_marks_input:

            return render(
                request,
                "students/faculty_results.html",
                {
                    "faculty": faculty,
                    "subjects": faculty_subjects,
                    "exams": exams,
                    "students": Student.objects.none(),
                    "selected_exam": selected_exam,
                    "selected_subject": selected_subject,
                    "max_marks": max_marks_input,
                    "error": "Please fill all fields.",
                }
            )

        # Validate maximum marks
        try:
            max_marks = float(max_marks_input)

        except ValueError:

            return render(
                request,
                "students/faculty_results.html",
                {
                    "faculty": faculty,
                    "subjects": faculty_subjects,
                    "exams": exams,
                    "students": Student.objects.none(),
                    "selected_exam": selected_exam,
                    "selected_subject": selected_subject,
                    "max_marks": max_marks_input,
                    "error": "Maximum marks must be a valid number.",
                }
            )

        if max_marks <= 0:

            return render(
                request,
                "students/faculty_results.html",
                {
                    "faculty": faculty,
                    "subjects": faculty_subjects,
                    "exams": exams,
                    "students": Student.objects.none(),
                    "selected_exam": selected_exam,
                    "selected_subject": selected_subject,
                    "max_marks": max_marks_input,
                    "error": "Maximum marks must be greater than 0.",
                }
            )

        # Get selected exam
        exam = get_object_or_404(
            Exam,
            id=selected_exam
        )

        # Get only faculty's subject
        subject = get_object_or_404(
            faculty_subjects,
            id=selected_subject
        )

        # Exam and subject must belong to same course/semester
        if (
            exam.course_id != subject.course_id
            or exam.semester_id != subject.semester_id
        ):

            return render(
                request,
                "students/faculty_results.html",
                {
                    "faculty": faculty,
                    "subjects": faculty_subjects,
                    "exams": exams,
                    "students": Student.objects.none(),
                    "selected_exam": selected_exam,
                    "selected_subject": selected_subject,
                    "max_marks": max_marks,
                    "error": "Selected exam does not match the subject course and semester.",
                }
            )

        # Load students of this subject
        students = Student.objects.filter(
            course=subject.course,
            semester=subject.semester
        ).order_by("student_id")

        # =========================
        # SAVE EACH STUDENT RESULT
        # =========================

        for student in students:

            marks = request.POST.get(
                f"marks_{student.id}",
                ""
            ).strip()

            # Blank marks = skip
            if marks == "":
                continue

            try:
                marks = float(marks)

            except ValueError:
                continue

            # Invalid marks = skip
            if marks < 0 or marks > max_marks:
                continue

            Result.objects.update_or_create(
                student=student,
                exam=exam,
                subject=subject,
                defaults={
                    "marks_obtained": marks,
                    "max_marks": max_marks,
                }
            )

        # Redirect after saving
        return redirect(
            f"/students/faculty-results/"
            f"?exam={selected_exam}"
            f"&subject={selected_subject}"
            f"&max_marks={max_marks}"
        )


    # =========================
    # LOAD RESULTS
    # =========================

    selected_exam = request.GET.get(
        "exam",
        ""
    ).strip()

    selected_subject = request.GET.get(
        "subject",
        ""
    ).strip()

    max_marks = request.GET.get(
        "max_marks",
        ""
    ).strip()

    students = Student.objects.none()

    if selected_exam and selected_subject:

        exam = exams.filter(
            id=selected_exam
        ).first()

        subject = faculty_subjects.filter(
            id=selected_subject
        ).first()

        if exam and subject:

            # Check course and semester
            if (
                exam.course_id == subject.course_id
                and exam.semester_id == subject.semester_id
            ):

                students = Student.objects.filter(
                    course=subject.course,
                    semester=subject.semester
                ).order_by("student_id")

                # Existing results
                results = Result.objects.filter(
                    student__in=students,
                    exam=exam,
                    subject=subject
                )

                result_map = {
                    result.student_id: result.marks_obtained
                    for result in results
                }

                # If maximum marks not present in URL,
                # get it from existing Result
                if not max_marks and results.exists():

                    max_marks = str(
                        results.first().max_marks
                    )

                # Attach marks to students
                for student in students:

                    student.result_marks = result_map.get(
                        student.id,
                        ""
                    )

    context = {
        "faculty": faculty,
        "subjects": faculty_subjects,
        "exams": exams,
        "students": students,
        "selected_exam": selected_exam,
        "selected_subject": selected_subject,
        "max_marks": max_marks,
    }

    return render(
        request,
        "students/faculty_results.html",
        context
    )
# =========================
# FACULTY ASSIGNMENTS
# =========================

@login_required
def faculty_assignments(request):

    if not request.user.groups.filter(name="Faculty").exists():
        return redirect("student-dashboard")


    faculty = request.user.faculty_profile

    # ONLY SUBJECTS ASSIGNED TO THIS FACULTY
    faculty_subjects = faculty.subjects.all().order_by("code")

    # Faculty ke existing assignments
    assignments = Assignment.objects.filter(
        faculty=faculty
    ).select_related(
        "subject"
    ).order_by("-due_date")

    # =========================
    # CREATE ASSIGNMENT
    # =========================

    if request.method == "POST":

        title = request.POST.get(
            "title",
            ""
        ).strip()

        description = request.POST.get(
            "description",
            ""
        ).strip()

        subject_id = request.POST.get(
            "subject",
            ""
        ).strip()

        due_date = request.POST.get(
            "due_date",
            ""
        ).strip()

        max_marks = request.POST.get(
            "max_marks",
            ""
        ).strip()

        # Required fields
        if not all([
            title,
            subject_id,
            due_date,
            max_marks
        ]):

            return render(
                request,
                "students/faculty_assignments.html",
                {
                    "faculty": faculty,
                    "assignments": assignments,
                    "subjects": faculty_subjects,
                    "error": "Please fill all required fields.",
                }
            )

        # =========================
        # SECURITY CHECK
        # =========================

        subject = faculty_subjects.filter(
            id=subject_id
        ).first()

        if not subject:

            return render(
                request,
                "students/faculty_assignments.html",
                {
                    "faculty": faculty,
                    "assignments": assignments,
                    "subjects": faculty_subjects,
                    "error": "You are not allowed to create an assignment for this subject.",
                }
            )

        # Validate date
        due = parse_date(due_date)

        if not due:

            return render(
                request,
                "students/faculty_assignments.html",
                {
                    "faculty": faculty,
                    "assignments": assignments,
                    "subjects": faculty_subjects,
                    "error": "Please enter a valid due date.",
                }
            )

        # Validate marks
        try:
            max_marks = int(max_marks)

        except ValueError:

            return render(
                request,
                "students/faculty_assignments.html",
                {
                    "faculty": faculty,
                    "assignments": assignments,
                    "subjects": faculty_subjects,
                    "error": "Maximum marks must be a valid number.",
                }
            )

        if max_marks <= 0:

            return render(
                request,
                "students/faculty_assignments.html",
                {
                    "faculty": faculty,
                    "assignments": assignments,
                    "subjects": faculty_subjects,
                    "error": "Maximum marks must be greater than 0.",
                }
            )

        # =========================
        # CREATE
        # =========================

        Assignment.objects.create(
            title=title,
            description=description,
            subject=subject,
            faculty=faculty,
            due_date=due,
            max_marks=max_marks
        )

        return redirect("faculty-assignments")

    # =========================
    # CONTEXT
    # =========================

    context = {
        "faculty": faculty,
        "assignments": assignments,
        "subjects": faculty_subjects,
    }

    return render(
        request,
        "students/faculty_assignments.html",
        context
    )
@login_required
def faculty_assignment_submissions(request, assignment_id):

    if not request.user.groups.filter(name="Faculty").exists():
        return redirect("student-dashboard")


    faculty = request.user.faculty_profile

    # Faculty sirf apna assignment access kar sakta hai
    assignment = get_object_or_404(
        Assignment,
        id=assignment_id,
        faculty=faculty
    )

    submissions = AssignmentSubmission.objects.filter(
        assignment=assignment
    ).select_related(
        "student"
    ).order_by(
        "-submitted_at"
    )

    # =========================
    # EVALUATE SUBMISSION
    # =========================

    if request.method == "POST":

        submission_id = request.POST.get(
            "submission_id",
            ""
        ).strip()

        marks_input = request.POST.get(
            "marks",
            ""
        ).strip()

        feedback = request.POST.get(
            "feedback",
            ""
        ).strip()

        submission = get_object_or_404(
            AssignmentSubmission,
            id=submission_id,
            assignment=assignment
        )

        # Validate marks
        try:
            marks = float(marks_input)

        except ValueError:

            return render(
                request,
                "students/faculty_assignment_submissions.html",
                {
                    "faculty": faculty,
                    "assignment": assignment,
                    "submissions": submissions,
                    "error": "Marks must be a valid number.",
                }
            )

        if marks < 0 or marks > assignment.max_marks:

            return render(
                request,
                "students/faculty_assignment_submissions.html",
                {
                    "faculty": faculty,
                    "assignment": assignment,
                    "submissions": submissions,
                    "error": (
                        f"Marks must be between "
                        f"0 and {assignment.max_marks}."
                    ),
                }
            )

        submission.marks_obtained = marks
        submission.feedback = feedback
        submission.status = "Evaluated"

        submission.save()
        Notification.objects.create(
            recipient=submission.student.user,
            title="Assignment Evaluated",
            message=(
                f"Your assignment '{assignment.title}' "
                f"has been evaluated. "
                f"Marks: {marks}/{assignment.max_marks}."
            )
        )
        return redirect(
            "faculty-assignment-submissions",
            assignment_id=assignment.id
        )

    context = {
        "faculty": faculty,
        "assignment": assignment,
        "submissions": submissions,
    }

    return render(
        request,
        "students/faculty_assignment_submissions.html",
        context
    )
@login_required
def faculty_edit_assignment(request, assignment_id):

    if not request.user.groups.filter(name="Faculty").exists():
        return redirect("student-dashboard")


    faculty = request.user.faculty_profile

    # IMPORTANT:
    # Faculty sirf apna assignment edit kar sakta hai
    assignment = get_object_or_404(
        Assignment,
        id=assignment_id,
        faculty=faculty
    )

    faculty_subjects = faculty.subjects.all().order_by("code")

    if request.method == "POST":

        title = request.POST.get(
            "title",
            ""
        ).strip()

        description = request.POST.get(
            "description",
            ""
        ).strip()

        subject_id = request.POST.get(
            "subject",
            ""
        ).strip()

        due_date = request.POST.get(
            "due_date",
            ""
        ).strip()

        max_marks = request.POST.get(
            "max_marks",
            ""
        ).strip()

        if not all([
            title,
            subject_id,
            due_date,
            max_marks
        ]):

            return render(
                request,
                "students/faculty_edit_assignment.html",
                {
                    "faculty": faculty,
                    "assignment": assignment,
                    "subjects": faculty_subjects,
                    "error": "Please fill all required fields.",
                }
            )

        subject = faculty_subjects.filter(
            id=subject_id
        ).first()

        if not subject:

            return render(
                request,
                "students/faculty_edit_assignment.html",
                {
                    "faculty": faculty,
                    "assignment": assignment,
                    "subjects": faculty_subjects,
                    "error": "You are not allowed to use this subject.",
                }
            )

        due = parse_date(due_date)

        if not due:

            return render(
                request,
                "students/faculty_edit_assignment.html",
                {
                    "faculty": faculty,
                    "assignment": assignment,
                    "subjects": faculty_subjects,
                    "error": "Please enter a valid due date.",
                }
            )

        try:

            max_marks = int(max_marks)

        except ValueError:

            return render(
                request,
                "students/faculty_edit_assignment.html",
                {
                    "faculty": faculty,
                    "assignment": assignment,
                    "subjects": faculty_subjects,
                    "error": "Maximum marks must be a valid number.",
                }
            )

        if max_marks <= 0:

            return render(
                request,
                "students/faculty_edit_assignment.html",
                {
                    "faculty": faculty,
                    "assignment": assignment,
                    "subjects": faculty_subjects,
                    "error": "Maximum marks must be greater than 0.",
                }
            )

        assignment.title = title
        assignment.description = description
        assignment.subject = subject
        assignment.due_date = due
        assignment.max_marks = max_marks

        assignment.save()

        return redirect("faculty-assignments")

    return render(
        request,
        "students/faculty_edit_assignment.html",
        {
            "faculty": faculty,
            "assignment": assignment,
            "subjects": faculty_subjects,
        }
    )


@login_required
def faculty_delete_assignment(request, assignment_id):

    if not request.user.groups.filter(name="Faculty").exists():
        return redirect("student-dashboard")


    faculty = request.user.faculty_profile

    # Faculty sirf apna assignment delete kar sakta hai
    assignment = get_object_or_404(
        Assignment,
        id=assignment_id,
        faculty=faculty
    )

    if request.method == "POST":

        assignment.delete()

        return redirect(
            "faculty-assignments"
        )

    return render(
        request,
        "students/faculty_delete_assignment.html",
        {
            "faculty": faculty,
            "assignment": assignment,
        }
    )
# =========================
# FACULTY NOTICES
# =========================

@login_required
def faculty_notices(request):

    if not request.user.groups.filter(name="Faculty").exists():
        return redirect("student-dashboard")


    faculty = request.user.faculty_profile

    # Sirf current faculty ke notices
    notices = Notice.objects.filter(
        faculty=faculty
    ).order_by("-publish_date", "-created_at")

    if request.method == "POST":

        title = request.POST.get(
            "title",
            ""
        ).strip()

        content = request.POST.get(
            "content",
            ""
        ).strip()

        notice_type = request.POST.get(
            "notice_type",
            "General"
        ).strip()

        publish_date = request.POST.get(
            "publish_date",
            ""
        ).strip()

        expiry_date = request.POST.get(
            "expiry_date",
            ""
        ).strip()

        is_active = request.POST.get(
            "is_active"
        ) == "on"

        # Required fields
        if not title or not content or not publish_date:

            return render(
                request,
                "students/faculty_notices.html",
                {
                    "faculty": faculty,
                    "notices": notices,
                    "notice_types": Notice._meta.get_field(
                        "notice_type"
                    ).choices,
                    "error": "Please fill all required fields.",
                }
            )

        publish = parse_date(publish_date)

        if not publish:

            return render(
                request,
                "students/faculty_notices.html",
                {
                    "faculty": faculty,
                    "notices": notices,
                    "notice_types": Notice._meta.get_field(
                        "notice_type"
                    ).choices,
                    "error": "Please enter a valid publish date.",
                }
            )

        expiry = None

        if expiry_date:
            expiry = parse_date(expiry_date)

            if not expiry:

                return render(
                    request,
                    "students/faculty_notices.html",
                    {
                        "faculty": faculty,
                        "notices": notices,
                        "notice_types": Notice._meta.get_field(
                            "notice_type"
                        ).choices,
                        "error": "Please enter a valid expiry date.",
                    }
                )

            if expiry < publish:

                return render(
                    request,
                    "students/faculty_notices.html",
                    {
                        "faculty": faculty,
                        "notices": notices,
                        "notice_types": Notice._meta.get_field(
                            "notice_type"
                        ).choices,
                        "error": "Expiry date cannot be before publish date.",
                    }
                )

        # Create notice for current faculty
        Notice.objects.create(
            title=title,
            content=content,
            faculty=faculty,
            notice_type=notice_type,
            publish_date=publish,
            expiry_date=expiry,
            is_active=is_active,
        )

        return redirect("faculty-notices")

    context = {
        "faculty": faculty,
        "notices": notices,
        "notice_types": Notice._meta.get_field(
            "notice_type"
        ).choices,
    }

    return render(
        request,
        "students/faculty_notices.html",
        context
    )


@login_required
def faculty_edit_notice(request, notice_id):

    if not request.user.groups.filter(name="Faculty").exists():
        return redirect("student-dashboard")


    faculty = request.user.faculty_profile

    # Faculty sirf apna notice edit kar sakta hai
    notice = get_object_or_404(
        Notice,
        id=notice_id,
        faculty=faculty
    )

    notice_types = Notice._meta.get_field(
        "notice_type"
    ).choices

    if request.method == "POST":

        title = request.POST.get(
            "title",
            ""
        ).strip()

        content = request.POST.get(
            "content",
            ""
        ).strip()

        notice_type = request.POST.get(
            "notice_type",
            "General"
        ).strip()

        publish_date = request.POST.get(
            "publish_date",
            ""
        ).strip()

        expiry_date = request.POST.get(
            "expiry_date",
            ""
        ).strip()

        is_active = request.POST.get(
            "is_active"
        ) == "on"

        if not title or not content or not publish_date:

            return render(
                request,
                "students/faculty_edit_notice.html",
                {
                    "faculty": faculty,
                    "notice": notice,
                    "notice_types": notice_types,
                    "error": "Please fill all required fields.",
                }
            )

        publish = parse_date(publish_date)

        if not publish:

            return render(
                request,
                "students/faculty_edit_notice.html",
                {
                    "faculty": faculty,
                    "notice": notice,
                    "notice_types": notice_types,
                    "error": "Please enter a valid publish date.",
                }
            )

        expiry = None

        if expiry_date:

            expiry = parse_date(expiry_date)

            if not expiry:

                return render(
                    request,
                    "students/faculty_edit_notice.html",
                    {
                        "faculty": faculty,
                        "notice": notice,
                        "notice_types": notice_types,
                        "error": "Please enter a valid expiry date.",
                    }
                )

            if expiry < publish:

                return render(
                    request,
                    "students/faculty_edit_notice.html",
                    {
                        "faculty": faculty,
                        "notice": notice,
                        "notice_types": notice_types,
                        "error": "Expiry date cannot be before publish date.",
                    }
                )

        notice.title = title
        notice.content = content
        notice.notice_type = notice_type
        notice.publish_date = publish
        notice.expiry_date = expiry
        notice.is_active = is_active

        notice.save()

        return redirect("faculty-notices")

    return render(
        request,
        "students/faculty_edit_notice.html",
        {
            "faculty": faculty,
            "notice": notice,
            "notice_types": notice_types,
        }
    )


@login_required
def faculty_delete_notice(request, notice_id):

    if not request.user.groups.filter(name="Faculty").exists():
        return redirect("student-dashboard")


    faculty = request.user.faculty_profile

    # Faculty sirf apna notice delete kar sakta hai
    notice = get_object_or_404(
        Notice,
        id=notice_id,
        faculty=faculty
    )

    if request.method == "POST":

        notice.delete()

        return redirect(
            "faculty-notices"
        )

    return render(
        request,
        "students/faculty_delete_notice.html",
        {
            "faculty": faculty,
            "notice": notice,
        }
    )
@login_required
def faculty_events(request):

    if not request.user.groups.filter(name="Faculty").exists():
        return redirect("student-dashboard")


    faculty = request.user.faculty_profile

    events = Event.objects.filter(
        organizer=faculty
    ).order_by("-date", "-time")

    context = {
        "faculty": faculty,
        "events": events,
    }

    return render(
        request,
        "students/faculty_events.html",
        context
    )


@login_required
def faculty_add_event(request):

    if not request.user.groups.filter(name="Faculty").exists():
        return redirect("student-dashboard")


    faculty = request.user.faculty_profile

    if request.method == "POST":

        title = request.POST.get("title")
        description = request.POST.get("description")
        event_type = request.POST.get("event_type")
        date = request.POST.get("date")
        time = request.POST.get("time")
        venue = request.POST.get("venue")

        Event.objects.create(
            title=title,
            description=description,
            event_type=event_type,
            date=date,
            time=time,
            venue=venue,
            organizer=faculty
        )

        return redirect("faculty-events")

    return render(
        request,
        "students/faculty_event_form.html",
        {
            "faculty": faculty,
        }
    )


@login_required
def faculty_edit_event(request, event_id):

    if not request.user.groups.filter(name="Faculty").exists():
        return redirect("student-dashboard")


    faculty = request.user.faculty_profile

    event = get_object_or_404(
        Event,
        id=event_id,
        organizer=faculty
    )

    if request.method == "POST":

        event.title = request.POST.get("title")
        event.description = request.POST.get("description")
        event.event_type = request.POST.get("event_type")
        event.date = request.POST.get("date")
        event.time = request.POST.get("time")
        event.venue = request.POST.get("venue")

        event.save()

        return redirect("faculty-events")

    return render(
        request,
        "students/faculty_event_form.html",
        {
            "faculty": faculty,
            "event": event,
        }
    )


@login_required
def faculty_delete_event(request, event_id):

    if not request.user.groups.filter(name="Faculty").exists():
        return redirect("student-dashboard")


    faculty = request.user.faculty_profile

    event = get_object_or_404(
        Event,
        id=event_id,
        organizer=faculty
    )

    if request.method == "POST":
        event.delete()

    return redirect("faculty-events")
@login_required
def my_attendance(request):

    if not request.user.groups.filter(name="Student").exists():
        return redirect("student-dashboard")


    student = request.user.student_profile

    records = Attendance.objects.filter(
        student=student
    ).select_related(
        "subject",
        "faculty"
    ).order_by("-date")

    total_classes = records.count()

    present_classes = records.filter(
        status="Present"
    ).count()

    absent_classes = records.filter(
        status="Absent"
    ).count()

    if total_classes > 0:
        attendance_percentage = round(
            (present_classes / total_classes) * 100,
            2
        )
    else:
        attendance_percentage = 0

    context = {
        "student": student,
        "records": records,
        "total_classes": total_classes,
        "present_classes": present_classes,
        "absent_classes": absent_classes,
        "attendance_percentage": attendance_percentage,
    }

    return render(
        request,
        "students/my_attendance.html",
        context
    )
@login_required
def attendance_history(request):
    if not request.user.is_staff:
        return redirect("student-dashboard")


    records = Attendance.objects.select_related(
        "student",
        "subject",
        "faculty"
    ).order_by("-date", "student__student_id")

    selected_date = request.GET.get("date", "").strip()
    selected_subject = request.GET.get("subject", "").strip()
    selected_faculty = request.GET.get("faculty", "").strip()

    if selected_date:
        attendance_date = parse_date(selected_date)

        if attendance_date:
            records = records.filter(date=attendance_date)

    if selected_subject:
        records = records.filter(subject_id=selected_subject)

    if selected_faculty:
        records = records.filter(faculty_id=selected_faculty)

    subjects = Subject.objects.all().order_by("code")
    faculties = Faculty.objects.all().order_by("employee_id")

    context = {
        "records": records,
        "subjects": subjects,
        "faculties": faculties,
        "selected_date": selected_date,
        "selected_subject": selected_subject,
        "selected_faculty": selected_faculty,
    }

    return render(
        request,
        "students/attendance_history.html",
        context
    )
@login_required
def exam_list(request):
    if not request.user.is_staff:
        return redirect("student-dashboard")


    exams = Exam.objects.select_related(
        "course",
        "semester"
    ).order_by("-start_date")

    search_query = request.GET.get("search", "").strip()
    exam_type_filter = request.GET.get("exam_type", "")
    course_filter = request.GET.get("course", "")
    semester_filter = request.GET.get("semester", "")

    if search_query:
        exams = exams.filter(
            Q(name__icontains=search_query)
            | Q(course__code__icontains=search_query)
            | Q(course__name__icontains=search_query)
        )

    if exam_type_filter:
        exams = exams.filter(
            exam_type=exam_type_filter
        )

    if course_filter:
        exams = exams.filter(
            course_id=course_filter
        )

    if semester_filter:
        exams = exams.filter(
            semester_id=semester_filter
        )

    courses = Course.objects.all().order_by("name")
    semesters = Semester.objects.all().order_by("number")

    context = {
        "exams": exams,
        "courses": courses,
        "semesters": semesters,
        "search_query": search_query,
        "exam_type_filter": exam_type_filter,
        "course_filter": course_filter,
        "semester_filter": semester_filter,
        "exam_types": Exam.EXAM_TYPE_CHOICES,
    }

    return render(
        request,
        "students/exam_list.html",
        context
    )

@login_required
def add_exam(request):
    if not request.user.is_staff:
        return redirect("student-dashboard")


    courses = Course.objects.all().order_by("name")
    semesters = Semester.objects.all().order_by("number")

    if request.method == "POST":

        name = request.POST.get("name", "").strip()
        exam_type = request.POST.get("exam_type", "").strip()
        course_id = request.POST.get("course", "").strip()
        semester_id = request.POST.get("semester", "").strip()
        start_date = request.POST.get("start_date", "").strip()
        end_date = request.POST.get("end_date", "").strip()

        if not all([
            name,
            exam_type,
            course_id,
            semester_id,
            start_date,
            end_date
        ]):
            error = "Please fill all fields."

            return render(
                request,
                "students/add_exam.html",
                {
                    "courses": courses,
                    "semesters": semesters,
                    "exam_types": Exam.EXAM_TYPE_CHOICES,
                    "error": error,
                }
            )

        start = parse_date(start_date)
        end = parse_date(end_date)

        if not start or not end:
            error = "Please enter valid dates."

            return render(
                request,
                "students/add_exam.html",
                {
                    "courses": courses,
                    "semesters": semesters,
                    "exam_types": Exam.EXAM_TYPE_CHOICES,
                    "error": error,
                }
            )

        if end < start:
            error = "End date cannot be before start date."

            return render(
                request,
                "students/add_exam.html",
                {
                    "courses": courses,
                    "semesters": semesters,
                    "exam_types": Exam.EXAM_TYPE_CHOICES,
                    "error": error,
                }
            )

        Exam.objects.create(
            name=name,
            exam_type=exam_type,
            course_id=course_id,
            semester_id=semester_id,
            start_date=start,
            end_date=end,
        )

        return redirect("exam-list")

    return render(
        request,
        "students/add_exam.html",
        {
            "courses": courses,
            "semesters": semesters,
            "exam_types": Exam.EXAM_TYPE_CHOICES,
        }
    )

@login_required
def edit_exam(request, exam_id):
    if not request.user.is_staff:
        return redirect("student-dashboard")


    exam = get_object_or_404(Exam, id=exam_id)

    courses = Course.objects.all().order_by("name")
    semesters = Semester.objects.all().order_by("number")

    if request.method == "POST":

        name = request.POST.get("name", "").strip()
        exam_type = request.POST.get("exam_type", "").strip()
        course_id = request.POST.get("course", "").strip()
        semester_id = request.POST.get("semester", "").strip()
        start_date = request.POST.get("start_date", "").strip()
        end_date = request.POST.get("end_date", "").strip()

        start = parse_date(start_date)
        end = parse_date(end_date)

        if not all([
            name,
            exam_type,
            course_id,
            semester_id,
            start,
            end
        ]):
            error = "Please fill all fields."

            return render(
                request,
                "students/edit_exam.html",
                {
                    "exam": exam,
                    "courses": courses,
                    "semesters": semesters,
                    "exam_types": Exam.EXAM_TYPE_CHOICES,
                    "error": error,
                }
            )

        if end < start:
            error = "End date cannot be before start date."

            return render(
                request,
                "students/edit_exam.html",
                {
                    "exam": exam,
                    "courses": courses,
                    "semesters": semesters,
                    "exam_types": Exam.EXAM_TYPE_CHOICES,
                    "error": error,
                }
            )

        exam.name = name
        exam.exam_type = exam_type
        exam.course_id = course_id
        exam.semester_id = semester_id
        exam.start_date = start
        exam.end_date = end

        exam.save()

        return redirect(
            "exam-list"
        )

    return render(
        request,
        "students/edit_exam.html",
        {
            "exam": exam,
            "courses": courses,
            "semesters": semesters,
            "exam_types": Exam.EXAM_TYPE_CHOICES,
        }
    )

@login_required
def delete_exam(request, exam_id):
    if not request.user.is_staff:
        return redirect("student-dashboard")


    exam = get_object_or_404(
        Exam,
        id=exam_id
    )

    if request.method == "POST":
        exam.delete()
        return redirect("exam-list")

    return render(
        request,
        "students/delete_exam.html",
        {
            "exam": exam
        }
    )
@login_required
def my_results(request):

    if not request.user.groups.filter(name="Student").exists():
        return redirect("student-dashboard")


    student = request.user.student_profile

    results = Result.objects.filter(
        student=student
    ).select_related(
        "exam",
        "subject"
    ).order_by("-exam__start_date", "subject__code")

    total_marks = sum(
        result.max_marks for result in results
    )

    obtained_marks = sum(
        result.marks_obtained for result in results
    )

    if total_marks > 0:
        percentage = round(
            (obtained_marks / total_marks) * 100,
            2
        )
    else:
        percentage = 0

    context = {
        "student": student,
        "results": results,
        "total_marks": total_marks,
        "obtained_marks": obtained_marks,
        "percentage": percentage,
    }

    return render(
        request,
        "students/my_results.html",
        context
    )
@login_required
def result_list(request):
    if not request.user.is_staff:
        return redirect("student-dashboard")


    results = Result.objects.select_related(
        "student",
        "exam",
        "subject"
    ).order_by("-id")

    search_query = request.GET.get("search", "").strip()
    subject_filter = request.GET.get("subject", "")
    exam_filter = request.GET.get("exam", "")

    if search_query:
        results = results.filter(
            Q(student__student_id__icontains=search_query)
            | Q(student__name__icontains=search_query)
            | Q(exam__name__icontains=search_query)
            | Q(subject__code__icontains=search_query)
            | Q(subject__name__icontains=search_query)
        )

    if subject_filter:
        results = results.filter(
            subject_id=subject_filter
        )

    if exam_filter:
        results = results.filter(
            exam_id=exam_filter
        )

    subjects = Subject.objects.all().order_by("code")
    exams = Exam.objects.select_related(
        "course",
        "semester"
    ).order_by("-start_date")

    context = {
        "results": results,
        "subjects": subjects,
        "exams": exams,
        "search_query": search_query,
        "subject_filter": subject_filter,
        "exam_filter": exam_filter,
    }

    return render(
        request,
        "students/result_list.html",
        context
    )

@login_required
def add_result(request):
    if not request.user.is_staff:
        return redirect("student-dashboard")


    students = Student.objects.select_related(
        "course",
        "semester"
    ).order_by("student_id")

    exams = Exam.objects.select_related(
        "course",
        "semester"
    ).order_by("-start_date")

    subjects = Subject.objects.all().order_by("code")

    if request.method == "POST":

        student_id = request.POST.get("student", "").strip()
        exam_id = request.POST.get("exam", "").strip()
        subject_id = request.POST.get("subject", "").strip()
        marks_obtained = request.POST.get("marks_obtained", "").strip()
        max_marks = request.POST.get("max_marks", "").strip()

        if not all([
            student_id,
            exam_id,
            subject_id,
            marks_obtained,
            max_marks
        ]):
            error = "Please fill all fields."

            return render(
                request,
                "students/add_result.html",
                {
                    "students": students,
                    "exams": exams,
                    "subjects": subjects,
                    "error": error,
                }
            )

        try:
            marks_obtained = float(marks_obtained)
            max_marks = float(max_marks)
        except ValueError:

            return render(
                request,
                "students/add_result.html",
                {
                    "students": students,
                    "exams": exams,
                    "subjects": subjects,
                    "error": "Marks must be valid numbers.",
                }
            )

        if marks_obtained < 0 or max_marks <= 0:
            return render(
                request,
                "students/add_result.html",
                {
                    "students": students,
                    "exams": exams,
                    "subjects": subjects,
                    "error": "Please enter valid marks.",
                }
            )

        if marks_obtained > max_marks:
            return render(
                request,
                "students/add_result.html",
                {
                    "students": students,
                    "exams": exams,
                    "subjects": subjects,
                    "error": "Marks obtained cannot exceed maximum marks.",
                }
            )

        Result.objects.create(
            student_id=student_id,
            exam_id=exam_id,
            subject_id=subject_id,
            marks_obtained=marks_obtained,
            max_marks=max_marks,
        )

        return redirect("result-list")

    return render(
        request,
        "students/add_result.html",
        {
            "students": students,
            "exams": exams,
            "subjects": subjects,
        }
    )

@login_required
def edit_result(request, result_id):
    if not request.user.is_staff:
        return redirect("student-dashboard")


    result = get_object_or_404(
        Result,
        id=result_id
    )

    students = Student.objects.select_related(
        "course",
        "semester"
    ).order_by("student_id")

    exams = Exam.objects.select_related(
        "course",
        "semester"
    ).order_by("-start_date")

    subjects = Subject.objects.all().order_by("code")

    if request.method == "POST":

        student_id = request.POST.get("student", "").strip()
        exam_id = request.POST.get("exam", "").strip()
        subject_id = request.POST.get("subject", "").strip()
        marks_obtained = request.POST.get("marks_obtained", "").strip()
        max_marks = request.POST.get("max_marks", "").strip()

        if not all([
            student_id,
            exam_id,
            subject_id,
            marks_obtained,
            max_marks
        ]):
            error = "Please fill all fields."

            return render(
                request,
                "students/edit_result.html",
                {
                    "result": result,
                    "students": students,
                    "exams": exams,
                    "subjects": subjects,
                    "error": error,
                }
            )

        try:
            marks_obtained = float(marks_obtained)
            max_marks = float(max_marks)
        except ValueError:

            return render(
                request,
                "students/edit_result.html",
                {
                    "result": result,
                    "students": students,
                    "exams": exams,
                    "subjects": subjects,
                    "error": "Marks must be valid numbers.",
                }
            )

        if marks_obtained < 0 or max_marks <= 0:
            error = "Please enter valid marks."

            return render(
                request,
                "students/edit_result.html",
                {
                    "result": result,
                    "students": students,
                    "exams": exams,
                    "subjects": subjects,
                    "error": error,
                }
            )

        if marks_obtained > max_marks:
            error = "Marks obtained cannot exceed maximum marks."

            return render(
                request,
                "students/edit_result.html",
                {
                    "result": result,
                    "students": students,
                    "exams": exams,
                    "subjects": subjects,
                    "error": error,
                }
            )

        result.student_id = student_id
        result.exam_id = exam_id
        result.subject_id = subject_id
        result.marks_obtained = marks_obtained
        result.max_marks = max_marks

        result.save()

        return redirect("result-list")

    return render(
        request,
        "students/edit_result.html",
        {
            "result": result,
            "students": students,
            "exams": exams,
            "subjects": subjects,
        }
    )

@login_required
def delete_result(request, result_id):
    if not request.user.is_staff:
        return redirect("student-dashboard")


    result = get_object_or_404(
        Result,
        id=result_id
    )

    if request.method == "POST":
        result.delete()
        return redirect("result-list")

    return render(
        request,
        "students/delete_result.html",
        {
            "result": result
        }
    )
@login_required
def marksheet_list(request):
    if not request.user.is_staff:
        return redirect("student-dashboard")


    students = Student.objects.all().order_by("student_id")
    exams = Exam.objects.all().order_by("-start_date")

    student_filter = request.GET.get("student")
    exam_filter = request.GET.get("exam")

    results = []
    total_marks = 0
    obtained_marks = 0
    percentage = None

    selected_student = None
    selected_exam = None

    if student_filter and exam_filter:

        selected_student = get_object_or_404(Student, id=student_filter)
        selected_exam = get_object_or_404(Exam, id=exam_filter)

        results = Result.objects.filter(
            student_id=student_filter,
            exam_id=exam_filter
        ).select_related("subject")

        obtained_marks = sum(r.marks_obtained for r in results)
        total_marks = sum(r.max_marks for r in results)

        if total_marks > 0:
            percentage = round((obtained_marks / total_marks) * 100, 2)

    context = {
        "students": students,
        "exams": exams,
        "results": results,
        "selected_student": selected_student,
        "selected_exam": selected_exam,
        "obtained_marks": obtained_marks,
        "total_marks": total_marks,
        "percentage": percentage,
    }

    return render(
        request,
        "students/marksheet_list.html",
        context
    )
# =========================
# ASSIGNMENTS
# =========================

@login_required
def assignment_list(request):

    if not request.user.is_staff:
        return redirect("student-dashboard")


    assignments = Assignment.objects.select_related(
        "subject",
        "faculty"
    ).order_by("-due_date")

    search_query = request.GET.get("search", "").strip()
    subject_filter = request.GET.get("subject", "")

    if search_query:
        assignments = assignments.filter(
            Q(title__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(subject__name__icontains=search_query)
            | Q(subject__code__icontains=search_query)
        )

    if subject_filter:
        assignments = assignments.filter(
            subject_id=subject_filter
        )

    subjects = Subject.objects.all().order_by("code")

    context = {
        "assignments": assignments,
        "subjects": subjects,
        "search_query": search_query,
        "subject_filter": subject_filter,
    }

    return render(
        request,
        "students/assignment_list.html",
        context
    )


@login_required
def add_assignment(request):

    if not request.user.is_staff:
        return redirect("student-dashboard")


    subjects = Subject.objects.all().order_by("code")
    faculties = Faculty.objects.all().order_by("employee_id")

    if request.method == "POST":

        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        subject_id = request.POST.get("subject", "").strip()
        faculty_id = request.POST.get("faculty", "").strip()
        due_date = request.POST.get("due_date", "").strip()
        max_marks = request.POST.get("max_marks", "").strip()

        if not all([
            title,
            subject_id,
            due_date,
            max_marks
        ]):
            error = "Please fill all required fields."

            return render(
                request,
                "students/add_assignment.html",
                {
                    "subjects": subjects,
                    "faculties": faculties,
                    "error": error,
                }
            )

        due = parse_date(due_date)

        if not due:
            error = "Please enter a valid due date."

            return render(
                request,
                "students/add_assignment.html",
                {
                    "subjects": subjects,
                    "faculties": faculties,
                    "error": error,
                }
            )

        try:
            max_marks = int(max_marks)
        except ValueError:

            return render(
                request,
                "students/add_assignment.html",
                {
                    "subjects": subjects,
                    "faculties": faculties,
                    "error": "Maximum marks must be a valid number.",
                }
            )

        if max_marks <= 0:

            return render(
                request,
                "students/add_assignment.html",
                {
                    "subjects": subjects,
                    "faculties": faculties,
                    "error": "Maximum marks must be greater than 0.",
                }
            )

        Assignment.objects.create(
            title=title,
            description=description,
            subject_id=subject_id,
            faculty_id=faculty_id if faculty_id else None,
            due_date=due,
            max_marks=max_marks,
        )

        return redirect("assignment-list")

    return render(
        request,
        "students/add_assignment.html",
        {
            "subjects": subjects,
            "faculties": faculties,
        }
    )


@login_required
def edit_assignment(request, assignment_id):

    if not request.user.is_staff:
        return redirect("student-dashboard")


    assignment = get_object_or_404(
        Assignment,
        id=assignment_id
    )

    subjects = Subject.objects.all().order_by("code")
    faculties = Faculty.objects.all().order_by("employee_id")

    if request.method == "POST":

        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        subject_id = request.POST.get("subject", "").strip()
        faculty_id = request.POST.get("faculty", "").strip()
        due_date = request.POST.get("due_date", "").strip()
        max_marks = request.POST.get("max_marks", "").strip()

        due = parse_date(due_date)

        if not all([
            title,
            subject_id,
            due,
            max_marks
        ]):
            error = "Please fill all required fields."

            return render(
                request,
                "students/edit_assignment.html",
                {
                    "assignment": assignment,
                    "subjects": subjects,
                    "faculties": faculties,
                    "error": error,
                }
            )

        try:
            max_marks = int(max_marks)
        except ValueError:

            return render(
                request,
                "students/edit_assignment.html",
                {
                    "assignment": assignment,
                    "subjects": subjects,
                    "faculties": faculties,
                    "error": "Maximum marks must be a valid number.",
                }
            )

        if max_marks <= 0:

            return render(
                request,
                "students/edit_assignment.html",
                {
                    "assignment": assignment,
                    "subjects": subjects,
                    "faculties": faculties,
                    "error": "Maximum marks must be greater than 0.",
                }
            )

        assignment.title = title
        assignment.description = description
        assignment.subject_id = subject_id
        assignment.faculty_id = faculty_id if faculty_id else None
        assignment.due_date = due
        assignment.max_marks = max_marks

        assignment.save()

        return redirect("assignment-list")

    return render(
        request,
        "students/edit_assignment.html",
        {
            "assignment": assignment,
            "subjects": subjects,
            "faculties": faculties,
        }
    )


@login_required
def delete_assignment(request, assignment_id):

    if not request.user.is_staff:
        return redirect("student-dashboard")


    assignment = get_object_or_404(
        Assignment,
        id=assignment_id
    )

    if request.method == "POST":
        assignment.delete()
        return redirect("assignment-list")

    return render(
        request,
        "students/delete_assignment.html",
        {
            "assignment": assignment
        }
    )
@login_required
def fee_list(request):

    if not request.user.is_staff:
        return redirect("student-dashboard")

    fees = Fee.objects.select_related("student").all()

    search = request.GET.get("search", "").strip()
    status = request.GET.get("status", "").strip()

    if search:
        fees = fees.filter(
            Q(student__student_id__icontains=search)
            | Q(student__name__icontains=search)
            | Q(fee_type__icontains=search)
        )

    if status:
        fees = fees.filter(status=status)

    context = {
        "fees": fees,
        "search": search,
        "selected_status": status,
    }

    return render(request, "students/fee_list.html", context)


@login_required
def add_fee(request):

    if not request.user.is_staff:
        return redirect("student-dashboard")

    students = Student.objects.all().order_by("student_id")

    if request.method == "POST":
        Fee.objects.create(
            student_id=request.POST.get("student"),
            fee_type=request.POST.get("fee_type"),
            amount=request.POST.get("amount"),
            paid_amount=request.POST.get("paid_amount") or 0,
            due_date=request.POST.get("due_date"),
            payment_date=request.POST.get("payment_date") or None,
            status=request.POST.get("status"),
            remarks=request.POST.get("remarks", ""),
        )

        return redirect("fee-list")

    return render(
        request,
        "students/add_fee.html",
        {"students": students}
    )


@login_required
def edit_fee(request, fee_id):

    if not request.user.is_staff:
        return redirect("student-dashboard")

    fee = get_object_or_404(Fee, id=fee_id)
    students = Student.objects.all().order_by("student_id")

    if request.method == "POST":
        fee.student_id = request.POST.get("student")
        fee.fee_type = request.POST.get("fee_type")
        fee.amount = request.POST.get("amount")
        fee.paid_amount = request.POST.get("paid_amount") or 0
        fee.due_date = request.POST.get("due_date")
        fee.payment_date = request.POST.get("payment_date") or None
        fee.status = request.POST.get("status")
        fee.remarks = request.POST.get("remarks", "")
        fee.save()

        return redirect("fee-list")

    return render(
        request,
        "students/edit_fee.html",
        {
            "fee": fee,
            "students": students,
        }
    )


@login_required
def delete_fee(request, fee_id):

    if not request.user.is_staff:
        return redirect("student-dashboard")

    fee = get_object_or_404(Fee, id=fee_id)

    if request.method == "POST":
        fee.delete()
        return redirect("fee-list")

    return render(
        request,
        "students/delete_fee.html",
        {"fee": fee}
    )
@login_required
def notice_list(request):

    if not request.user.is_staff:
        return redirect("student-dashboard")

    notices = Notice.objects.all()

    search = request.GET.get("search", "").strip()
    notice_type = request.GET.get("notice_type", "").strip()

    if search:
        notices = notices.filter(
            Q(title__icontains=search)
            | Q(content__icontains=search)
        )

    if notice_type:
        notices = notices.filter(notice_type=notice_type)

    context = {
        "notices": notices,
        "search": search,
        "selected_notice_type": notice_type,
    }

    return render(request, "students/notice_list.html", context)


@login_required
def add_notice(request):

    if not request.user.is_staff:
        return redirect("student-dashboard")

    if request.method == "POST":
        Notice.objects.create(
            title=request.POST.get("title"),
            content=request.POST.get("content"),
            notice_type=request.POST.get("notice_type"),
            publish_date=request.POST.get("publish_date"),
            expiry_date=request.POST.get("expiry_date") or None,
            is_active=request.POST.get("is_active") == "on",
        )

        return redirect("notice-list")

    return render(request, "students/add_notice.html")


@login_required
def edit_notice(request, notice_id):

    if not request.user.is_staff:
        return redirect("student-dashboard")

    notice = get_object_or_404(Notice, id=notice_id)

    if request.method == "POST":
        notice.title = request.POST.get("title")
        notice.content = request.POST.get("content")
        notice.notice_type = request.POST.get("notice_type")
        notice.publish_date = request.POST.get("publish_date")
        notice.expiry_date = request.POST.get("expiry_date") or None
        notice.is_active = request.POST.get("is_active") == "on"
        notice.save()

        return redirect("notice-list")

    return render(
        request,
        "students/edit_notice.html",
        {"notice": notice}
    )


@login_required
def delete_notice(request, notice_id):

    if not request.user.is_staff:
        return redirect("student-dashboard")

    notice = get_object_or_404(Notice, id=notice_id)

    if request.method == "POST":
        notice.delete()
        return redirect("notice-list")

    return render(
        request,
        "students/delete_notice.html",
        {"notice": notice}
    )
@login_required
def event_list(request):

    if not request.user.is_staff:
        return redirect("student-dashboard")

    events = Event.objects.all().order_by("date", "time")

    search = request.GET.get("search", "").strip()
    event_type = request.GET.get("event_type", "").strip()

    if search:
        events = events.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(venue__icontains=search) |
            Q(organizer__icontains=search)
        )

    if event_type:
        events = events.filter(event_type=event_type)

    event_types = Event.EVENT_TYPE_CHOICES

    context = {
        "events": events,
        "event_types": event_types,
        "search": search,
        "selected_event_type": event_type,
    }

    return render(request, "students/events.html", context)


@login_required
def add_event(request):

    if not request.user.is_staff:
        return redirect("student-dashboard")

    if request.method == "POST":
        Event.objects.create(
            title=request.POST.get("title"),
            description=request.POST.get("description"),
            event_type=request.POST.get("event_type"),
            date=request.POST.get("date"),
            time=request.POST.get("time"),
            venue=request.POST.get("venue"),
            organizer=request.POST.get("organizer"),
        )

        return redirect("event-list")

    return render(request, "students/add_event.html")


@login_required
def edit_event(request, event_id):

    if not request.user.is_staff:
        return redirect("student-dashboard")

    event = get_object_or_404(Event, id=event_id)

    if request.method == "POST":
        event.title = request.POST.get("title")
        event.description = request.POST.get("description")
        event.event_type = request.POST.get("event_type")
        event.date = request.POST.get("date")
        event.time = request.POST.get("time")
        event.venue = request.POST.get("venue")
        event.organizer = request.POST.get("organizer")
        event.save()

        return redirect("event-list")

    return render(
        request,
        "students/edit_event.html",
        {"event": event}
    )


@login_required
def delete_event(request, event_id):

    if not request.user.is_staff:
        return redirect("student-dashboard")

    event = get_object_or_404(Event, id=event_id)

    if request.method == "POST":
        event.delete()
        return redirect("event-list")

    return render(
        request,
        "students/delete_event.html",
        {"event": event}
    )
@login_required
def book_list(request):

    if not request.user.is_staff:
        return redirect("student-dashboard")


    books = Book.objects.all().order_by("title")

    search = request.GET.get("search", "").strip()
    category = request.GET.get("category", "").strip()

    if search:
        books = books.filter(
            Q(title__icontains=search) |
            Q(author__icontains=search) |
            Q(isbn__icontains=search)
        )

    if category:
        books = books.filter(category=category)

    categories = Book.CATEGORY_CHOICES

    total_books = Book.objects.count()

    total_copies = sum(
        book.total_copies
        for book in Book.objects.all()
    )

    available_copies = sum(
        book.available_copies
        for book in Book.objects.all()
    )

    issued_books = BookIssue.objects.filter(
        status="Issued"
    ).count()

    overdue_books = BookIssue.objects.filter(
        status="Overdue"
    ).count()

    context = {
        "books": books,
        "categories": categories,
        "search": search,
        "selected_category": category,

        "total_books": total_books,
        "total_copies": total_copies,
        "available_copies": available_copies,
        "issued_books": issued_books,
        "overdue_books": overdue_books,
    }

    return render(
        request,
        "students/book_list.html",
        context
    )


@login_required
def add_book(request):

    if not request.user.is_staff:
        return redirect("student-dashboard")


    if request.method == "POST":

        total_copies = int(
            request.POST.get("total_copies", 1)
        )

        Book.objects.create(
            title=request.POST.get("title"),
            author=request.POST.get("author"),
            isbn=request.POST.get("isbn"),
            category=request.POST.get("category"),
            publisher=request.POST.get("publisher"),
            total_copies=total_copies,
            available_copies=total_copies,
            shelf_location=request.POST.get("shelf_location"),
        )

        return redirect("book-list")

    return render(
        request,
        "students/add_book.html"
    )


@login_required
def edit_book(request, book_id):

    if not request.user.is_staff:
        return redirect("student-dashboard")


    book = get_object_or_404(
        Book,
        id=book_id
    )

    if request.method == "POST":

        book.title = request.POST.get("title")
        book.author = request.POST.get("author")
        book.isbn = request.POST.get("isbn")
        book.category = request.POST.get("category")
        book.publisher = request.POST.get("publisher")
        book.shelf_location = request.POST.get(
            "shelf_location"
        )

        new_total = int(
            request.POST.get(
                "total_copies",
                book.total_copies
            )
        )

        difference = (
            new_total - book.total_copies
        )

        book.total_copies = new_total

        book.available_copies = max(
            0,
            book.available_copies + difference
        )

        book.save()

        return redirect("book-list")

    return render(
        request,
        "students/edit_book.html",
        {"book": book}
    )


@login_required
def delete_book(request, book_id):

    if not request.user.is_staff:
        return redirect("student-dashboard")


    book = get_object_or_404(
        Book,
        id=book_id
    )

    if request.method == "POST":

        book.delete()

        return redirect("book-list")

    return render(
        request,
        "students/delete_book.html",
        {"book": book}
    )
@login_required
def book_issue_list(request):

    if not request.user.is_staff:
        return redirect("student-dashboard")


    issues = BookIssue.objects.select_related(
        "book",
        "student"
    ).order_by("-issue_date")

    search = request.GET.get("search", "").strip()
    status = request.GET.get("status", "").strip()

    if search:
        issues = issues.filter(
            Q(book__title__icontains=search) |
            Q(student__name__icontains=search) |
            Q(student__student_id__icontains=search)
        )

    if status:
        issues = issues.filter(status=status)

    context = {
        "issues": issues,
        "search": search,
        "selected_status": status,
    }

    return render(
        request,
        "students/book_issue_list.html",
        context
    )


@login_required
def issue_book(request):

    if not request.user.is_staff:
        return redirect("student-dashboard")


    if request.method == "POST":

        book_id = request.POST.get("book")
        student_id = request.POST.get("student")
        issue_date = request.POST.get("issue_date")
        due_date = request.POST.get("due_date")
        remarks = request.POST.get("remarks")

        book = get_object_or_404(
            Book,
            id=book_id
        )

        student = get_object_or_404(
            Student,
            id=student_id
        )

        if book.available_copies <= 0:
            return render(
                request,
                "students/issue_book.html",
                {
                    "books": Book.objects.all().order_by("title"),
                    "students": Student.objects.all().order_by("name"),
                    "error": "This book is currently not available."
                }
            )

        BookIssue.objects.create(
            book=book,
            student=student,
            issue_date=issue_date,
            due_date=due_date,
            remarks=remarks,
            status="Issued"
        )

        book.available_copies -= 1
        book.save()

        return redirect("book-issue-list")

    context = {
        "books": Book.objects.filter(
            available_copies__gt=0
        ).order_by("title"),

        "students": Student.objects.all().order_by("name"),
    }

    return render(
        request,
        "students/issue_book.html",
        context
    )


@login_required
def return_book(request, issue_id):

    if not request.user.is_staff:
        return redirect("student-dashboard")


    issue = get_object_or_404(
        BookIssue,
        id=issue_id
    )

    if request.method == "POST":

        if issue.status != "Returned":

            issue.return_date = request.POST.get(
                "return_date"
            )

            issue.status = "Returned"
            issue.save()

            issue.book.available_copies += 1

            if issue.book.available_copies > issue.book.total_copies:
                issue.book.available_copies = issue.book.total_copies

            issue.book.save()

        return redirect("book-issue-list")

    return render(
        request,
        "students/return_book.html",
        {"issue": issue}
    )
@login_required
def reports(request):

    if not request.user.is_staff:
        return redirect("student-dashboard")


    total_students = Student.objects.count()
    total_faculty = Faculty.objects.count()
    total_courses = Course.objects.count()
    total_subjects = Subject.objects.count()

    total_books = Book.objects.count()

    total_book_copies = sum(
        book.total_copies
        for book in Book.objects.all()
    )

    available_book_copies = sum(
        book.available_copies
        for book in Book.objects.all()
    )

    issued_books = BookIssue.objects.filter(
        status="Issued"
    ).count()

    returned_books = BookIssue.objects.filter(
        status="Returned"
    ).count()

    overdue_books = BookIssue.objects.filter(
        status="Overdue"
    ).count()

    total_fees = sum(
        fee.amount
        for fee in Fee.objects.all()
    )

    paid_fees = sum(
        fee.paid_amount
        for fee in Fee.objects.all()
    )

    pending_fees = total_fees - paid_fees
    if total_fees > 0:
      fee_collection_percentage = round(
        (paid_fees / total_fees) * 100,
        2
    )
    else:
      fee_collection_percentage = 0

    total_assignments = Assignment.objects.count()
    total_notices = Notice.objects.count()
    total_events = Event.objects.count()

    total_attendance = Attendance.objects.count()

    present_attendance = Attendance.objects.filter(
        status="Present"
    ).count()

    absent_attendance = Attendance.objects.filter(
        status="Absent"
    ).count()

    if total_attendance > 0:
        attendance_percentage = round(
            (present_attendance / total_attendance) * 100,
            2
        )
    else:
        attendance_percentage = 0

    total_results = Result.objects.count()

    total_marks_obtained = sum(
        result.marks_obtained
        for result in Result.objects.all()
    )

    total_max_marks = sum(
        result.max_marks
        for result in Result.objects.all()
    )

    if total_max_marks > 0:
        overall_result_percentage = round(
            (total_marks_obtained / total_max_marks) * 100,
            2
        )
    else:
        overall_result_percentage = 0
    department_stats = []

    for department in Department.objects.all().order_by("name"):

     student_count = Student.objects.filter(
        department=department
    ).count()

    department_stats.append({
        "name": department.name,
        "code": department.code,
        "student_count": student_count,
    })
    course_stats = []

    for course in Course.objects.all().order_by("name"):

     student_count = Student.objects.filter(
        course=course
    ).count()

    course_stats.append({
        "name": course.name,
        "code": course.code,
        "student_count": student_count,
    })
    student_performance = []

    for student in Student.objects.all().order_by("name"):

     results = Result.objects.filter(student=student)

    student_marks = sum(
        result.marks_obtained
        for result in results
    )

    student_max_marks = sum(
        result.max_marks
        for result in results
    )

    if student_max_marks > 0:
        student_percentage = round(
            (student_marks / student_max_marks) * 100,
            2
        )
    else:
        student_percentage = 0

    student_performance.append({
        "name": student.name,
        "student_id": student.student_id,
        "total_results": results.count(),
        "marks_obtained": student_marks,
        "max_marks": student_max_marks,
        "percentage": student_percentage,
    })
    context = {
        "total_students": total_students,
        "total_faculty": total_faculty,
        "total_courses": total_courses,
        "total_subjects": total_subjects,

        "total_books": total_books,
        "total_book_copies": total_book_copies,
        "available_book_copies": available_book_copies,
        "issued_books": issued_books,
        "returned_books": returned_books,
        "overdue_books": overdue_books,

        "total_fees": total_fees,
        "paid_fees": paid_fees,
        "pending_fees": pending_fees,

        "total_assignments": total_assignments,
        "total_notices": total_notices,
        "total_events": total_events,

        "total_attendance": total_attendance,
        "present_attendance": present_attendance,
        "absent_attendance": absent_attendance,
        "attendance_percentage": attendance_percentage,

        "total_results": total_results,
        "total_marks_obtained": total_marks_obtained,
        "total_max_marks": total_max_marks,
        "overall_result_percentage": overall_result_percentage,
        "fee_collection_percentage": fee_collection_percentage,
        "department_stats": department_stats,
        "course_stats": course_stats,
        "student_performance": student_performance,
    }

    return render(
        request,
        "students/reports.html",
        context
    )
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from .serializers import StudentSerializer
from .permissions import IsAdminOrFaculty


@api_view(["GET", "POST"])
@permission_classes([IsAdminOrFaculty])
def student_api(request):

    if request.method == "GET":

        students = Student.objects.all()

        serializer = StudentSerializer(
            students,
            many=True
        )

        return Response(serializer.data)

    elif request.method == "POST":

        serializer = StudentSerializer(
            data=request.data
        )

        if serializer.is_valid():

            serializer.save()

            return Response(
                serializer.data,
                status=201
            )

        return Response(
            serializer.errors,
            status=400
        )
@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAdminOrFaculty])
def student_detail_api(request, student_id):

    student = get_object_or_404(
        Student,
        id=student_id
    )

    if request.method == "GET":

        serializer = StudentSerializer(student)

        return Response(serializer.data)

    elif request.method in ["PUT", "PATCH"]:

        serializer = StudentSerializer(
            student,
            data=request.data,
            partial=(request.method == "PATCH")
        )

        if serializer.is_valid():

            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=400
        )

    elif request.method == "DELETE":

        student.delete()

        return Response(
            {"message": "Student deleted successfully."},
            status=204
        )
# =========================
# SETTINGS
# =========================

@login_required
def settings_view(request):

    if not request.user.is_staff:
        return redirect("student-dashboard")

    return render(
        request,
        "students/settings.html",
        {
            "user": request.user
        }
    )
@login_required
def faculty_reports(request):

    if not request.user.groups.filter(name="Faculty").exists():
        return redirect("student-dashboard")


    faculty = request.user.faculty_profile

    # Faculty ke attendance records
    attendance_records = Attendance.objects.filter(
        faculty=faculty
    ).select_related(
        "student",
        "subject"
    )

    # Faculty ke assignments
    assignments = Assignment.objects.filter(
        faculty=faculty
    ).select_related(
        "subject"
    )

    # Faculty ke subjects
    subject_ids = set(
        attendance_records.values_list(
            "subject_id",
            flat=True
        )
    )

    assignment_subject_ids = set(
        assignments.values_list(
            "subject_id",
            flat=True
        )
    )

    subject_ids.update(assignment_subject_ids)

    subjects = Subject.objects.filter(
        id__in=subject_ids
    ).order_by("code")

    # Attendance statistics
    total_attendance = attendance_records.count()

    present_attendance = attendance_records.filter(
        status="Present"
    ).count()

    absent_attendance = attendance_records.filter(
        status="Absent"
    ).count()

    attendance_percentage = (
        round(
            (present_attendance / total_attendance) * 100,
            2
        )
        if total_attendance > 0
        else 0
    )

    # Subject-wise attendance
    subject_attendance = []

    for subject in subjects:

        records = attendance_records.filter(
            subject=subject
        )

        total = records.count()

        present = records.filter(
            status="Present"
        ).count()

        percentage = (
            round(
                (present / total) * 100,
                2
            )
            if total > 0
            else 0
        )

        subject_attendance.append({
            "subject": subject,
            "total": total,
            "present": present,
            "absent": total - present,
            "percentage": percentage,
        })

    # Unique students handled by faculty
    student_ids = attendance_records.values_list(
        "student_id",
        flat=True
    ).distinct()

    total_students = student_ids.count()

    context = {
        "faculty": faculty,

        "total_students": total_students,

        "total_attendance": total_attendance,
        "present_attendance": present_attendance,
        "absent_attendance": absent_attendance,
        "attendance_percentage": attendance_percentage,

        "total_assignments": assignments.count(),

        "subject_attendance": subject_attendance,
    }

    return render(
        request,
        "students/faculty_reports.html",
        context
    )
@login_required
def faculty_subject_mapping(request):
    if not request.user.is_staff:
        return redirect("student-dashboard")


    faculties = Faculty.objects.prefetch_related("subjects").order_by("name")

    selected_faculty = None
    form = None

    faculty_id = request.GET.get("faculty")

    if faculty_id:
        selected_faculty = get_object_or_404(
            Faculty,
            id=faculty_id
        )

        if request.method == "POST":
            form = FacultySubjectMappingForm(
                request.POST,
                instance=selected_faculty
            )

            if form.is_valid():
                form.save()
                return redirect(
                    f"/students/faculty-subject-mapping/?faculty={selected_faculty.id}"
                )

        else:
            form = FacultySubjectMappingForm(
                instance=selected_faculty
            )

    context = {
        "faculties": faculties,
        "selected_faculty": selected_faculty,
        "form": form,
    }

    return render(
        request,
        "students/faculty_subject_mapping.html",
        context
    )
@login_required
def my_timetable(request):

    if not request.user.groups.filter(name="Student").exists():
        return redirect("student-dashboard")


    if not request.user.groups.filter(name="Student").exists():
        return redirect("student-dashboard")

    student = request.user.student_profile

    timetable = Timetable.objects.filter(
        course=student.course,
        semester=student.semester
    ).select_related(
        "subject",
        "faculty"
    ).order_by(
        "day",
        "start_time"
    )

    context = {
        "student": student,
        "timetable": timetable,
    }

    return render(
        request,
        "students/my_timetable.html",
        context
    )
@login_required
def faculty_timetable(request):

    if not request.user.groups.filter(name="Faculty").exists():
        return redirect("student-dashboard")


    if not request.user.groups.filter(name="Faculty").exists():
        return redirect("student-dashboard")

    faculty = request.user.faculty_profile

    timetable = Timetable.objects.filter(
        faculty=faculty
    ).select_related(
        "subject",
        "course",
        "semester"
    ).order_by(
        "day",
        "start_time"
    )

    context = {
        "faculty": faculty,
        "timetable": timetable,
    }

    return render(
        request,
        "students/faculty_timetable.html",
        context
    )
@login_required
def student_leave_requests(request):

    if not request.user.groups.filter(name="Student").exists():
        return redirect("student-dashboard")


    if not request.user.groups.filter(name="Student").exists():
        return redirect("student-dashboard")

    student = request.user.student_profile

    leave_requests = LeaveRequest.objects.filter(
        student=student
    ).order_by("-applied_at")

    context = {
        "student": student,
        "leave_requests": leave_requests,
    }

    return render(
        request,
        "students/student_leave_requests.html",
        context
    )
@login_required
def apply_leave(request):

    if not request.user.groups.filter(name="Student").exists():
        return redirect("student-dashboard")


    if not request.user.groups.filter(name="Student").exists():
        return redirect("student-dashboard")

    student = request.user.student_profile

    if request.method == "POST":

        leave_type = request.POST.get("leave_type", "").strip()
        start_date = request.POST.get("start_date", "").strip()
        end_date = request.POST.get("end_date", "").strip()
        reason = request.POST.get("reason", "").strip()

        if not all([
            leave_type,
            start_date,
            end_date,
            reason
        ]):
            return render(
                request,
                "students/apply_leave.html",
                {
                    "student": student,
                    "error": "Please fill all required fields.",
                }
            )

        start = parse_date(start_date)
        end = parse_date(end_date)

        if not start or not end:
            return render(
                request,
                "students/apply_leave.html",
                {
                    "student": student,
                    "error": "Please enter valid dates.",
                }
            )

        if end < start:
            return render(
                request,
                "students/apply_leave.html",
                {
                    "student": student,
                    "error": "End date cannot be before start date.",
                }
            )

        LeaveRequest.objects.create(
            student=student,
            leave_type=leave_type,
            start_date=start,
            end_date=end,
            reason=reason,
        )

        return redirect("student-leave-requests")

    return render(
        request,
        "students/apply_leave.html",
        {
            "student": student,
        }
    )
@login_required
def faculty_leave_requests(request):

    if not request.user.groups.filter(name="Faculty").exists():
        return redirect("student-dashboard")


    if not request.user.groups.filter(name="Faculty").exists():
        return redirect("student-dashboard")

    faculty = request.user.faculty_profile

    leave_requests = LeaveRequest.objects.filter(
        student__department=faculty.department
    ).select_related(
        "student",
        "student__course",
        "student__semester"
    ).order_by("-applied_at")

    if request.method == "POST":

        leave_id = request.POST.get("leave_id", "").strip()
        action = request.POST.get("action", "").strip()

        leave = get_object_or_404(
            LeaveRequest,
            id=leave_id,
            student__department=faculty.department
        )

        if leave.status != "Pending":
            return redirect("faculty-leave-requests")

        if action == "approve":
            leave.status = "Approved"

        elif action == "reject":
            leave.status = "Rejected"

        else:
            return redirect("faculty-leave-requests")

        leave.reviewed_by = request.user
        leave.reviewed_at = timezone.now()
        leave.save()

        Notification.objects.create(
            recipient=leave.student.user,
            title=f"Leave Request {leave.status}",
            message=(
                f"Your {leave.leave_type} request "
                f"from {leave.start_date} to {leave.end_date} "
                f"has been {leave.status.lower()}."
            )
        )

        return redirect("faculty-leave-requests")

    context = {
        "faculty": faculty,
        "leave_requests": leave_requests,
    }

    return render(
        request,
        "students/faculty_leave_requests.html",
        context
    )
@login_required
def student_complaints(request):

    if not request.user.groups.filter(name="Student").exists():
        return redirect("student-dashboard")


    if not request.user.groups.filter(name="Student").exists():
        return redirect("student-dashboard")

    student = request.user.student_profile

    complaints = Complaint.objects.filter(
        student=student
    ).order_by("-created_at")

    context = {
        "student": student,
        "complaints": complaints,
    }

    return render(
        request,
        "students/student_complaints.html",
        context
    )
@login_required
def create_complaint(request):

    if not request.user.groups.filter(name="Student").exists():
        return redirect("student-dashboard")


    if not request.user.groups.filter(name="Student").exists():
        return redirect("student-dashboard")

    student = request.user.student_profile

    if request.method == "POST":

        title = request.POST.get("title", "").strip()
        category = request.POST.get("category", "").strip()
        description = request.POST.get("description", "").strip()
        priority = request.POST.get("priority", "").strip()

        if not all([
            title,
            category,
            description,
            priority
        ]):
            return render(
                request,
                "students/create_complaint.html",
                {
                    "student": student,
                    "error": "Please fill all required fields.",
                }
            )

        Complaint.objects.create(
            student=student,
            title=title,
            category=category,
            description=description,
            priority=priority,
        )

        return redirect("student-complaints")

    return render(
        request,
        "students/create_complaint.html",
        {
            "student": student,
        }
    )
@login_required
def admin_complaints(request):

    if not request.user.is_staff:
        return redirect("student-dashboard")


    if not request.user.is_staff:
        return redirect("student-dashboard")

    complaints = Complaint.objects.filter(
        student__isnull=False
    ).select_related(
        "student",
        "student__course",
        "student__semester"
    ).order_by("-created_at")

    if request.method == "POST":

        complaint_id = request.POST.get(
            "complaint_id",
            ""
        ).strip()

        status = request.POST.get(
            "status",
            ""
        ).strip()

        admin_response = request.POST.get(
            "admin_response",
            ""
        ).strip()

        complaint = get_object_or_404(
            Complaint,
            id=complaint_id
        )

        allowed_statuses = [
            "Pending",
            "In Progress",
            "Resolved",
            "Rejected",
        ]

        if status not in allowed_statuses:
            return redirect("admin-complaints")

        complaint.status = status
        complaint.admin_response = admin_response

        if status == "Resolved":
            complaint.resolved_at = timezone.now()
        else:
            complaint.resolved_at = None

        complaint.save()

        Notification.objects.create(
            recipient=complaint.student.user,
            title="Complaint Status Updated",
            message=(
                f"Your complaint "
                f"'{complaint.title}' "
                f"has been marked as "
                f"'{status}'."
            )
        )

        return redirect("admin-complaints")

    context = {
        "complaints": complaints,
    }

    return render(
        request,
        "students/admin_complaints.html",
        context
    )