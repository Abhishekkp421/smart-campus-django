from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Student, Faculty, Attendance,Result, Exam, Assignment,Fee, Notice, Event
from .serializers import StudentSerializer, FacultySerializer,AttendanceSerializer,ResultSerializer, ExamSerializer, AssignmentSerializer,FeeSerializer, NoticeSerializer, EventSerializer
from .permissions import IsAdminOrFaculty


# =========================
# STUDENT API
# =========================

class StudentListCreateAPIView(APIView):

    permission_classes = [IsAdminOrFaculty]

    def get(self, request):
        students = Student.objects.all()
        serializer = StudentSerializer(students, many=True)

        return Response(serializer.data)

    def post(self, request):
        serializer = StudentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class StudentDetailAPIView(APIView):

    permission_classes = [IsAdminOrFaculty]

    def get_object(self, student_id):
        try:
            return Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return None

    def get(self, request, student_id):
        student = self.get_object(student_id)

        if student is None:
            return Response(
                {"error": "Student not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = StudentSerializer(student)

        return Response(serializer.data)

    def put(self, request, student_id):
        student = self.get_object(student_id)

        if student is None:
            return Response(
                {"error": "Student not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = StudentSerializer(
            student,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, student_id):
        student = self.get_object(student_id)

        if student is None:
            return Response(
                {"error": "Student not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        student.delete()

        return Response(
            {"message": "Student deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )


# =========================
# FACULTY API
# =========================

class FacultyListCreateAPIView(APIView):

    permission_classes = [IsAdminOrFaculty]

    def get(self, request):
        faculty = Faculty.objects.all()
        serializer = FacultySerializer(faculty, many=True)

        return Response(serializer.data)

    def post(self, request):
        serializer = FacultySerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class FacultyDetailAPIView(APIView):

    permission_classes = [IsAdminOrFaculty]

    def get_object(self, faculty_id):
        try:
            return Faculty.objects.get(id=faculty_id)
        except Faculty.DoesNotExist:
            return None

    def get(self, request, faculty_id):
        faculty = self.get_object(faculty_id)

        if faculty is None:
            return Response(
                {"error": "Faculty not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = FacultySerializer(faculty)

        return Response(serializer.data)

    def put(self, request, faculty_id):
        faculty = self.get_object(faculty_id)

        if faculty is None:
            return Response(
                {"error": "Faculty not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = FacultySerializer(
            faculty,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, faculty_id):
        faculty = self.get_object(faculty_id)

        if faculty is None:
            return Response(
                {"error": "Faculty not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        faculty.delete()

        return Response(
            {"message": "Faculty deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )
# =========================
# ATTENDANCE API
# =========================

class AttendanceListCreateAPIView(APIView):

    permission_classes = [IsAdminOrFaculty]

    def get(self, request):
        attendance = Attendance.objects.all()
        serializer = AttendanceSerializer(attendance, many=True)

        return Response(serializer.data)

    def post(self, request):
        serializer = AttendanceSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class AttendanceDetailAPIView(APIView):

    permission_classes = [IsAdminOrFaculty]

    def get_object(self, attendance_id):
        try:
            return Attendance.objects.get(id=attendance_id)
        except Attendance.DoesNotExist:
            return None

    def get(self, request, attendance_id):
        attendance = self.get_object(attendance_id)

        if attendance is None:
            return Response(
                {"error": "Attendance record not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = AttendanceSerializer(attendance)

        return Response(serializer.data)

    def put(self, request, attendance_id):
        attendance = self.get_object(attendance_id)

        if attendance is None:
            return Response(
                {"error": "Attendance record not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = AttendanceSerializer(
            attendance,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, attendance_id):
        attendance = self.get_object(attendance_id)

        if attendance is None:
            return Response(
                {"error": "Attendance record not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        attendance.delete()

        return Response(
            {"message": "Attendance deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )
# =========================
# RESULT API
# =========================

class ResultListCreateAPIView(APIView):

    permission_classes = [IsAdminOrFaculty]

    def get(self, request):
        results = Result.objects.all()
        serializer = ResultSerializer(results, many=True)

        return Response(serializer.data)

    def post(self, request):
        serializer = ResultSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class ResultDetailAPIView(APIView):

    permission_classes = [IsAdminOrFaculty]

    def get_object(self, result_id):
        try:
            return Result.objects.get(id=result_id)
        except Result.DoesNotExist:
            return None

    def get(self, request, result_id):
        result = self.get_object(result_id)

        if result is None:
            return Response(
                {"error": "Result not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ResultSerializer(result)

        return Response(serializer.data)

    def put(self, request, result_id):
        result = self.get_object(result_id)

        if result is None:
            return Response(
                {"error": "Result not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ResultSerializer(
            result,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, result_id):
        result = self.get_object(result_id)

        if result is None:
            return Response(
                {"error": "Result not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        result.delete()

        return Response(
            {"message": "Result deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )


# =========================
# EXAM API
# =========================

class ExamListCreateAPIView(APIView):

    permission_classes = [IsAdminOrFaculty]

    def get(self, request):
        exams = Exam.objects.all()
        serializer = ExamSerializer(exams, many=True)

        return Response(serializer.data)

    def post(self, request):
        serializer = ExamSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class ExamDetailAPIView(APIView):

    permission_classes = [IsAdminOrFaculty]

    def get_object(self, exam_id):
        try:
            return Exam.objects.get(id=exam_id)
        except Exam.DoesNotExist:
            return None

    def get(self, request, exam_id):
        exam = self.get_object(exam_id)

        if exam is None:
            return Response(
                {"error": "Exam not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ExamSerializer(exam)

        return Response(serializer.data)

    def put(self, request, exam_id):
        exam = self.get_object(exam_id)

        if exam is None:
            return Response(
                {"error": "Exam not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ExamSerializer(
            exam,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, exam_id):
        exam = self.get_object(exam_id)

        if exam is None:
            return Response(
                {"error": "Exam not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        exam.delete()

        return Response(
            {"message": "Exam deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )


# =========================
# ASSIGNMENT API
# =========================

class AssignmentListCreateAPIView(APIView):

    permission_classes = [IsAdminOrFaculty]

    def get(self, request):
        assignments = Assignment.objects.all()
        serializer = AssignmentSerializer(assignments, many=True)

        return Response(serializer.data)

    def post(self, request):
        serializer = AssignmentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class AssignmentDetailAPIView(APIView):

    permission_classes = [IsAdminOrFaculty]

    def get_object(self, assignment_id):
        try:
            return Assignment.objects.get(id=assignment_id)
        except Assignment.DoesNotExist:
            return None

    def get(self, request, assignment_id):
        assignment = self.get_object(assignment_id)

        if assignment is None:
            return Response(
                {"error": "Assignment not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = AssignmentSerializer(assignment)

        return Response(serializer.data)

    def put(self, request, assignment_id):
        assignment = self.get_object(assignment_id)

        if assignment is None:
            return Response(
                {"error": "Assignment not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = AssignmentSerializer(
            assignment,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, assignment_id):
        assignment = self.get_object(assignment_id)

        if assignment is None:
            return Response(
                {"error": "Assignment not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        assignment.delete()

        return Response(
            {"message": "Assignment deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )
# =========================
# FEE API
# =========================

class FeeListCreateAPIView(APIView):

    permission_classes = [IsAdminOrFaculty]

    def get(self, request):
        fees = Fee.objects.all()
        serializer = FeeSerializer(fees, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = FeeSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class FeeDetailAPIView(APIView):

    permission_classes = [IsAdminOrFaculty]

    def get_object(self, fee_id):
        try:
            return Fee.objects.get(id=fee_id)
        except Fee.DoesNotExist:
            return None

    def get(self, request, fee_id):
        fee = self.get_object(fee_id)

        if fee is None:
            return Response(
                {"error": "Fee not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(FeeSerializer(fee).data)

    def put(self, request, fee_id):
        fee = self.get_object(fee_id)

        if fee is None:
            return Response(
                {"error": "Fee not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = FeeSerializer(fee, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, fee_id):
        fee = self.get_object(fee_id)

        if fee is None:
            return Response(
                {"error": "Fee not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        fee.delete()

        return Response(
            {"message": "Fee deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )


# =========================
# NOTICE API
# =========================

class NoticeListCreateAPIView(APIView):

    permission_classes = [IsAdminOrFaculty]

    def get(self, request):
        notices = Notice.objects.all()
        serializer = NoticeSerializer(notices, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = NoticeSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class NoticeDetailAPIView(APIView):

    permission_classes = [IsAdminOrFaculty]

    def get_object(self, notice_id):
        try:
            return Notice.objects.get(id=notice_id)
        except Notice.DoesNotExist:
            return None

    def get(self, request, notice_id):
        notice = self.get_object(notice_id)

        if notice is None:
            return Response(
                {"error": "Notice not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(NoticeSerializer(notice).data)

    def put(self, request, notice_id):
        notice = self.get_object(notice_id)

        if notice is None:
            return Response(
                {"error": "Notice not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = NoticeSerializer(notice, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, notice_id):
        notice = self.get_object(notice_id)

        if notice is None:
            return Response(
                {"error": "Notice not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        notice.delete()

        return Response(
            {"message": "Notice deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )


# =========================
# EVENT API
# =========================

class EventListCreateAPIView(APIView):

    permission_classes = [IsAdminOrFaculty]

    def get(self, request):
        events = Event.objects.all()
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = EventSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class EventDetailAPIView(APIView):

    permission_classes = [IsAdminOrFaculty]

    def get_object(self, event_id):
        try:
            return Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return None

    def get(self, request, event_id):
        event = self.get_object(event_id)

        if event is None:
            return Response(
                {"error": "Event not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(EventSerializer(event).data)

    def put(self, request, event_id):
        event = self.get_object(event_id)

        if event is None:
            return Response(
                {"error": "Event not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = EventSerializer(event, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, event_id):
        event = self.get_object(event_id)

        if event is None:
            return Response(
                {"error": "Event not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        event.delete()

        return Response(
            {"message": "Event deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )