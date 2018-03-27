from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def code_of_conduct(request):
    return render(request, 'code-of-conduct.html')
