from django.shortcuts import render


def index(request):
    return render(request, 'core/index.html')

def profile(request):
    return render(request, 'core/profile.html')

def lifestyle(request):
    return render(request, 'core/lifestyle.html')

def dashboard(request):
    return render(request, 'core/dashboard.html')

def readmore(request):
    return render(request, 'core/readmore.html')

def source(request):
    return render(request, 'core/source.html')

def stayfit(request):
    return render(request, 'core/stayfit.html')