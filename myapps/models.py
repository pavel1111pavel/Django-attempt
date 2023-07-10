import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.urls import reverse

2 / 2


from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.db import models
from django.urls import reverse
import uuid

class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, email, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('The phone number must be set')
        if not email:
            raise ValueError('The email field must be set')
        email = self.normalize_email(email)

        extra_fields.setdefault('is_teacher', False)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        user = self.model(phone_number=phone_number, email=email, **extra_fields)
        user.set_password(password)  # Set the user's password
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, email, password=None, **extra_fields):
        extra_fields.setdefault('is_teacher', False)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(phone_number, email, password, **extra_fields)

    def normalize_email(self, email):
        """
        Normalize the email address by lowercasing the domain part of it.
        """
        email_parts = email.split('@')
        if len(email_parts) == 2:
            email_parts[1] = email_parts[1].lower()
            email = '@'.join(email_parts)
        return email

class CustomUser(AbstractBaseUser, PermissionsMixin):
    is_teacher = models.BooleanField(default=False)
    email = models.EmailField(unique=True, null=False)
    is_email_verified = models.BooleanField(default=False)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15, unique=True, null=False)
    city = models.CharField(max_length=255)
    unique_user_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']
    USERNAME_FIELD = 'phone_number'

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        return self.first_name

    def get_absolute_url(self):
        return reverse('user_detail', args=[str(self.user_id)])


class Student(models.Model):
    user = models.OneToOneField('myapps.CustomUser', on_delete=models.CASCADE, primary_key=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    city = models.CharField(max_length=255, default=None)
    about = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        self.user.save()  # Сохранение связанного объекта CustomUser
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.get_full_name()

    class Meta:
        db_table = 'myapps_student'

class Teacher(models.Model):
    user = models.OneToOneField('myapps.CustomUser', on_delete=models.CASCADE, primary_key=True)

    teacher_name = models.CharField(max_length=100)
    teacher_last_name = models.CharField(max_length=100)
    city = models.CharField(max_length=255)
    about = models.CharField(max_length=255)
    is_verified = models.BooleanField(default=False)
    students = models.ManyToManyField('myapps.Student', related_name='teachers', through='myapps.Lesson')
    # Добавляем ManyToMany связь с моделью Student через промежуточную модель Lesson
    def save(self, *args, **kwargs):
        self.user.save()  # Сохранение связанного объекта CustomUser
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.get_full_name()

    def get_lessons(self):
        return Lesson.objects.filter(teacher=self)

    def get_messages(self):
        return Message.objects.filter(teacher=self)

    class Meta:
        db_table = 'myapps_teacher'


class Classroom(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    date_joined = models.DateField()

class MediaFile(models.Model):
    file = models.ImageField(upload_to='media_files/')
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name

class Task(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='tasks')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    def __str__(self):
        return self.content

class Lesson(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    is_accepted = models.BooleanField(default=False)  # Флаг принятия задачи учителем

    def __str__(self):
        return f"Lesson {self.pk}"


class Message(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From: {self.sender.email} To: {self.lesson.task.teacher.teacher_name}"


