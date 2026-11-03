from django.test import TestCase

from .models import Alumno, Duda, Historial, Tema


class SistemaWebTests(TestCase):
    def test_paginas_principales_se_muestran(self):
        inicio = self.client.get("/")
        panel_profesor = self.client.get("/profesor/")
        panel_alumno = self.client.get("/alumno/")

        self.assertEqual(inicio.status_code, 200)
        self.assertContains(inicio, "Ingresar como profesor")
        self.assertEqual(panel_profesor.status_code, 200)
        self.assertContains(panel_profesor, "Gestionar alumnos")
        self.assertEqual(panel_alumno.status_code, 200)
        self.assertContains(panel_alumno, "Verificar acceso")
        self.assertEqual(self.client.get("/profesor/alumnos/").status_code, 200)
        self.assertEqual(self.client.get("/profesor/temas/").status_code, 200)
        self.assertEqual(self.client.get("/profesor/dudas/").status_code, 200)

    def test_apartados_del_alumno_requieren_sesion_y_tienen_navegacion(self):
        response = self.client.get("/alumno/temas/")
        self.assertRedirects(response, "/alumno/")

        Alumno.objects.create(
            nombre="Ana Torres",
            dni="12345678",
            correo="ana@example.com",
        )
        self.client.post(
            "/alumno/",
            {"accion": "iniciar_sesion", "dni": "12345678"},
        )
        panel = self.client.get("/alumno/")
        self.assertContains(panel, "Consultar temas")
        self.assertContains(panel, "Buscar alumno")

        for seccion in ("temas", "dudas", "buscar", "historial"):
            response = self.client.get(f"/alumno/{seccion}/")
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "Cerrar sesión")

    def test_profesor_registra_alumno(self):
        response = self.client.post(
            "/profesor/alumnos/",
            {
                "accion": "registrar_alumno",
                "nombre": "Ana Torres",
                "dni": "12345678",
                "correo": "ana@example.com",
            },
        )

        self.assertRedirects(response, "/profesor/alumnos/")
        alumno = Alumno.objects.get(dni="12345678")
        self.assertIsNotNone(alumno)
        self.assertEqual(alumno.nombre, "Ana Torres")

    def test_dni_invalido_muestra_un_mensaje(self):
        response = self.client.post(
            "/profesor/alumnos/",
            {
                "accion": "registrar_alumno",
                "nombre": "Ana Torres",
                "dni": "123",
                "correo": "ana@example.com",
            },
            follow=True,
        )

        self.assertEqual(response.redirect_chain, [("/profesor/alumnos/", 302)])
        self.assertContains(response, "exactamente 8 dígitos")
        self.assertFalse(Alumno.objects.exists())

    def test_alumno_envia_duda_y_profesor_la_atiende(self):
        Alumno.objects.create(
            nombre="Ana Torres",
            dni="12345678",
            correo="ana@example.com",
        )

        login = self.client.post(
            "/alumno/",
            {"accion": "iniciar_sesion", "dni": "12345678"},
        )
        self.assertRedirects(login, "/alumno/")

        envio = self.client.post(
            "/alumno/dudas/",
            {"accion": "enviar_duda", "duda": "¿Cómo funciona una cola?"},
        )
        self.assertRedirects(envio, "/alumno/dudas/")
        self.assertEqual(Duda.objects.get().texto, "¿Cómo funciona una cola?")

        atencion = self.client.post(
            "/profesor/dudas/",
            {"accion": "responder_duda"},
        )
        self.assertRedirects(atencion, "/profesor/dudas/")
        self.assertFalse(Duda.objects.exists())
        self.assertEqual(
            Historial.objects.get().texto,
            "Atendida: ¿Cómo funciona una cola?",
        )

    def test_profesor_ve_todos_los_temas_y_puede_eliminar_uno(self):
        for tema in ("Tema 1", "Tema 2", "Tema 3", "Tema 4", "Tema 5"):
            Tema.objects.create(nombre=tema)

        response = self.client.get("/profesor/temas/")
        for tema in ("Tema 1", "Tema 2", "Tema 3", "Tema 4", "Tema 5"):
            self.assertContains(response, tema)

        tema = Tema.objects.get(nombre="Tema 3")
        self.client.post(
            "/profesor/temas/",
            {"accion": "eliminar_tema", "tema_id": tema.id},
        )

        response = self.client.get("/profesor/temas/")
        self.assertNotContains(response, "Tema 3")
        self.assertContains(response, "Tema 2")
        self.assertContains(response, "Tema 4")
        self.assertEqual(Tema.objects.count(), 4)

    def test_alumno_recorre_temas_de_uno_en_uno_en_ambos_sentidos(self):
        Alumno.objects.create(
            nombre="Ana Torres",
            dni="12345678",
            correo="ana@example.com",
        )
        for tema in ("Tema 1", "Tema 2", "Tema 3"):
            Tema.objects.create(nombre=tema)
        self.client.post(
            "/alumno/",
            {"accion": "iniciar_sesion", "dni": "12345678"},
        )

        self.assertContains(self.client.get("/alumno/"), "Consultar temas")
        response = self.client.get("/alumno/temas/")
        self.assertContains(response, "Tema 1")
        self.assertNotContains(response, "Tema 2")
        self.client.post("/alumno/temas/", {"accion": "tema_siguiente"})
        response = self.client.get("/alumno/temas/")
        self.assertContains(response, "Tema 2")
        self.assertNotContains(response, "Tema 1")
        self.client.post("/alumno/temas/", {"accion": "tema_siguiente"})
        self.client.post("/alumno/temas/", {"accion": "tema_anterior"})
        response = self.client.get("/alumno/temas/")
        self.assertContains(response, "Tema 2")
        self.assertNotContains(response, "Eliminar tema")

    def test_alumno_busca_companero_en_apartado_separado(self):
        Alumno.objects.create(
            nombre="Ana Torres",
            dni="12345678",
            correo="ana@example.com",
        )
        Alumno.objects.create(
            nombre="Luis Pérez",
            dni="87654321",
            correo="luis@example.com",
        )
        self.client.post(
            "/alumno/",
            {"accion": "iniciar_sesion", "dni": "12345678"},
        )

        response = self.client.post(
            "/alumno/buscar/",
            {"accion": "buscar_alumno", "dni": "87654321"},
            follow=True,
        )

        self.assertContains(response, "Alumno: Luis Pérez")
        self.assertContains(response, "luis@example.com")

    def test_historial_se_numera_en_orden_de_atencion_y_elimina_el_mas_reciente(self):
        Alumno.objects.create(
            nombre="Ana Torres",
            dni="12345678",
            correo="ana@example.com",
        )
        first = Historial.objects.create(texto="Atendida: duda 1")
        second = Historial.objects.create(texto="Atendida: duda 2")
        third = Historial.objects.create(texto="Atendida: duda 3")
        login = self.client.post(
            "/alumno/",
            {"accion": "iniciar_sesion", "dni": "12345678"},
        )
        self.assertRedirects(login, "/alumno/")

        response = self.client.get("/alumno/historial/")
        self.assertEqual(
            [
                (entry["numero"], entry["texto"])
                for entry in response.context["historial"]
            ],
            [
                (3, "Atendida: duda 3"),
                (2, "Atendida: duda 2"),
                (1, "Atendida: duda 1"),
            ],
        )
        content = response.content.decode()
        self.assertLess(
            content.index("3. Atendida: duda 3"),
            content.index("2. Atendida: duda 2"),
        )
        self.assertLess(
            content.index("2. Atendida: duda 2"),
            content.index("1. Atendida: duda 1"),
        )

        self.client.post("/alumno/historial/", {"accion": "eliminar_historial"})

        self.assertFalse(Historial.objects.filter(pk=third.id).exists())
        self.assertTrue(Historial.objects.filter(pk=first.id).exists())
        self.assertTrue(Historial.objects.filter(pk=second.id).exists())
        response = self.client.get("/alumno/historial/")
        self.assertContains(response, "2. Atendida: duda 2")
        self.assertContains(response, "1. Atendida: duda 1")
        self.assertNotContains(response, "3. Atendida: duda 3")

    def test_datos_persisten_entre_solicitudes(self):
        response = self.client.post(
            "/profesor/alumnos/",
            {
                "accion": "registrar_alumno",
                "nombre": "Luis Pérez",
                "dni": "87654321",
                "correo": "luis@example.com",
            },
        )
        self.assertRedirects(response, "/profesor/alumnos/")

        self.client.post(
            "/profesor/temas/",
            {"accion": "registrar_tema", "tema": "Estructuras de datos"},
        )
        self.client.post(
            "/alumno/",
            {"accion": "iniciar_sesion", "dni": "87654321"},
        )
        self.client.post(
            "/alumno/dudas/",
            {"accion": "enviar_duda", "duda": "¿Qué es una lista doble?"},
        )

        self.assertContains(self.client.get("/profesor/alumnos/"), "Luis Pérez")
        self.assertContains(self.client.get("/profesor/temas/"), "Estructuras de datos")
        self.assertContains(self.client.get("/profesor/dudas/"), "¿Qué es una lista doble?")
        self.assertEqual(Alumno.objects.count(), 1)
        self.assertEqual(Tema.objects.count(), 1)
        self.assertEqual(Duda.objects.count(), 1)

    def test_eliminar_tema_persiste_en_sqlite(self):
        tema = Tema.objects.create(nombre="Tema para borrar")

        self.client.post(
            "/profesor/temas/",
            {"accion": "eliminar_tema", "tema_id": tema.id},
        )

        self.assertFalse(Tema.objects.exists())
