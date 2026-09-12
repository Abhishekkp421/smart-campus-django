from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from .forms import StudentForm,FacultyForm
from .models import Student, Faculty, Course, Department, Semester, Subject, Attendance,Exam,Result,Assignment,Fee,Notice,Event,Book,BookIssue
from django.utils.dateparse import parse_date

@login_required
def dashboard(request):
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
def student_list(request):
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
def student_detail(request, student_id):
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


def edit_student(request, student_id):
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


def delete_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    if request.method == "POST":
        student.delete()
        return redirect("student-list")

    return render(
        request,
        "students/delete_student.html",
        {"student": student}
    )

def add_student(request):

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
def faculty_list(request):
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
def faculty_detail(request, faculty_id):
    faculty = get_object_or_404(
        Faculty.objects.select_related("department"),
        id=faculty_id
    )

    return render(
        request,
        "students/faculty_detail.html",
        {"faculty": faculty}
    )
def edit_faculty(request, faculty_id):
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
def delete_faculty(request, faculty_id):
    faculty = get_object_or_404(Faculty, id=faculty_id)

    if request.method == "POST":
        faculty.delete()
        return redirect("faculty-list")

    return render(
        request,
        "students/delete_faculty.html",
        {"faculty": faculty}
    )
def add_faculty(request):
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
def attendance(request):

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
def attendance_history(request):

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
def exam_list(request):

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


def add_exam(request):

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


def edit_exam(request, exam_id):

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


def delete_exam(request, exam_id):

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
def result_list(request):

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


def add_result(request):

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


def edit_result(request, result_id):

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


def delete_result(request, result_id):

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
def marksheet_list(request):

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

def assignment_list(request):

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


def add_assignment(request):

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


def edit_assignment(request, assignment_id):

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


def delete_assignment(request, assignment_id):

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
def fee_list(request):
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


def add_fee(request):
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


def edit_fee(request, fee_id):
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


def delete_fee(request, fee_id):
    fee = get_object_or_404(Fee, id=fee_id)

    if request.method == "POST":
        fee.delete()
        return redirect("fee-list")

    return render(
        request,
        "students/delete_fee.html",
        {"fee": fee}
    )
def notice_list(request):
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


def add_notice(request):
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


def edit_notice(request, notice_id):
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


def delete_notice(request, notice_id):
    notice = get_object_or_404(Notice, id=notice_id)

    if request.method == "POST":
        notice.delete()
        return redirect("notice-list")

    return render(
        request,
        "students/delete_notice.html",
        {"notice": notice}
    )
def event_list(request):
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


def add_event(request):
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


def edit_event(request, event_id):
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


def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == "POST":
        event.delete()
        return redirect("event-list")

    return render(
        request,
        "students/delete_event.html",
        {"event": event}
    )
def book_list(request):

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


def add_book(request):

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


def edit_book(request, book_id):

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


def delete_book(request, book_id):

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
def book_issue_list(request):

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


def issue_book(request):

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


def return_book(request, issue_id):

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
def reports(request):

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
from rest_framework.decorators import api_view

from .serializers import StudentSerializer


@api_view(["GET", "POST"])
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

def settings_view(request):
    return render(
        request,
        "students/settings.html",
        {
            "user": request.user
        }
    )