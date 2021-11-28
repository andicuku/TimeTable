from django.contrib.auth.forms import UserCreationForm
from .models import *
from django import forms

from timetable.models import Course


class CreateUserForm(UserCreationForm):
    username = forms.CharField(label='Username', max_length=30, required=True)
    email = forms.EmailField(label='Email', max_length=254, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'department')


class CreateCourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ('start_time', 'end_time', 'day_of_week', 'class_room', 'subject', 'teacher')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['teacher'].queryset = Teacher.objects.none()
