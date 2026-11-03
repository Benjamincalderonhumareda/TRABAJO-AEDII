from django import forms


class AlumnoForm(forms.Form):
    nombre = forms.CharField(label="Nombre completo", max_length=120)
    dni = forms.RegexField(
        label="DNI",
        regex=r"^\d{8}$",
        error_messages={"invalid": "El DNI debe tener exactamente 8 dígitos."},
        widget=forms.TextInput(attrs={"inputmode": "numeric", "maxlength": "8"}),
    )
    correo = forms.EmailField(label="Correo electrónico")


class DniForm(forms.Form):
    dni = forms.RegexField(
        label="DNI",
        regex=r"^\d{8}$",
        error_messages={"invalid": "Ingresa un DNI válido de 8 dígitos."},
        widget=forms.TextInput(attrs={"inputmode": "numeric", "maxlength": "8"}),
    )


class TemaForm(forms.Form):
    tema = forms.CharField(label="Nombre del tema", max_length=160)


class DudaForm(forms.Form):
    duda = forms.CharField(label="Tu duda", max_length=500)
