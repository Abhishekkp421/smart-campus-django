from django import forms

from .models import Student, Faculty


class StudentForm(forms.ModelForm):

    class Meta:
        model = Student

        fields = [
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
        ]

        widgets = {
            "date_of_birth": forms.DateInput(
                attrs={"type": "date"}
            ),
            "admission_date": forms.DateInput(
                attrs={"type": "date"}
            ),
            "address": forms.Textarea(
                attrs={"rows": 4}
            ),
        }


class FacultyForm(forms.ModelForm):

    class Meta:
        model = Faculty

        fields = [
            "employee_id",
            "name",
            "email",
            "phone",
            "department",
            "designation",
        ]