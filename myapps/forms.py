from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import CustomUser, Teacher, Student
import re
from django.core.validators import RegexValidator
from django.contrib.auth import get_user_model
from django import forms
from django.db import transaction
from django.forms import ValidationError

from .models import Teacher, Student


from django import forms

class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=255)
    last_name = forms.CharField(max_length=255)
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=15)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    is_teacher = forms.BooleanField(required=False, label='Вы хотите преподавать?')
    city = forms.CharField(max_length=255)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].validators.append(self.validate_email)
        self.fields['phone_number'].validators.append(self.validate_phone_number)

    def validate_email(self, value):
        email = CustomUser.objects.normalize_email(value)
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже существует.')
        return email

    def validate_phone_number(self, value):
        if CustomUser.objects.filter(phone_number=value).exists():
            raise ValidationError('Пользователь с таким номером телефона уже существует.')
        return value

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Пароли не совпадают')

    def save(self, is_teacher):
        first_name = self.cleaned_data['first_name']
        last_name = self.cleaned_data['last_name']
        email = self.cleaned_data['email']
        phone_number = self.cleaned_data['phone_number']
        is_teacher = self.cleaned_data['is_teacher']
        password = self.cleaned_data['password']
        city = self.cleaned_data['city']

        if is_teacher:
            User = get_user_model()
            user = CustomUser.objects.create_user(
                email=email,
                phone_number=phone_number,
                first_name=first_name,
                last_name=last_name,
                password=password,
                city=city  # Pass the city field when creating a CustomUser
            )
            teacher = Teacher.objects.create(
                user=user,
                teacher_name=first_name,
                teacher_last_name=last_name,
                city=city,
                number_phone=phone_number,
                email=email,
                about='Sample about text'  # Set a default value for the 'about' field
            )
            return teacher
        else:
            User = get_user_model()
            user = CustomUser.objects.create_user(
                email=email,
                phone_number=phone_number,
                first_name=first_name,
                last_name=last_name,
                password=password,
                city=city  # Pass the city field when creating a CustomUser
            )
            student = Student.objects.create(
                user=user,
                email=email,
                phone_number=phone_number,
                first_name=first_name,
                last_name=last_name,
                password=password,
                city=city  # Pass the city field when creating a Student
            )


class UserLoginForm(forms.Form):
    email = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

from django import forms
from myapps.models import CustomUser, CustomUserManager

User = get_user_model()

class CustomUserCreationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    confirm_password = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    is_teacher = forms.BooleanField(required=False, label='Вы хотите преподавать?')

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'phone_number', 'city']

    def clean(self):
        cleaned_data = super().clean()

        email = cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            self.add_error('email', 'Пользователь с таким email уже существует.')

        phone_number = cleaned_data.get('phone_number')
        if CustomUser.objects.filter(phone_number=phone_number).exists():
            self.add_error('phone_number', 'Пользователь с таким номером телефона уже существует.')

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Пароли не совпадают.')

        return cleaned_data

    def save(self, commit=True):
        is_teacher = self.cleaned_data['is_teacher']
        email = self.cleaned_data['email']
        first_name = self.cleaned_data['first_name']
        last_name = self.cleaned_data['last_name']
        phone_number = self.cleaned_data['phone_number']
        password = self.cleaned_data['password']  # Используйте password1 для получения пароля
        city = self.cleaned_data['city']

        user = CustomUser.objects.create_user(
            email=email,
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            password=password,  # Используйте полученный пароль
            city=city
        )

        if is_teacher:
            Teacher.objects.create(
                user=user,
                teacher_name=first_name,
                teacher_last_name=last_name,
                city=city,
                about='Sample about text'
            )
        else:
            Student.objects.create(
                user=user,
                first_name=first_name,
                last_name=last_name,
                city=city,
                about='Sample about text'
            )

        return user
