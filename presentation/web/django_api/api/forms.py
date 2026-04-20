from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from django import forms
from .models import *


class UserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'group', 'password1', 'password2']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].label = 'Логин'
        self.fields['group'].label = 'Группа'
        self.fields['password1'].label = 'Пароль'
        self.fields['password2'].label = 'Подтверждение пароля'

        self.fields['password1'].help_text = 'Пароль должен быть не менее 8 символов'
        self.fields['password2'].help_text = 'Введите тот же пароль для подтверждения'

        for _, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control',
                'placeholder': field.label
            })

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Пользователь с таким login уже существует!')
        return username

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Пароли не совпадают! Проверьте ввод')
        
        return password2
    
    def save(self, commit=True):
        user = super().save(commit=False) 
        
        if commit:
            user.save()
        return user


class UserAuthForm(AuthenticationForm):
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Логин'})
        )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Пароль'})
        )
    
    error_messages = {
        'invalid_login': 'Неверный login или пароль. Пожалуйста, проверьте правильность ввода.'
    }