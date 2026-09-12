from rest_framework.test import APIClient
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.authtoken.models import Token

from .models import Department, Course, Semester, Student


class StudentModelTest(TestCase):

    def setUp(self):
        self.department = Department.objects.create(
            name="Test Computer Science",
            code="TEST-CSE"
        )

        self.course = Course.objects.create(
            name="Test B.Tech CSE",
            code="TEST-BTECH",
            department=self.department,
            duration_years=4
        )

        self.semester = Semester.objects.create(
            number=1,
            name="Test Semester 1"
        )

        self.student = Student.objects.create(
            student_id="TEST001",
            name="Test Student",
            email="teststudent@example.com",
            phone="9876543210",
            date_of_birth="2003-01-01",
            gender="Male",
            department=self.department,
            course=self.course,
            semester=self.semester,
            admission_date="2026-01-01",
            address="Test Address"
        )

    def test_student_created(self):
        self.assertEqual(Student.objects.count(), 1)
        self.assertEqual(self.student.student_id, "TEST001")

    def test_student_string(self):
        self.assertEqual(
            str(self.student),
            "TEST001 - Test Student"
        )


class DashboardTest(TestCase):

    def test_dashboard_requires_login(self):
        response = self.client.get("/students/")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/students/login/", response.url)


class APIAuthenticationTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testadmin",
            password="testpassword123",
            is_staff=True
        )

        self.token = Token.objects.create(
            user=self.user
        )

        self.client = APIClient()

    def test_api_requires_authentication(self):
        response = self.client.get("/students/api/students/")

        self.assertEqual(response.status_code, 401)

    def test_api_allows_authenticated_user(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.token.key}"
        )

        response = self.client.get("/students/api/students/")

        self.assertEqual(response.status_code, 200)