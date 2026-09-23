from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import (
    Student,
    Faculty,
    Attendance,
    Result,
    Exam,
    Assignment,
    Fee,
    Notice,
    Event,
)
from .serializers import (
    StudentSerializer,
    FacultySerializer,
    AttendanceSerializer,
    ResultSerializer,
    ExamSerializer,
    AssignmentSerializer,
    FeeSerializer,
    NoticeSerializer,
    EventSerializer,
)
from .permissions import IsAdminOrFaculty


def is_admin(request):
    return request.user.is_staff


def is_faculty(request):
    return request.user.groups.filter(name="Faculty").exists()


def get_faculty(request):
    return request.user.faculty_profile


def forbidden(message="Permission denied"):
    return Response(
        {"error": message},
        status=status.HTTP_403_FORBIDDEN,
    )


def not_found(message):
    return Response(
        {"error": message},
        status=status.HTTP_404_NOT_FOUND,
    )


# =========================
# STUDENT API
# =========================

class StudentListCreateAPIView(APIView):

    permission_classes = [IsAdminOrFaculty]

    def get(self, request):
        if is_admin(request):
            students = Student.objects.all()
        elif is_faculty(request):
            faculty = get_faculty(request)
            students = Student.objects.filter(
                course__department=faculty.department
            )
        else:
            students = Student.objects.none()

        return Response(StudentSerializer(students, many=True).data)

    def post(self, request):
        if not is_admin(request):
            return forbidden("Only admin can create students")

        serializer = StudentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class StudentDetailAPIView(APIView):

    permission_classes = [IsAdminOrFaculty]

    def get_object(self, request, student_id):
        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return None

        if is_admin(request):
            return student

        if is_faculty(request):
            faculty = get_faculty(request)
            if student.course.department_id == faculty.department_id:
                return student

        return None

    def get(self, request, student_id):
        student = self.get_object(request, student_id)

        if student is None:
            return not_found("Student not found")

        return Response(StudentSerializer(student).data)

    def put(self, request, student_id):
        if not is_admin(request):
            return forbidden("Only admin can update students")

        student = self.get_object(request, student_id)

        if student is None:
            return not_found("Student not found")

        serializer = StudentSerializer(student, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, student_id):
        if not is_admin(request):
            return forbidden("Only admin can delete students")

        student = self.get_object(request, student_id)

        if student is None:
            return not_found("Student not found")

        student.delete()

        return Response(
            {"message": "Student deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )


# =========================
# FACULTY API
# =========================

class FacultyListCreateAPIView(APIView):

    permission_classes = [IsAdminOrFaculty]

    def get(self, request):
        if is_admin(request):
            faculty = Faculty.objects.all()
        elif is_faculty(request):
            faculty = Faculty.objects.filter(user=request.user)
        else:
            faculty = Faculty.objects.none()

        return Response(FacultySerializer(faculty, many=True).data)

    def post(self, request):
        if not is_admin(request):
            return forbidden("Only admin can create faculty")

        serializer = FacultySerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class FacultyDetailAPIView(APIView):

    permission_classes = [IsAdminOrFaculty]

    def get_object(self, request, faculty_id):
        try:
            faculty = Faculty.objects.get(id=faculty_id)
        except Faculty.DoesNotExist:
            return None

        if is_admin(request):
            return faculty

        if is_faculty(request) and faculty.user_id == request.user.id:
            return faculty

        return None

    def get(self, request, faculty_id):
        faculty = self.get_object(request, faculty_id)

        if faculty is None:
            return not_found("Faculty not found")

        return Response(FacultySerializer(faculty).data)

    def put(self, request, faculty_id):
        if not is_admin(request):
            return forbidden("Only admin can update faculty")

        faculty = self.get_object(request, faculty_id)

        if faculty is None:
            return not_found("Faculty not found")

        serializer = FacultySerializer(faculty, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, faculty_id):
        if not is_admin(request):
            return forbidden("Only admin can delete faculty")

        faculty = self.get_object(request, faculty_id)

        if faculty is None:
            return not_found("Faculty not found")

        faculty.delete()

        return Response(
            {"message": "Faculty deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )


# =========================
# ATTENDANCE API
# =========================

class AttendanceListCreateAPIView(APIView):

    permission_classes = [IsAdminOrFaculty]

    def get(self, request):
        if is_admin(request):
            attendance = Attendance.objects.all()
        elif is_faculty(request):
            faculty = get_faculty(request)
            attendance = Attendance.objects.filter(
                faculty=faculty,
                subject__in=faculty.subjects.all(),
            )
        else:
            attendance = Attendance.objects.none()

        return Response(AttendanceSerializer(attendance, many=True).data)

    def post(self, request):
        if is_admin(request):
            serializer = AttendanceSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED,
                )

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        if is_faculty(request):
            faculty = get_faculty(request)
            subject_id = request.data.get("subject")

            if not subject_id:
                return Response(
                    {"error": "Subject is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not faculty.subjects.filter(id=subject_id).exists():
                return forbidden(
                    "You can only add attendance for your assigned subjects"
                )

            serializer = AttendanceSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save(faculty=faculty)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED,
                )

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        return forbidden()


class AttendanceDetailAPIView(APIView):

    permission_classes = [IsAdminOrFaculty]

    def get_object(self, request, attendance_id):
        try:
            attendance = Attendance.objects.get(id=attendance_id)
        except Attendance.DoesNotExist:
            return None

        if is_admin(request):
            return attendance

        if is_faculty(request):
            faculty = get_faculty(request)
            if (
                attendance.faculty_id == faculty.id
                and faculty.subjects.filter(id=attendance.subject_id).exists()
            ):
                return attendance

        return None

    def get(self, request, attendance_id):
        attendance = self.get_object(request, attendance_id)

        if attendance is None:
            return not_found("Attendance record not found")

        return Response(AttendanceSerializer(attendance).data)

    def put(self, request, attendance_id):
        attendance = self.get_object(request, attendance_id)

        if attendance is None:
            return not_found("Attendance record not found")

        if is_faculty(request):
            new_subject = request.data.get("subject")
            if new_subject and str(new_subject) != str(attendance.subject_id):
                return forbidden(
                    "You cannot change the subject of this attendance record"
                )

        serializer = AttendanceSerializer(
            attendance,
            data=request.data,
        )

        if serializer.is_valid():
            if is_faculty(request):
                serializer.save(faculty=get_faculty(request))
            else:
                serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, attendance_id):
        if not is_admin(request):
            return forbidden("Only admin can delete attendance")

        attendance = self.get_object(request, attendance_id)

        if attendance is None:
            return not_found("Attendance record not found")

        attendance.delete()

        return Response(
            {"message": "Attendance deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )


# =========================
# RESULT API
# =========================

class ResultListCreateAPIView(APIView):

    permission_classes = [IsAdminOrFaculty]

    def get(self, request):
        if is_admin(request):
            results = Result.objects.all()
        elif is_faculty(request):
            faculty = get_faculty(request)
            results = Result.objects.filter(
                subject__in=faculty.subjects.all()
            )
        else:
            results = Result.objects.none()

        return Response(ResultSerializer(results, many=True).data)

    def post(self, request):
        if is_admin(request):
            serializer = ResultSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED,
                )

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        if is_faculty(request):
            faculty = get_faculty(request)
            subject_id = request.data.get("subject")

            if not subject_id:
                return Response(
                    {"error": "Subject is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not faculty.subjects.filter(id=subject_id).exists():
                return forbidden(
                    "You can only add results for your assigned subjects"
                )

            serializer = ResultSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED,
                )

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        return forbidden()


class ResultDetailAPIView(APIView):

    permission_classes = [IsAdminOrFaculty]

    def get_object(self, request, result_id):
        try:
            result = Result.objects.get(id=result_id)
        except Result.DoesNotExist:
            return None

        if is_admin(request):
            return result

        if is_faculty(request):
            faculty = get_faculty(request)
            if faculty.subjects.filter(id=result.subject_id).exists():
                return result

        return None

    def get(self, request, result_id):
        result = self.get_object(request, result_id)

        if result is None:
            return not_found("Result not found")

        return Response(ResultSerializer(result).data)

    def put(self, request, result_id):
        result = self.get_object(request, result_id)

        if result is None:
            return not_found("Result not found")

        if is_faculty(request):
            new_subject = request.data.get("subject")
            if new_subject and str(new_subject) != str(result.subject_id):
                return forbidden("You cannot change the subject of this result")

        serializer = ResultSerializer(result, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, result_id):
        if not is_admin(request):
            return forbidden("Only admin can delete results")

        result = self.get_object(request, result_id)

        if result is None:
            return not_found("Result not found")

        result.delete()

        return Response(
            {"message": "Result deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )


# =========================
# EXAM API
# =========================

class ExamListCreateAPIView(APIView):

    permission_classes = [IsAdminOrFaculty]

    def get(self, request):
        if is_admin(request):
            exams = Exam.objects.all()
        elif is_faculty(request):
            faculty = get_faculty(request)
            exams = Exam.objects.filter(
                subject__in=faculty.subjects.all()
            )
        else:
            exams = Exam.objects.none()

        return Response(ExamSerializer(exams, many=True).data)

    def post(self, request):
        if is_admin(request):
            serializer = ExamSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED,
                )

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        if is_faculty(request):
            faculty = get_faculty(request)
            subject_id = request.data.get("subject")

            if not subject_id:
                return Response(
                    {"error": "Subject is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not faculty.subjects.filter(id=subject_id).exists():
                return forbidden(
                    "You can only create exams for your assigned subjects"
                )

            serializer = ExamSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED,
                )

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        return forbidden()


class ExamDetailAPIView(APIView):

    permission_classes = [IsAdminOrFaculty]

    def get_object(self, request, exam_id):
        try:
            exam = Exam.objects.get(id=exam_id)
        except Exam.DoesNotExist:
            return None

        if is_admin(request):
            return exam

        if is_faculty(request):
            faculty = get_faculty(request)
            if faculty.subjects.filter(id=exam.subject_id).exists():
                return exam

        return None

    def get(self, request, exam_id):
        exam = self.get_object(request, exam_id)

        if exam is None:
            return not_found("Exam not found")

        return Response(ExamSerializer(exam).data)

    def put(self, request, exam_id):
        exam = self.get_object(request, exam_id)

        if exam is None:
            return not_found("Exam not found")

        if is_faculty(request):
            new_subject = request.data.get("subject")
            if new_subject and str(new_subject) != str(exam.subject_id):
                return forbidden("You cannot change the subject of this exam")

        serializer = ExamSerializer(exam, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, exam_id):
        if not is_admin(request):
            return forbidden("Only admin can delete exams")

        exam = self.get_object(request, exam_id)

        if exam is None:
            return not_found("Exam not found")

        exam.delete()

        return Response(
            {"message": "Exam deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )


# =========================
# ASSIGNMENT API
# =========================

class AssignmentListCreateAPIView(APIView):

    permission_classes = [IsAdminOrFaculty]

    def get(self, request):
        if is_admin(request):
            assignments = Assignment.objects.all()
        elif is_faculty(request):
            faculty = get_faculty(request)
            assignments = Assignment.objects.filter(
                faculty=faculty,
                subject__in=faculty.subjects.all(),
            )
        else:
            assignments = Assignment.objects.none()

        return Response(AssignmentSerializer(assignments, many=True).data)

    def post(self, request):
        if is_admin(request):
            serializer = AssignmentSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED,
                )

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        if is_faculty(request):
            faculty = get_faculty(request)
            subject_id = request.data.get("subject")

            if not subject_id:
                return Response(
                    {"error": "Subject is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not faculty.subjects.filter(id=subject_id).exists():
                return forbidden(
                    "You can only create assignments for your assigned subjects"
                )

            serializer = AssignmentSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save(faculty=faculty)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED,
                )

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        return forbidden()


class AssignmentDetailAPIView(APIView):

    permission_classes = [IsAdminOrFaculty]

    def get_object(self, request, assignment_id):
        try:
            assignment = Assignment.objects.get(id=assignment_id)
        except Assignment.DoesNotExist:
            return None

        if is_admin(request):
            return assignment

        if is_faculty(request):
            faculty = get_faculty(request)
            if (
                assignment.faculty_id == faculty.id
                and faculty.subjects.filter(id=assignment.subject_id).exists()
            ):
                return assignment

        return None

    def get(self, request, assignment_id):
        assignment = self.get_object(request, assignment_id)

        if assignment is None:
            return not_found("Assignment not found")

        return Response(AssignmentSerializer(assignment).data)

    def put(self, request, assignment_id):
        assignment = self.get_object(request, assignment_id)

        if assignment is None:
            return not_found("Assignment not found")

        if is_faculty(request):
            new_subject = request.data.get("subject")
            if new_subject and str(new_subject) != str(assignment.subject_id):
                return forbidden(
                    "You cannot change the subject of this assignment"
                )

        serializer = AssignmentSerializer(assignment, data=request.data)

        if serializer.is_valid():
            if is_faculty(request):
                serializer.save(faculty=get_faculty(request))
            else:
                serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, assignment_id):
        if not is_admin(request):
            return forbidden("Only admin can delete assignments")

        assignment = self.get_object(request, assignment_id)

        if assignment is None:
            return not_found("Assignment not found")

        assignment.delete()

        return Response(
            {"message": "Assignment deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )


# =========================
# FEE API
# =========================

class FeeListCreateAPIView(APIView):

    permission_classes = [IsAdminOrFaculty]

    def get(self, request):
        if is_admin(request):
            fees = Fee.objects.all()
        elif is_faculty(request):
            faculty = get_faculty(request)
            fees = Fee.objects.filter(
                student__course__department=faculty.department
            )
        else:
            fees = Fee.objects.none()

        return Response(FeeSerializer(fees, many=True).data)

    def post(self, request):
        if not is_admin(request):
            return forbidden("Only admin can create fees")

        serializer = FeeSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class FeeDetailAPIView(APIView):

    permission_classes = [IsAdminOrFaculty]

    def get_object(self, request, fee_id):
        try:
            fee = Fee.objects.get(id=fee_id)
        except Fee.DoesNotExist:
            return None

        if is_admin(request):
            return fee

        if is_faculty(request):
            faculty = get_faculty(request)
            if fee.student.course.department_id == faculty.department_id:
                return fee

        return None

    def get(self, request, fee_id):
        fee = self.get_object(request, fee_id)

        if fee is None:
            return not_found("Fee not found")

        return Response(FeeSerializer(fee).data)

    def put(self, request, fee_id):
        if not is_admin(request):
            return forbidden("Only admin can update fees")

        fee = self.get_object(request, fee_id)

        if fee is None:
            return not_found("Fee not found")

        serializer = FeeSerializer(fee, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, fee_id):
        if not is_admin(request):
            return forbidden("Only admin can delete fees")

        fee = self.get_object(request, fee_id)

        if fee is None:
            return not_found("Fee not found")

        fee.delete()

        return Response(
            {"message": "Fee deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )


# =========================
# NOTICE API
# =========================

class NoticeListCreateAPIView(APIView):

    permission_classes = [IsAdminOrFaculty]

    def get(self, request):
        if is_admin(request):
            notices = Notice.objects.all()
        elif is_faculty(request):
            faculty = get_faculty(request)
            notices = Notice.objects.filter(faculty=faculty)
        else:
            notices = Notice.objects.none()

        return Response(NoticeSerializer(notices, many=True).data)

    def post(self, request):
        if not is_admin(request):
            return forbidden("Only admin can create notices")

        serializer = NoticeSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class NoticeDetailAPIView(APIView):

    permission_classes = [IsAdminOrFaculty]

    def get_object(self, request, notice_id):
        try:
            notice = Notice.objects.get(id=notice_id)
        except Notice.DoesNotExist:
            return None

        if is_admin(request):
            return notice

        if is_faculty(request):
            faculty = get_faculty(request)
            if notice.faculty_id == faculty.id:
                return notice

        return None

    def get(self, request, notice_id):
        notice = self.get_object(request, notice_id)

        if notice is None:
            return not_found("Notice not found")

        return Response(NoticeSerializer(notice).data)

    def put(self, request, notice_id):
        if not is_admin(request):
            return forbidden("Only admin can update notices")

        notice = self.get_object(request, notice_id)

        if notice is None:
            return not_found("Notice not found")

        serializer = NoticeSerializer(notice, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, notice_id):
        if not is_admin(request):
            return forbidden("Only admin can delete notices")

        notice = self.get_object(request, notice_id)

        if notice is None:
            return not_found("Notice not found")

        notice.delete()

        return Response(
            {"message": "Notice deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )


# =========================
# EVENT API
# =========================

class EventListCreateAPIView(APIView):

    permission_classes = [IsAdminOrFaculty]

    def get(self, request):
        if is_admin(request) or is_faculty(request):
            events = Event.objects.all()
        else:
            events = Event.objects.none()

        return Response(EventSerializer(events, many=True).data)

    def post(self, request):
        if not is_admin(request):
            return forbidden("Only admin can create events")

        serializer = EventSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class EventDetailAPIView(APIView):

    permission_classes = [IsAdminOrFaculty]

    def get_object(self, request, event_id):
        try:
            return Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return None

    def get(self, request, event_id):
        event = self.get_object(request, event_id)

        if event is None:
            return not_found("Event not found")

        return Response(EventSerializer(event).data)

    def put(self, request, event_id):
        if not is_admin(request):
            return forbidden("Only admin can update events")

        event = self.get_object(request, event_id)

        if event is None:
            return not_found("Event not found")

        serializer = EventSerializer(event, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, event_id):
        if not is_admin(request):
            return forbidden("Only admin can delete events")

        event = self.get_object(request, event_id)

        if event is None:
            return not_found("Event not found")

        event.delete()

        return Response(
            {"message": "Event deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )
