from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect, render

from . import structures
from .forms import AlumnoForm, DniForm, DudaForm, TemaForm
from .models import Alumno as AlumnoModel
from .models import Duda as DudaModel
from .models import Historial as HistorialModel
from .models import Tema as TemaModel


PROFESOR_NAV = [
    {"label": "Alumnos", "url": "profesor_alumnos", "seccion": "alumnos"},
    {"label": "Temas", "url": "profesor_temas", "seccion": "temas"},
    {"label": "Dudas pendientes", "url": "profesor_dudas", "seccion": "dudas"},
]
ALUMNO_NAV = [
    {"label": "Temas", "url": "alumno_seccion", "seccion": "temas"},
    {"label": "Enviar duda", "url": "alumno_seccion", "seccion": "dudas"},
    {"label": "Buscar alumno", "url": "alumno_seccion", "seccion": "buscar"},
    {"label": "Historial", "url": "alumno_seccion", "seccion": "historial"},
]


def _avisar_errores(request, form):
    errores = [str(error) for lista in form.errors.values() for error in lista]
    messages.error(request, " ".join(errores))


def _alumnos():
    return list(AlumnoModel.objects.order_by("id"))


def _temas():
    return list(TemaModel.objects.order_by("id"))


def _indice_tema_actual(request, cantidad):
    if cantidad == 0:
        request.session.pop("alumno_tema_indice", None)
        return None

    try:
        indice = int(request.session.get("alumno_tema_indice", 0))
    except (TypeError, ValueError):
        indice = 0

    indice = max(0, min(indice, cantidad - 1))
    request.session["alumno_tema_indice"] = indice
    return indice


def _nodo_tema_en_indice(lista, indice):
    if indice < 0 or indice >= lista.tam:
        return None

    if indice <= lista.tam // 2:
        nodo = lista.cabecera
        for _ in range(indice):
            nodo = nodo.sig
        return nodo

    nodo = lista.cola
    for _ in range(lista.tam - indice - 1):
        nodo = nodo.ant
    return nodo


def _dudas_pendientes():
    return list(DudaModel.objects.order_by("id"))


def _historial():
    registros = list(HistorialModel.objects.order_by("id"))
    numerados = [
        {"numero": numero, "texto": registro.texto}
        for numero, registro in enumerate(registros, start=1)
    ]
    return list(reversed(numerados))


def _profesor_nav_context(seccion):
    return {
        "nav_items": PROFESOR_NAV,
        "active_section": seccion,
        "nav_role": "profesor",
    }


def _alumno_actual(request):
    dni = request.session.get("alumno_dni")
    alumno = AlumnoModel.objects.filter(dni=dni).first() if dni else None
    if dni and alumno is None:
        request.session.pop("alumno_dni", None)
    return alumno


def _alumno_context(alumno, seccion):
    return {
        "alumno": alumno,
        "nav_items": ALUMNO_NAV if alumno else [],
        "active_section": seccion,
        "nav_role": "alumno",
    }


def inicio(request):
    return render(request, "academico/inicio.html")


def profesor(request):
    return render(
        request,
        "academico/profesor.html",
        {
            **_profesor_nav_context("inicio"),
            "seccion": "inicio",
            "cantidad_alumnos": AlumnoModel.objects.count(),
            "cantidad_temas": TemaModel.objects.count(),
            "cantidad_dudas": DudaModel.objects.count(),
        },
    )


def profesor_alumnos(request):
    resultado_busqueda = None
    dni_busqueda = ""

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
        else:
            messages.error(request, "No se reconoció la acción solicitada.")
        return redirect("profesor_alumnos")

    dni_busqueda = request.GET.get("dni", "").strip()
    if dni_busqueda:
        if len(dni_busqueda) == 8 and dni_busqueda.isdigit():
            resultado_busqueda = AlumnoModel.objects.filter(dni=dni_busqueda).first()
        else:
            messages.error(request, "Ingresa un DNI válido de 8 dígitos.")

    context = {
        **_profesor_nav_context("alumnos"),
        "seccion": "alumnos",
        "alumnos": _alumnos(),
        "form_alumno": AlumnoForm(),
        "form_dni": DniForm(),
        "resultado_busqueda": resultado_busqueda,
        "dni_busqueda": dni_busqueda,
    }
    return render(request, "academico/profesor.html", context)


def profesor_temas(request):
    if request.method == "POST":
        accion = request.POST.get("accion")
        if accion == "registrar_tema":
            form = TemaForm(request.POST)
            if form.is_valid():
                TemaModel.objects.create(nombre=form.cleaned_data["tema"].strip())
                messages.success(request, "Tema agregado al plan de repaso.")
            else:
                _avisar_errores(request, form)
        elif accion == "eliminar_tema":
            tema_id = request.POST.get("tema_id")
            try:
                tema = TemaModel.objects.get(pk=tema_id)
            except (TemaModel.DoesNotExist, ValueError, TypeError):
                messages.error(request, "No se encontró el tema que intentas eliminar.")
            else:
                tema.delete()
                messages.success(request, "Tema eliminado.")
        else:
            messages.error(request, "No se reconoció la acción solicitada.")
        return redirect("profesor_temas")

    context = {
        **_profesor_nav_context("temas"),
        "seccion": "temas",
        "temas": _temas(),
        "form_tema": TemaForm(),
    }
    return render(request, "academico/profesor.html", context)


def profesor_dudas(request):
    if request.method == "POST":
        if request.POST.get("accion") != "responder_duda":
            messages.error(request, "No se reconoció la acción solicitada.")
            return redirect("profesor_dudas")

        with transaction.atomic():
            duda = DudaModel.objects.select_for_update().order_by("id").first()
            if duda is None:
                messages.error(request, "No hay dudas pendientes.")
            else:
                HistorialModel.objects.create(texto=f"Atendida: {duda.texto}")
                duda.delete()
                messages.success(request, f"Duda atendida: {duda.texto}")
        return redirect("profesor_dudas")

    return render(
        request,
        "academico/profesor.html",
        {
            **_profesor_nav_context("dudas"),
            "seccion": "dudas",
            "dudas": _dudas_pendientes(),
        },
    )


def alumno(request):
    alumno = _alumno_actual(request)
    if request.method == "POST":
        accion = request.POST.get("accion")
        if accion == "iniciar_sesion":
            form = DniForm(request.POST)
            if form.is_valid():
                alumno = AlumnoModel.objects.filter(
                    dni=form.cleaned_data["dni"]
                ).first()
                if alumno is None:
                    messages.error(request, "El DNI no está registrado. Pide acceso a tu profesor.")
                else:
                    request.session["alumno_dni"] = alumno.dni
                    return redirect("alumno")
            else:
                _avisar_errores(request, form)
        elif accion == "cerrar_sesion":
            request.session.pop("alumno_dni", None)
            return redirect("alumno")
        else:
            messages.error(request, "No se reconoció la acción solicitada.")

    return render(
        request,
        "academico/alumno.html",
        {
            **_alumno_context(alumno, "inicio" if alumno else None),
            "seccion": "inicio",
            "form_dni": DniForm(),
        },
    )


def alumno_seccion(request, seccion):
    alumno = _alumno_actual(request)
    if alumno is None:
        messages.error(request, "Primero inicia sesión con un DNI registrado.")
        return redirect("alumno")

    secciones_validas = {"temas", "dudas", "buscar", "historial"}
    if seccion not in secciones_validas:
        messages.error(request, "No se encontró ese apartado.")
        return redirect("alumno")

    contexto = {
        **_alumno_context(alumno, seccion),
        "seccion": seccion,
    }

    if request.method == "POST":
        accion = request.POST.get("accion")
        if seccion == "temas" and accion in {"tema_anterior", "tema_siguiente"}:
            cantidad = TemaModel.objects.count()
            indice = _indice_tema_actual(request, cantidad)
            if indice is not None and accion == "tema_anterior":
                request.session["alumno_tema_indice"] = max(0, indice - 1)
            elif indice is not None:
                request.session["alumno_tema_indice"] = min(cantidad - 1, indice + 1)
        elif seccion == "dudas" and accion == "enviar_duda":
            form = DudaForm(request.POST)
            if form.is_valid():
                DudaModel.objects.create(texto=form.cleaned_data["duda"].strip())
                messages.success(request, "Tu duda se envió a la cola del profesor.")
            else:
                _avisar_errores(request, form)
        elif seccion == "buscar" and accion == "buscar_alumno":
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
        elif seccion == "historial" and accion == "eliminar_historial":
            eliminada = HistorialModel.objects.order_by("-id").first()
            if eliminada is None:
                messages.error(request, "El historial está vacío.")
            else:
                messages.success(request, f"Se eliminó del historial: {eliminada.texto}")
                eliminada.delete()
        else:
            messages.error(request, "No se reconoció la acción solicitada.")
        return redirect("alumno_seccion", seccion=seccion)

    if seccion == "temas":
        temas = _temas()
        indice = _indice_tema_actual(request, len(temas))
        lista_temas = structures.ListaDoble()
        for tema in temas:
            lista_temas.insertar_final(tema.nombre)
        nodo_actual = (
            _nodo_tema_en_indice(lista_temas, indice)
            if indice is not None
            else None
        )
        contexto.update(
            {
                "tema_actual": nodo_actual.dato if nodo_actual else None,
                "tema_posicion": indice + 1 if indice is not None else 0,
                "cantidad_temas": len(temas),
                "hay_tema_anterior": indice is not None and indice > 0,
                "hay_tema_siguiente": (
                    indice is not None and indice < len(temas) - 1
                ),
            }
        )
    elif seccion == "dudas":
        contexto["form_duda"] = DudaForm()
    elif seccion == "buscar":
        contexto.setdefault("resultado_busqueda", None)
        contexto["form_dni"] = DniForm()
    elif seccion == "historial":
        contexto["historial"] = _historial()

    return render(request, "academico/alumno.html", contexto)
