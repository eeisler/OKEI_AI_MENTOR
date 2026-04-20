from datetime import datetime
import json

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.shortcuts import get_object_or_404, redirect, render
from . import forms

from django.contrib.auth import login, authenticate, logout
from .models import *
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

def welcome(request):
    return render(request, 'welcome.html')

def register(request):
    if request.method == 'POST':
        form = forms.UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('welcome')  
    else:
        form = forms.UserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_user(request):
    if request.method == 'POST':
        form = forms.UserAuthForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()  
            if user is not None:
                login(request, user)
                return redirect('welcome')
    else:
        form = forms.UserAuthForm()
    return render(request, 'login.html', {'form': form})

def logout_user(request):
    if request.method == 'POST':
        logout(request)
        return redirect('welcome')
    else:
        return redirect('welcome')

@login_required
def chat(request):
    dialogs = Dialog.objects.filter(user_id=request.user).order_by('user_message_time')
    
    if request.method == 'POST':
        user_message = request.POST.get('user_message', '')
        
        if user_message:
            ai_response = f"Вы написали: '{user_message}'. Это заглушка. Скоро здесь будет настоящий ИИ-ментор!"
            
            dialog = Dialog(
                user_id=request.user,
                user_message=user_message,
                ai_response=ai_response,
                user_message_time=datetime.now(),
                ai_response_time=datetime.now()
            )
            dialog.save()
    
    return render(request, 'chat.html', {'dialogs': dialogs})
