from django.contrib.auth.decorators import login_required

from .models import Teacher, CustomUser, Message, Task, MediaFile
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, RegistrationForm
from django.http import JsonResponse
from django.forms.utils import ErrorDict
from django.conf import settings
from django.contrib.auth import login
from django.shortcuts import redirect
from .models import CustomUser, Student, Teacher, Lesson
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from django.db import transaction

from django.contrib.auth.views import LogoutView
from django.shortcuts import reverse

from django.contrib.auth.views import LoginView

class CustomLoginView(LoginView):
    template_name = 'login.html'
    success_url = 'home'  # URL, на который будет перенаправлен пользователь после успешного входа



class CustomLogoutView(LogoutView):
    def get_next_page(self):
        return reverse('login')
class HomePageView(TemplateView):
    template_name = 'home.html'



def teacher_dashboard(request):
    teacher = Teacher.objects.get(user=request.user)
    lessons = teacher.get_lessons()
    messages = teacher.get_messages()
    context = {
        'teacher': teacher,
        'lessons': lessons,
        'messages': messages
    }
    return render(request, 'teacher_dashboard.html', context)



import logging

logger = logging.getLogger(__name__)




@login_required
def student_view(request):
    task_sent = False
    teachers = Teacher.objects.filter(is_verified=True)
    user = request.user  # Получение текущего пользователя
    print(teachers, user, request.method)
    if request.method == 'POST':
        teacher_id = request.POST.get('teacher_id')
        task_content = request.POST.get('task_content')
        print(task_content)
        if teacher_id and task_content:
            teacher = Teacher.objects.get(user_id=teacher_id)
            task = Task.objects.create(content=task_content, student_id=user.id, teacher=teacher.user)
            task_sent = True
            task.save()  # Сохранение задачи в базе данных
            print('задача сохранена')
            response_data = {'success': True, 'message': 'Задача успешно отправлена.'}
            return JsonResponse(response_data)

    # selected_teacher_id = request.GET.get('teacher_id')
    # messages = Message.objects.filter(teacher_id=selected_teacher_id, student_id=user.id).order_by('timestamp')
    #
    lessons = Lesson.objects.filter(student_id=user.id)

    return render(request, 'student_room.html', {'user': user, 'teachers': teachers, 'lessons': lessons, 'messages': messages, 'task_sent': task_sent})



@login_required
def teacher_view(request):
    teacher_id = request.user.teacher.user_id

    submitted_tasks = Task.objects.filter(teacher_id=teacher_id, is_approved=False)

    approved_tasks = Task.objects.filter(teacher_id=teacher_id, is_approved=True)
    lessons = Lesson.objects.filter(task__teacher_id=teacher_id, is_accepted=True)
    print(teacher_id)
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        task = get_object_or_404(Task, id=task_id)

        # Обновление задачи
        task.is_approved = True
        task.save()
        student = task.student

        # Создание или обновление урока
        lesson, created = Lesson.objects.get_or_create(task=task, student=student, teacher_id=teacher_id)
        lesson.content = task.content  # Используйте значение task.task_content
        lesson.is_accepted = True
        lesson.save()
        print(lesson)
        return redirect('teacher_room')

    return render(request, 'teacher_room.html', {
        'submitted_tasks': submitted_tasks,
        'approved_tasks': approved_tasks,
        'lessons': lessons,  # Добавлено поле lessons в контекст
    })

    # Обработка сохранения медиафайлов для уроков
    media_file = request.FILES.get('media_file')
    if media_file:
        media = MediaFile(file=media_file)
        media.save()

    # Обработка связи с учениками через чаты
    message_content = request.POST.get('message_content')
    if message_content:
        message = Message(teacher=request.user, content=message_content)
        message.save()

    # Перезагрузка текущей страницы для обновления данных
    return redirect('teacher_room')

    # Получение данных для отображения
    #tasks = Lesson.objects.filter(teacher=request.user.teacher)
    active_students = Student.objects.filter(lesson__teacher=request.user.teacher, lesson__is_accepted=True).distinct()

    return render(request, 'teacher_room.html', {'tasks': tasks, 'active_students': active_students})

def verify_task(request, id):
    task = Task.objects.get(id=id)
    task.is_approved = True

    return redirect('teacher_room')

def about_view(request):
    return render(request, 'about.html')


def registration_view(request):

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_teacher = form.cleaned_data['is_teacher']
            user.save()  # Сохраните изменения модели CustomUser
            login(request, user)
            if form.cleaned_data['is_teacher']:
                success_message = "Регистрация учителя прошла успешно."
                user_type = 'teacher'
                user.is_teacher = form.cleaned_data['is_teacher']
                messages.success(request, success_message)
                redirect_url = settings.LOGIN_REDIRECT_URL
                print(redirect_url)
            else:
                success_message = "Регистрация студента прошла успешно."
                user_type = 'student'
                messages.success(request, success_message)
                redirect_url = settings.STUDENT_LOGIN_REDIRECT_URL
                print(redirect_url)
            response_data = {
                'success': True,
                'user_type': user_type,
                'redirect_url': redirect_url,
                'success_message': success_message
            }

            return JsonResponse(response_data)
        else:
            # Преобразуем сложные массивы ошибок в простой словарь
            error_messages = {}
            for field, errors in form.errors.items():
                error_messages[field] = [error for error in errors]

            return JsonResponse({'success': False, 'errors': error_messages})

    else:
        form = CustomUserCreationForm(initial={'is_teacher': False})

    context = {'form': form}
    return render(request, 'registration_page.html', context)


def success_view(request):
    return render(request, 'success.html')


def success_page_view(request, user_type):
    context = {'user_type': user_type}
    return render(request, 'success_page.html', context)
