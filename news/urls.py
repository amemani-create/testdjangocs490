from django.contrib import admin
from django.urls import path
from news.views import newsPaper
urlpatterns = [
    path('', newsPaper, name ='news'),

]