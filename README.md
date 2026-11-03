# Interfaz web del sistema académico

Esta aplicación agrega una interfaz web con Django sin modificar `trabajoF.py`. El menú de terminal original sigue disponible; la interfaz carga únicamente las clases de estructuras de datos de ese archivo y no ejecuta su menú.

## Requisitos

- Python 3.10 o posterior
- Django (instalación con `pip install -r requirements.txt`)

## Iniciar

Desde esta carpeta, ejecuta:

```powershell
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8001
```

Después abre `http://127.0.0.1:8001/` en el navegador. Si ese puerto también está ocupado, puedes probar otro, por ejemplo `python manage.py runserver 8002`, y abrir `http://127.0.0.1:8002/`.

## Desplegar en Render con Neon

En local, Django usa `db.sqlite3` por defecto. Si se define `DATABASE_URL`, cambia automáticamente a PostgreSQL. No guardes esa URL ni la clave secreta en el repositorio.

1. En Render, crea un **Web Service** conectado al repositorio de GitHub.
2. Usa estos comandos:
   - **Build Command:** `pip install -r requirements.txt && python manage.py collectstatic --no-input`
   - **Start Command:** `python manage.py migrate && gunicorn config.wsgi:application`
3. En **Environment Variables**, agrega:
   - `DATABASE_URL`: URL de conexión de Neon, copiada de **Connect**. Usa la URL completa con SSL.
   - `DJANGO_SECRET_KEY`: una clave secreta aleatoria. Puedes generar una localmente con `python -c "import secrets; print(secrets.token_urlsafe(50))"` y pegar el resultado directamente en Render.
   - `DJANGO_DEBUG`: `false`.
   - `ALLOWED_HOSTS`: el dominio de Render, por ejemplo `mi-app.onrender.com` (sin `https://`).
   - `CSRF_TRUSTED_ORIGINS`: el origen del sitio, por ejemplo `https://mi-app.onrender.com`.
4. Despliega. El comando de inicio ejecuta las migraciones de Django contra Neon antes de arrancar la aplicación.

No compartas ni subas los valores de `DATABASE_URL` o `DJANGO_SECRET_KEY` a GitHub.

## Uso y datos

- En el panel del profesor puedes registrar, buscar y eliminar alumnos; ver todos los temas y eliminar cualquiera de ellos; además, puedes atender dudas.
- En el panel del alumno inicia sesión con un DNI registrado. Desde ahí puedes recorrer los temas de uno en uno hacia adelante y atrás, buscar alumnos, enviar dudas y revisar el historial en orden de atención; eliminar la última entrada quita la duda atendida más recientemente.
- En local, alumnos, temas, dudas e historial se guardan en SQLite (`db.sqlite3`). En Render, se guardan en PostgreSQL usando la URL de Neon.
- El panel web usa modelos de Django para persistir la información. Los temas también se cargan en una lista doble para recorrerlos y eliminar el tema seleccionado; las estructuras originales siguen disponibles en `trabajoF.py` para el programa de consola.
