from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, HttpResponse
from django.views import generic
from .forms import CreateCourseForm, CreateUserForm

# Create your views here.
from .models import Course, Subject, Teacher


@login_required(login_url='login')
def index(request):
    user_courses = request.user.department.subjects.all()
    context = {'courses': user_courses}
    return render(request, 'base.html', context=context)


def register_page(request):
    if request.user.is_authenticated:
        return render(request, 'base.html')

    user_form = CreateUserForm()
    if request.method == "POST":
        user_form = CreateUserForm(request.POST)
        if user_form.is_valid():
            user_form.save()
            username = user_form.cleaned_data.get('username')
            messages.success(request, "Account created for " + username)
            return redirect("login")

    context = {'form': user_form}
    return render(request, 'register.html', context)


def login_page(request):
    if request.user.is_authenticated:
        return render(request, 'base.html')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("base")
        else:
            messages.info(request, "Username or password is incorrect")
    return render(request, 'login.html')


def log_out(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect("login")


class CreateCourses(generic.CreateView):
    model = Course
    template_name = 'create_course.html'
    success_url = "base"
    form_class = CreateCourseForm

    # def get(self, request, *args, **kwargs):
    #     return (render(request, self.template_name, {'form': self.form_class()}))

    def get_context_data(self, **kwargs):
        context = super(CreateCourses, self).get_context_data(**kwargs)
        subject = self.request.GET.get('subject')
        if subject:
            context.get("form")['teacher'].field.choices = list(self.request.user.department.teachers.filter(
                subjects=subject))

        return context


def load_teacher(request):
    subject = request.GET.get('subject')
    s = ""
    if subject:
        s = Subject.objects.get(id=subject)
    if s:
        teachers = s.teacher.all()
    else:
        teachers = Teacher.objects.none()
    return render(request, 'dropdown.html', {'teachers': teachers})
