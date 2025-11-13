# Inventario

Instrucciones mínimas para que el profesor pueda clonar y ver la aplicación corriendo en `http://localhost:8000` con un solo comando.

Requisitos previos
- Docker Desktop instalado y funcionando.

Pasos (1 comando)
1. Clonar el repositorio.
2. Posicionarse en la carpeta del proyecto que contiene `docker-compose.yml`:

```powershell
Set-Location 'C:\ruta\a\Proyecto\Inventario\inventario'
```

3. Copiar la plantilla de variables de entorno y editar las contraseñas (opcional, pero recomendado si quieres usuarios demo/admin ya creados):

```powershell
Copy-Item .env.example .env
# editar .env y completar ADMIN_PASS, DEMO_VENTAS_PASS, DEMO_STOCK_PASS
```

4. Ejecutar el comando único para levantar la aplicación (rebuild + detached):

```powershell
docker compose up -d --build
```

Eso hará:
- Construir la imagen del servicio web.
- Arrancar Postgres y el servicio web.
- Ejecutar migraciones y `collectstatic` dentro del contenedor.

Acceder
- Abrir `http://localhost:8000` en el navegador.
- La interfaz de administración estará en `/admin`.

Credenciales / Usuarios auto-creados:

- Si editaste `.env` y definiste `ADMIN_PASS`, `DEMO_VENTAS_PASS` y/o `DEMO_STOCK_PASS`, esos usuarios serán creados automáticamente al arrancar el contenedor (usuario `admin`, `demo_ventas` y `demo_stock`).
- Si NO definiste esas variables, tendrás que crear el superuser manualmente desde el contenedor:

```powershell
# Crear superuser interactivamente
docker compose exec web python manage.py createsuperuser

# O crear usuarios de ejemplo no interactivos (ejemplo con contraseñas)
docker compose exec web python manage.py shell -c "from django.contrib.auth import get_user_model; User=get_user_model(); User.objects.create_superuser('admin','admin@example.com','AdminPass123')"
```

Notas
- No se incluyen archivos estáticos recopilados en el repo (`staticfiles/` está en `.gitignore`).
Variables sensibles:

- `SECRET_KEY` y las contraseñas de demo/admin pueden ser definidas en un archivo `.env` (copia de `.env.example`) o exportadas en la shell. Si definís `ADMIN_PASS` y/o las otras variables, los usuarios se crearán automáticamente.

Ejemplo (PowerShell) usando `.env`:

```powershell
Copy-Item .env.example .env
# Editar .env y poner contraseñas en ADMIN_PASS, DEMO_VENTAS_PASS, DEMO_STOCK_PASS
docker compose up -d --build
```
