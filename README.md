# Aula en línea

Aplicación web académica desarrollada con Django. Permite al profesor administrar alumnos, temas de repaso y dudas; el alumno puede consultar temas, buscar compañeros, enviar dudas y revisar el historial.

## Requisitos

- Python 3.10 o posterior.
- Dependencias instaladas con `python -m pip install -r requirements.txt`.

## Iniciar el proyecto (ACA LO LEVANTABA DESDE EL POWERSHELL)

Abre PowerShell en esta carpeta y ejecuta:

```powershell
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8001
```

Abre `http://127.0.0.1:8001/` en el navegador. Si el puerto está ocupado, cambia `8001` por otro, como `8002`.
Cada vez que se cerraba el POWERSHELL se perdian los datos de los alumnos registrados y las dudas
Pero ahora implementamos NEON y RENDER para no tener esas molestias

## Estructura de carpetas y archivos

- **`academico/`**: Contiene la aplicación académica de Django.
  - **`forms.py`**: Define los formularios y valida los datos ingresados.
  - **`views.py`**: Procesa las solicitudes y coordina las acciones de cada página.
- **`config/`**: Almacena la configuración general y las rutas principales del proyecto Django.
- **`static/`**: Contiene los archivos estáticos originales, como los estilos CSS.
- **`staticfiles/`**: Reúne los archivos estáticos preparados para servir la aplicación.
- **`templates/`**: Contiene las plantillas HTML que Django muestra en las páginas.
- **`trabajoF.py`**: Estructuras de datos del trabajo, aca esta nuestro codigo original.

## Uso y datos

- El profesor puede registrar, buscar y eliminar alumnos; agregar o eliminar temas y atender dudas pendientes.
- El alumno inicia sesión con un DNI registrado, consulta temas, busca compañeros, envía dudas y revisa o elimina entradas del historial.
- Los datos de la aplicación web se guardan en la base SQLite local `db.sqlite3`; aplica los cambios del esquema con `python manage.py migrate`.
- El menú de consola de `trabajoF.py` permanece disponible por separado.
