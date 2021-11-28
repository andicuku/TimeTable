from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from model_utils import Choices
from .utils import TrackedModel

# Create your models here.

professors_titles = Choices(
    (0, 'professor', 'Professor'),
    (1, 'associate_professor', 'Associate Professor'),
    (2, 'assistant_professor', 'Assistant Professor'),
    (3, 'lecturer', 'Lecturer'),
    (4, 'post_doc', 'Post Doc'),
    (5, 'phd_student', 'PhD Student'),
    (6, 'other', 'Other')
)

days_of_week = Choices(
    (0, 'monday', 'Monday'),
    (1, 'tuesday', 'Tuesday'),
    (2, 'wednesday', 'Wednesday'),
    (3, 'thursday', 'Thursday'),
    (4, 'friday', 'Friday'),
)

subject_types = Choices(
    (0, 'compulsory', 'Compulsory'),
    (1, 'elective_lecture', 'Elective Lecture'),
)

lessons_start_hours = Choices(
    (0, '8:45', '8:45'),
    (1, '9:45', '9:45'),
    (2, '10:45', '10:45'),
    (3, '11:45', '11:45'),
    (4, '12:45', '12:45'),
    (5, '13:45', '13:45'),
    (6, '14:45', '14:45'),
    (7, '15:45', '15:45'),
    (8, '16:45', '16:45'),
    (9, '17:45', '17:45'),
    (10, '18:45', '18:45'),
)
lessons_end_hours = Choices(
    (1, '9:30', '9:30'),
    (2, '10:30', '10:30'),
    (3, '11:30', '11:30'),
    (4, '12:30', '12:30'),
    (5, '13:30', '13:30'),
    (6, '14:30', '14:30'),
    (7, '15:30', '15:30'),
    (8, '16:30', '16:30'),
    (9, '17:30', '17:30'),
    (10, '18:30', '18:30'),
    (11, '19:30', '19:30')
)


def generate_random_code():
    import random, string
    while True:
        code = ''.join(random.choice(string.digits) for _ in range(3))
        if not ClassRoom.objects.filter(name=code):
            break
    return code


class Faculty(TrackedModel):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Faculty'
        verbose_name_plural = 'Faculties'


class Building(TrackedModel):
    name = models.CharField(max_length=100, unique=True)
    location = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Buildings'


class ClassRoom(TrackedModel):
    name = models.CharField(max_length=100, blank=True, null=True)
    capacity = models.IntegerField()
    building = models.ForeignKey(Building, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.name:
            self.name = f"{self.building.name[0]}{generate_random_code()}"
        super().save()

    class Meta:
        verbose_name_plural = 'Class Rooms'


class Department(TrackedModel):
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=10)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Departments'


class Teacher(TrackedModel):
    first_name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    initials = models.CharField(max_length=10, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='teachers')

    def __str__(self):
        return self.first_name + ' ' + self.surname

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.initials = self.first_name[0] + "." + self.surname[0]
        super().save()


class Subject(TrackedModel):
    name = models.CharField(max_length=100)
    capacity = models.IntegerField()
    credits = models.IntegerField()
    lab = models.BooleanField(default=False)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='subjects')
    teacher = models.ManyToManyField(Teacher, related_name="subjects")
    subject_type = models.IntegerField(choices=subject_types)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('name', 'department')
        verbose_name_plural = 'Subjects'


class Course(TrackedModel):
    start_time = models.IntegerField(choices=lessons_start_hours)
    end_time = models.IntegerField(choices=lessons_end_hours)
    day_of_week = models.IntegerField(choices=days_of_week, default=0)
    duration = models.IntegerField(blank=True, null=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    class_room = models.ForeignKey(ClassRoom, on_delete=models.CASCADE)
    teacher = models.ManyToManyField(to="timetable.Teacher", related_name='courses')

    def __str__(self):
        return self.subject.name

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.department = self.subject.department
        self.duration = self.end_time - self.start_time
        if int(self.start_time) > int(self.end_time):
            raise ValidationError("Start time cannot be greater than end time")
        super().save()

    class Meta:
        verbose_name_plural = 'Classes'
        unique_together = [
            ('start_time', 'end_time', 'day_of_week', 'subject', 'class_room'),
            ('subject', 'start_time', 'day_of_week', 'end_time'),
            ("subject", "day_of_week")
        ]


class User(AbstractUser):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
