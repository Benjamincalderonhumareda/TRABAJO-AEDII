from django.db import models


class Alumno(models.Model):
    nombre = models.CharField(max_length=120)
    dni = models.CharField(max_length=8, unique=True)
    correo = models.EmailField()

    def __str__(self):
        return f"{self.nombre} ({self.dni})"


class Tema(models.Model):
    nombre = models.CharField(max_length=160)

    def __str__(self):
        return self.nombre


class Duda(models.Model):
    texto = models.CharField(max_length=500)

    def __str__(self):
        return self.texto


class Historial(models.Model):
    texto = models.CharField(max_length=500)

    def __str__(self):
        return self.texto
