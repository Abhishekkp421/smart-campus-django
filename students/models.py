from django.db import models
from django.contrib.auth.models import User


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.code} - {self.name}"


class Course(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="courses"
    )

    duration_years = models.PositiveIntegerField(default=4)

    def __str__(self):
        return f"{self.code} - {self.name}"


class Semester(models.Model):
    number = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Faculty(models.Model):
    employee_id = models.CharField(max_length=20, unique=True)

    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="faculty_profile"
    )

    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)

    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        related_name="faculty_members"
    )

    designation = models.CharField(max_length=100)

    subjects = models.ManyToManyField(
        "Subject",
        blank=True,
        related_name="faculty_members"
    )

    def __str__(self):
        return f"{self.employee_id} - {self.name}"

class Student(models.Model):
    student_id = models.CharField(max_length=20, unique=True)
    user = models.OneToOneField(
    User,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="student_profile"
   )
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=20)

    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        related_name="students"
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        related_name="students"
    )

    semester = models.ForeignKey(
        Semester,
        on_delete=models.SET_NULL,
        null=True,
        related_name="students"
    )

    admission_date = models.DateField()
    address = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student_id} - {self.name}"


class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="subjects"
    )

    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
        related_name="subjects"
    )

    credits = models.PositiveIntegerField(default=4)

    def __str__(self):
        return f"{self.code} - {self.name}"


class Attendance(models.Model):
    STATUS_CHOICES = [
        ("Present", "Present"),
        ("Absent", "Absent"),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="attendance_records"
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="attendance_records"
    )

    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.SET_NULL,
        null=True,
        related_name="attendance_records"
    )

    date = models.DateField()

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES
    )

    class Meta:
        ordering = ["-date"]

        constraints = [
            models.UniqueConstraint(
                fields=["student", "subject", "date"],
                name="unique_student_subject_date"
            )
        ]

    def __str__(self):
        return f"{self.student.student_id} - {self.subject.code} - {self.date}"

class Assignment(models.Model):
    title = models.CharField(max_length=150)

    description = models.TextField(blank=True)

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="assignments"
    )

    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assignments"
    )

    due_date = models.DateField()

    max_marks = models.PositiveIntegerField(default=100)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.subject.code}"
class Timetable(models.Model):

    DAY_CHOICES = [
        ("Monday", "Monday"),
        ("Tuesday", "Tuesday"),
        ("Wednesday", "Wednesday"),
        ("Thursday", "Thursday"),
        ("Friday", "Friday"),
        ("Saturday", "Saturday"),
    ]

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="timetable_entries"
    )

    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="timetable_entries"
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="timetable_entries"
    )

    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
        related_name="timetable_entries"
    )

    day = models.CharField(
        max_length=20,
        choices=DAY_CHOICES
    )

    start_time = models.TimeField()

    end_time = models.TimeField()

    room = models.CharField(
        max_length=100,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["day", "start_time"]

    def __str__(self):
        return (
            f"{self.day} - "
            f"{self.subject.code} "
            f"({self.start_time} - {self.end_time})"
        )
class LeaveRequest(models.Model):

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="leave_requests"
    )

    leave_type = models.CharField(
        max_length=50
    )

    start_date = models.DateField()

    end_date = models.DateField()

    reason = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    applied_at = models.DateTimeField(
        auto_now_add=True
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_leave_requests"
    )

    class Meta:
        ordering = ["-applied_at"]

    def __str__(self):
        return (
            f"{self.student.name} - "
            f"{self.leave_type} - "
            f"{self.status}"
        )
class Complaint(models.Model):

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("In Progress", "In Progress"),
        ("Resolved", "Resolved"),
        ("Rejected", "Rejected"),
    ]

    PRIORITY_CHOICES = [
        ("Low", "Low"),
        ("Medium", "Medium"),
        ("High", "High"),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="complaints"
    )

    title = models.CharField(
        max_length=150
    )

    category = models.CharField(
        max_length=100
    )

    description = models.TextField()

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default="Medium"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    admin_response = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    resolved_at = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student.name} - {self.title}"
class AssignmentSubmission(models.Model):

    STATUS_CHOICES = [
        ("Submitted", "Submitted"),
        ("Evaluated", "Evaluated"),
    ]

    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name="submissions"
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="assignment_submissions"
    )

    submission_file = models.FileField(
        upload_to="assignments/submissions/"
    )

    submitted_at = models.DateTimeField(
        auto_now_add=True
    )

    marks_obtained = models.FloatField(
        null=True,
        blank=True
    )

    feedback = models.TextField(
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Submitted"
    )

    class Meta:
        ordering = ["-submitted_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["assignment", "student"],
                name="unique_assignment_student_submission"
            )
        ]

    def __str__(self):
        return f"{self.assignment.title} - {self.student.name}"
class Notification(models.Model):

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    title = models.CharField(
        max_length=150
    )

    message = models.TextField()

    is_read = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.recipient.username} - {self.title}"
class Exam(models.Model):

    EXAM_TYPE_CHOICES = [
        ("Internal", "Internal"),
        ("Mid Semester", "Mid Semester"),
        ("End Semester", "End Semester"),
        ("Practical", "Practical"),
    ]

    name = models.CharField(max_length=100)

    exam_type = models.CharField(
        max_length=30,
        choices=EXAM_TYPE_CHOICES
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="exams"
    )

    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
        related_name="exams"
    )

    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.name} - {self.course.code} - {self.semester.name}"
class Result(models.Model):

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="results"
    )

    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name="results"
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="results"
    )

    marks_obtained = models.PositiveIntegerField()

    max_marks = models.PositiveIntegerField(default=100)

    def __str__(self):
        return (
            f"{self.student.student_id} - "
            f"{self.exam.name} - "
            f"{self.subject.code}"
        )
class Fee(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Partial", "Partial"),
        ("Paid", "Paid"),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="fees"
    )

    fee_type = models.CharField(max_length=100)

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    paid_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    due_date = models.DateField()

    payment_date = models.DateField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    remarks = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.student.student_id} - {self.fee_type}"
class Notice(models.Model):
    title = models.CharField(max_length=200)

    content = models.TextField()
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notices"
    )

    notice_type = models.CharField(
        max_length=50,
        choices=[
            ("General", "General"),
            ("Academic", "Academic"),
            ("Exam", "Exam"),
            ("Fee", "Fee"),
            ("Event", "Event"),
        ],
        default="General"
    )

    publish_date = models.DateField()

    expiry_date = models.DateField(
        null=True,
        blank=True
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
class Event(models.Model):

    EVENT_TYPE_CHOICES = [
        ("Seminar", "Seminar"),
        ("Workshop", "Workshop"),
        ("Cultural", "Cultural"),
        ("Sports", "Sports"),
        ("Meeting", "Meeting"),
        ("Other", "Other"),
    ]

    title = models.CharField(max_length=150)

    description = models.TextField()

    event_type = models.CharField(
        max_length=50,
        choices=EVENT_TYPE_CHOICES,
        default="Other"
    )

    date = models.DateField()

    time = models.TimeField()

    venue = models.CharField(max_length=150)

    organizer = models.CharField(max_length=100)

    def __str__(self):
        return self.title
class Book(models.Model):

    CATEGORY_CHOICES = [
        ("Programming", "Programming"),
        ("Database", "Database"),
        ("AI/ML", "AI/ML"),
        ("Networking", "Networking"),
        ("Mathematics", "Mathematics"),
        ("General", "General"),
        ("Other", "Other"),
    ]

    title = models.CharField(max_length=200)

    author = models.CharField(max_length=150)

    isbn = models.CharField(
        max_length=20,
        unique=True
    )

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default="General"
    )

    publisher = models.CharField(
        max_length=150,
        blank=True
    )

    total_copies = models.PositiveIntegerField(
        default=1
    )

    available_copies = models.PositiveIntegerField(
        default=1
    )

    shelf_location = models.CharField(
        max_length=50,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.title} - {self.author}"


class BookIssue(models.Model):

    STATUS_CHOICES = [
        ("Issued", "Issued"),
        ("Returned", "Returned"),
        ("Overdue", "Overdue"),
    ]

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="issues"
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="book_issues"
    )

    issue_date = models.DateField()

    due_date = models.DateField()

    return_date = models.DateField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Issued"
    )

    remarks = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.book.title} - {self.student.name}"