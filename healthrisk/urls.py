from django.contrib import admin
from django.urls import path

from core import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.index, name="index"),
    path("profile/", views.profile, name="profile"),
    path("lifestyle/", views.lifestyle, name="lifestyle"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("readmore/", views.readmore, name="readmore"),
    path("source/", views.source, name="source"),
    path("stayfit/", views.stayfit, name="stayfit"),
    path("api/cause-of-death/", views.cause_of_death_stats, name="cause_of_death_stats"),
    path("api/stayfit/routine/", views.api_stayfit_routine, name="api_stayfit_routine"),
    path("api/stayfit/reshuffle/", views.api_stayfit_reshuffle, name="api_stayfit_reshuffle"),
]
