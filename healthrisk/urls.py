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

    # Work 1: cause of death statistics by age and gender.
    path('api/cause-of-death/', views.cause_of_death_stats,
         name='cause_of_death_stats'),
]
