import re
 
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import EnrollmentRequest, Program, ServiceReview


class SignupForm(forms.ModelForm):
    phone = forms.CharField(label='Телефон', max_length=20)
    password = forms.CharField(label='Пароль', min_length=8, widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'password', 'email']
        labels = {'username': 'Логин', 'email': 'Email'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')

    def clean_username(self):
        username = self.cleaned_data['username']
        if len(username) < 4:
            raise ValidationError('Логин должен содержать минимум 4 символа.')
        if len(username) > 6:
            raise ValidationError('Логин должен быть не длиннее 6 символов.')
        if not re.fullmatch(r'[A-Za-z0-9]+', username):
            raise ValidationError('Допустимы только латинские буквы и цифры.')
        if User.objects.filter(username=username).exists():
            raise ValidationError('Пользователь с таким логином уже есть.')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if not email:
            raise ValidationError('Email обязателен.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            user.learner_profile.phone = self.cleaned_data['phone']
            user.learner_profile.save(update_fields=['phone'])
        return user


class SigninForm(forms.Form):
    username = forms.CharField(label='Логин')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')

    def clean(self):
        cleaned = super().clean()
        username = cleaned.get('username')
        password = cleaned.get('password')
        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise ValidationError('Неверный логин или пароль.')
            cleaned['user'] = user
        return cleaned


class EnrollmentForm(forms.ModelForm):
    preferred_start = forms.DateField(
        label='Дата начала обучения',
        input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(attrs={'type': 'date'}),
    )

    class Meta:
        model = EnrollmentRequest
        fields = ['program', 'preferred_start', 'payment']
        labels = {'program': 'Курс', 'payment': 'Способ оплаты'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['program'].queryset = Program.objects.all()
        self.fields['preferred_start'].widget.attrs['min'] = timezone.localdate().isoformat()
        for field_name, field in self.fields.items():
            if field_name == 'program' or isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault('class', 'form-select')
            else:
                field.widget.attrs.setdefault('class', 'form-control')

    def clean_preferred_start(self):
        value = self.cleaned_data['preferred_start']
        if value < timezone.localdate():
            raise ValidationError('Дата начала не может быть раньше сегодняшнего дня.')
        return value


class ServiceReviewForm(forms.ModelForm):
    class Meta:
        model = ServiceReview
        fields = ['score', 'comment']
        labels = {'score': 'Оценка', 'comment': 'Ваш отзыв'}
        widgets = {
            'score': forms.Select(attrs={'class': 'form-select'}, choices=[(number, number) for number in range(1, 6)]),
            'comment': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }


class ProgramForm(forms.ModelForm):
    class Meta:
        model = Program
        fields = ['name', 'summary', 'hours']
        labels = {
            'name': 'Название курса',
            'summary': 'Описание',
            'hours': 'Количество часов',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'summary': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'hours': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }
