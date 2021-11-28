from django.urls import path
from .views import *

urlpatterns = [
    path('register/', register_page, name='register'),
    path('login/', login_page, name='login'),
    path('logout/', log_out, name='logout'),
    path('', index, name='base'),
    path('create-course/', CreateCourses.as_view(), name='create-course'),
    path('ajax/load-teachers/', load_teacher, name='ajax_load_teachers')
]
