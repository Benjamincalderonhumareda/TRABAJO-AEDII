from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect, render

from . import structures
from .forms import AlumnoForm, DniForm, DudaForm, TemaForm
from .models import Alumno as AlumnoModel
from .models import Duda as DudaModel
from .models import Historial as HistorialModel
from .models import Tema as TemaModel


def _avisar_errores(request, form):
    errores = [str(error) for lista in form.errors.values() for error in lista]
    messages.error(request, " ".join(errores))


def _alumnos():
    return list(AlumnoModel.objects.order_by("id"))


def _temas():
    return list(TemaModel.objects.order_by("id"))


def _indice_tema_actual(request, cantidad, clave="tema_indice"):
    if cantidad == 0:
        request.session.pop(clave, None)
        return None

    try:
        indice = int(request.session.get(clave, 0))
    except (TypeError, ValueError):
        indice = 0

    indice = max(0, min(indice, cantidad - 1))
    request.session[clave] = indice
    return indice


def _dudas_pendientes():
    return list(DudaModel.objects.order_by("id"))


def _historial():
    registros = list(HistorialModel.objects.order_by("id"))
    numerados = [
        {"numero": numero, "texto": registro.texto}
        for numero, registro in enumerate(registros, start=1)
    ]
    return list(reversed(numerados))


def inicio(request):
    return render(request, "academico/inicio.html")


def profesor(request):
    resultado_busqueda = None
    dni_busqueda = ""
    temas = _temas()

    if request.method == "POST":
        accion = request.POST.get("accion")

        if accion == "registrar_alumno":
            form = AlumnoForm(request.POST)
            if form.is_valid():
                datos = form.cleaned_data
                if AlumnoModel.objects.filter(dni=datos["dni"]).exists():
                    messages.error(request, "Ya existe un alumno registrado con ese DNI.")
                else:
                    AlumnoModel.objects.create(
                        nombre=datos["nombre"].strip(),
                        dni=datos["dni"],
                        correo=datos["correo"].strip(),
                    )
                    messages.success(request, "Alumno registrado correctamente.")
            else:
                _avisar_errores(request, form)
            return redirect("profesor")

        elif accion == "eliminar_alumno":
            form = DniForm(request.POST)
            if form.is_valid():
                eliminados, _ = AlumnoModel.objects.filter(
                    dni=form.cleaned_data["dni"]
                ).delete()
                if eliminados:
                    messages.success(request, "Alumno eliminado.")
                else:
                    messages.error(request, "No se encontró un alumno con ese DNI.")
            else:
                _avisar_errores(request, form)
            return redirect("profesor")

        elif accion == "registrar_tema":
            form = TemaForm(request.POST)
            if form.is_valid():
                TemaModel.objects.create(nombre=form.cleaned_data["tema"].strip())
                messages.success(request, "Tema agregado al plan de repaso.")
            else:
                _avisar_errores(request, form)
            return redirect("profesor")

        elif accion == "eliminar_tema":
            tema_id = request.POST.get("tema_id")
            try:
                tema = TemaModel.objects.get(pk=tema_id)
            except (TemaModel.DoesNotExist, ValueError, TypeError):
                messages.error(request, "No se encontró el tema que intentas eliminar.")
            else:
                tema.delete()
                messages.success(request, "Tema eliminado.")
            return redirect("profesor")

        elif accion == "responder_duda":
            with transaction.atomic():
                duda = DudaModel.objects.select_for_update().order_by("id").first()
                if duda is None:
                    messages.error(request, "No hay dudas pendientes.")
                else:
                    HistorialModel.objects.create(texto=f"Atendida: {duda.texto}")
                    duda.delete()
                    messages.success(request, f"Duda atendida: {duda.texto}")
            return redirect("profesor")

        else:
            messages.error(request, "No se reconoció la acción solicitada.")

    elif request.method == "GET":
        dni_busqueda = request.GET.get("dni", "").strip()
        if dni_busqueda:
            if len(dni_busqueda) == 8 and dni_busqueda.isdigit():
                resultado_busqueda = AlumnoModel.objects.filter(
                    dni=dni_busqueda
                ).first()
            else:
                messages.error(request, "Ingresa un DNI válido de 8 dígitos.")

    temas = _temas()
    context = {
        "alumnos": _alumnos(),
        "temas": temas,
        "dudas": _dudas_pendientes(),
        "form_alumno": AlumnoForm(),
        "form_tema": TemaForm(),
        "form_dni": DniForm(),
        "resultado_busqueda": resultado_busqueda,
        "dni_busqueda": dni_busqueda,
    }
    return render(request, "academico/profesor.html", context)


def alumno(request):
    dni_sesion = request.session.get("alumno_dni")
    alumno_actual = (
        AlumnoModel.objects.filter(dni=dni_sesion).first() if dni_sesion else None
    )
    if dni_sesion and alumno_actual is None:
        request.session.pop("alumno_dni", None)
        dni_sesion = None
    temas = _temas()
    indice_tema = _indice_tema_actual(
        request,
        len(temas),
        clave="alumno_tema_indice",
    )

    if request.method == "POST":
        accion = request.POST.get("accion")

        if accion == "iniciar_sesion":
            form = DniForm(request.POST)
            if form.is_valid():
                alumno_encontrado = AlumnoModel.objects.filter(
                    dni=form.cleaned_data["dni"]
                ).first()
                if alumno_encontrado is None:
                    messages.error(request, "El DNI no está registrado. Pide acceso a tu profesor.")
                else:
                    request.session["alumno_dni"] = alumno_encontrado.dni
                    return redirect("alumno")
            else:
                _avisar_errores(request, form)

        elif accion == "cerrar_sesion":
            request.session.pop("alumno_dni", None)
            return redirect("alumno")

        elif alumno_actual is None:
            messages.error(request, "Primero inicia sesión con un DNI registrado.")

        elif accion in {"tema_anterior", "tema_siguiente"}:
            if indice_tema is None:
                messages.error(request, "El profesor aún no agregó temas.")
            elif accion == "tema_anterior":
                request.session["alumno_tema_indice"] = max(0, indice_tema - 1)
            else:
                request.session["alumno_tema_indice"] = min(
                    len(temas) - 1,
                    indice_tema + 1,
                )

        elif accion == "buscar_alumno":
            form = DniForm(request.POST)
            if form.is_valid():
                resultado = AlumnoModel.objects.filter(
                    dni=form.cleaned_data["dni"]
                ).first()
                if resultado is None:
                    messages.error(request, "No se encontró al alumno.")
                else:
                    messages.info(
                        request,
                        f"Alumno: {resultado.nombre} | Correo: {resultado.correo}",
                    )
            else:
                _avisar_errores(request, form)

        elif accion == "enviar_duda":
            form = DudaForm(request.POST)
            if form.is_valid():
                DudaModel.objects.create(texto=form.cleaned_data["duda"].strip())
                messages.success(request, "Tu duda se envió a la cola del profesor.")
            else:
                _avisar_errores(request, form)

        elif accion == "eliminar_historial":
            eliminada = HistorialModel.objects.order_by("-id").first()
            if eliminada is None:
                messages.error(request, "El historial está vacío.")
            else:
                messages.success(request, f"Se eliminó del historial: {eliminada.texto}")
                eliminada.delete()

        else:
            messages.error(request, "No se reconoció la acción solicitada.")

        return redirect("alumno")

    lista_temas = structures.ListaDoble()
    for tema in temas:
        lista_temas.insertar_final(tema.nombre)
    nodo_tema_actual = (
        lista_temas.obtener_por_indice(indice_tema)
        if indice_tema is not None
        else None
    )
    return render(
        request,
        "academico/alumno.html",
        {
            "alumno": alumno_actual,
            "tema_actual": nodo_tema_actual.dato if nodo_tema_actual else None,
            "tema_posicion": indice_tema + 1 if indice_tema is not None else 0,
            "cantidad_temas": len(temas),
            "hay_tema_anterior": indice_tema is not None and indice_tema > 0,
            "hay_tema_siguiente": (
                indice_tema is not None and indice_tema < len(temas) - 1
            ),
            "historial": list(_historial()),
            "form_dni": DniForm(),
            "form_duda": DudaForm(),
        },
    )
