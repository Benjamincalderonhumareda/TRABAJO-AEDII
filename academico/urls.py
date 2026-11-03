from django.urls import path

from . import views


urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("profesor/", views.profesor, name="profesor"),
    path("profesor/alumnos/", views.profesor_alumnos, name="profesor_alumnos"),
    path("profesor/temas/", views.profesor_temas, name="profesor_temas"),
    path("profesor/dudas/", views.profesor_dudas, name="profesor_dudas"),
    path("alumno/", views.alumno, name="alumno"),
    path("alumno/<str:seccion>/", views.alumno_seccion, name="alumno_seccion"),
]
