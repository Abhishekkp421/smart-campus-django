from rest_framework import serializers
from .models import Student, Faculty, Attendance,Result, Exam, Assignment,Fee, Notice, Event


class StudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student
        fields = [
            "id",
            "student_id",
            "name",
            "email",
            "phone",
            "date_of_birth",
            "gender",
            "department",
            "course",
            "semester",
            "admission_date",
            "address",
            "created_at",
            "updated_at",
        ]
class FacultySerializer(serializers.ModelSerializer):

    class Meta:
        model = Faculty
        fields = "__all__"
from .models import Attendance


class AttendanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Attendance
        fields = "__all__"
class ResultSerializer(serializers.ModelSerializer):

    class Meta:
        model = Result
        fields = "__all__"


class ExamSerializer(serializers.ModelSerializer):

    class Meta:
        model = Exam
        fields = "__all__"


class AssignmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Assignment
        fields = "__all__"
class FeeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Fee
        fields = "__all__"


class NoticeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notice
        fields = "__all__"


class EventSerializer(serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = "__all__"