from django.contrib import admin
from django.urls import path
from graphene_django.views import GraphQLView
from .schema import schema
from movies import views


urlpatterns = [
    path('', views.weatherAPI, name='movies-home'),
]
