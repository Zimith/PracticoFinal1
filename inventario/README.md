# Inventario

Instrucciones mínimas para que el profesor pueda clonar y ver la aplicación corriendo en `http://localhost:8000` con un solo comando.

Requisitos previos
- Docker Desktop instalado y funcionando.

Pasos (1 comando)
1. Clonar el repositorio.
2. Posicionarse en la carpeta del proyecto que contiene `docker-compose.prod.yml`:

```powershell
Set-Location 'C:\ruta\a\Proyecto\Inventario\inventario'
```

3. Ejecutar el comando único para levantar la aplicación (rebuild + detached):

```powershell
docker compose -f docker-compose.prod.yml up -d --build
```

Eso hará:
- Construir la imagen del servicio web.
- Arrancar Postgres y el servicio web.
- Ejecutar migraciones y `collectstatic` dentro del contenedor.

Acceder
- Abrir `http://localhost:8000` en el navegador.
- La interfaz de administración estará en `/admin`.

Credenciales (si deseas crear un superusuario):
- Puedes crear uno dentro del contenedor con:

```powershell
# Reemplaza la ruta si estás en otra carpeta
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

Notas
- No se incluyen archivos estáticos recopilados en el repo (`staticfiles/` está en `.gitignore`).
- Variables sensibles como `SECRET_KEY` se leen de las variables de entorno. Para cambiar el `SECRET_KEY` antes de arrancar, exporta la variable en tu shell o crea un archivo `.env` y pásalo al comando.

Ejemplo (PowerShell) con `SECRET_KEY` temporal:

```powershell
$env:SECRET_KEY = 'mi_clave_segura_de_prueba'
docker compose -f docker-compose.prod.yml up -d --build
```
