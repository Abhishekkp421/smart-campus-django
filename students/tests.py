from datetime import date
from django.test import TestCase
from django.contrib.auth.models import User

from .models import (
    Department,
    Course,
    Semester,
    Student,
    Subject,
    Complaint,
)


class StudentModelTest(TestCase):

    def setUp(self):

        self.department = Department.objects.create(
            name="Computer Science",
            code="CSE"
        )

        self.course = Course.objects.create(
            name="Bachelor of Technology",
            code="BTECH-CSE",
            department=self.department
        )

        self.semester = Semester.objects.create(
            number=1
        )

        self.user = User.objects.create_user(
            username="teststudent",
            password="testpass123"
        )

        self.student = Student.objects.create(
            student_id="TEST001",
            user=self.user,
            name="Test Student",
            email="test@example.com",
            phone="9876543210",
            date_of_birth=date(2000, 1, 1),
            admission_date=date(2024, 8, 1),
            department=self.department,
            course=self.course,
            semester=self.semester,
        )

    def test_student_created(self):

        self.assertEqual(
            self.student.student_id,
            "TEST001"
        )

        self.assertEqual(
            self.student.name,
            "Test Student"
        )

        self.assertEqual(
            self.student.department,
            self.department
        )


class ComplaintModelTest(TestCase):

    def setUp(self):

        self.department = Department.objects.create(
            name="Computer Science",
            code="CSE"
        )

        self.course = Course.objects.create(
            name="Bachelor of Technology",
            code="BTECH-CSE",
            department=self.department
        )

        self.semester = Semester.objects.create(
            number=1
        )

        self.user = User.objects.create_user(
            username="complaintstudent",
            password="testpass123"
        )

        self.student = Student.objects.create(
            student_id="TEST002",
            user=self.user,
            name="Complaint Student",
            email="complaint@example.com",
            phone="9876543211",
            date_of_birth=date(2000, 1, 1),
            admission_date=date(2024, 8, 1),
            department=self.department,
            course=self.course,
            semester=self.semester,
        )

    def test_complaint_default_status(self):

        complaint = Complaint.objects.create(
            student=self.student,
            title="Test Complaint",
            category="Technical",
            description="Testing complaint system.",
            priority="Medium"
        )

        self.assertEqual(
            complaint.status,
            "Pending"
        )

    def test_complaint_student_relation(self):

        complaint = Complaint.objects.create(
            student=self.student,
            title="Test Complaint",
            category="Library",
            description="Library issue.",
            priority="Low"
        )

        self.assertEqual(
            complaint.student,
            self.student
        )