from django.urls import path

from . import views


urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("profesor/", views.profesor, name="profesor"),
    path("alumno/", views.alumno, name="alumno"),
]
