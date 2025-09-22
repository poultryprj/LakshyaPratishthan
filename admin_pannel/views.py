import os
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import requests
from datetime import datetime
import calendar

def login(request):
    return HttpResponse("<h1>Login Page Working!</h1>")
    

# def logout(request):
#     request.session.flush()  # clears all session data
#     messages.success(request, "You have successfully signed out")
#     return redirect('login')

# def dashboard(request):
#     return render(request, 'dashboard.html')