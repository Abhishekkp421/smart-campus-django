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
class StudentProfileForm(forms.ModelForm):

    class Meta:
        model = Student

        fields = [
            "name",
            "email",
            "phone",
            "date_of_birth",
            "gender",
            "address",
        ]

        widgets = {
            "date_of_birth": forms.DateInput(
                attrs={
                    "type": "date"
                }
            ),

            "address": forms.Textarea(
                attrs={
                    "rows": 4
                }
            ),
        }
class FacultyProfileForm(forms.ModelForm):

    class Meta:
        model = Faculty

        fields = [
            "name",
            "email",
            "phone",
            "designation",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": "Enter your name"
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "placeholder": "Enter your email"
                }
            ),

            "phone": forms.TextInput(
                attrs={
                    "placeholder": "Enter your phone number"
                }
            ),

            "designation": forms.TextInput(
                attrs={
                    "placeholder": "Enter your designation"
                }
            ),
        }
from django.contrib.auth.forms import PasswordChangeForm
class FacultySubjectMappingForm(forms.ModelForm):
    class Meta:
        model = Faculty
        fields = ["subjects"]
        widgets = {
            "subjects": forms.CheckboxSelectMultiple()
        }