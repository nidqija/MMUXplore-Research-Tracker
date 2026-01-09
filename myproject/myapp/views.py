
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login 
from django.conf import settings


def index(request):
    return render(request , 'home.html')

def user_signup(request):
    return render(request , 'signup.html')

def user_signin(request):
    return render(request , 'signin.html')



