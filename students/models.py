from django.db import models


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

    def __str__(self):
        return f"{self.employee_id} - {self.name}"


class Student(models.Model):
    student_id = models.CharField(max_length=20, unique=True)
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