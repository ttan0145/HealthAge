from django.contrib import admin
from django.urls import path

from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('profile/', views.profile, name='profile'),
    path('lifestyle/', views.lifestyle, name='lifestyle'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('readmore/', views.readmore, name='readmore'),
    path('source/', views.source, name='source'),
    path('stayfit/', views.stayfit, name='stayfit'),
]
