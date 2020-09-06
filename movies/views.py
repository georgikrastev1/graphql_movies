import requests
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def weatherAPI(request):
    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&APPID=d7f3c8d25586e840fb2703b4858f4c59'
    city="Sofia"
    r = requests.get(url.format(city)).json()
    print(r)
    return HttpResponse("Hello World")