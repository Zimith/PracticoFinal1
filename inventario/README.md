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

Para simplificar la evaluación, la imagen está configurada con credenciales por defecto. Si el profesor clona el repo y ejecuta el único comando, los usuarios se crean automáticamente con las siguientes credenciales:

- Admin (superuser): usuario `admin` / contraseña `AdminPass123`
- Usuario ventas: usuario `demo_ventas` / contraseña `DemoPass123!`
- Usuario stock: usuario `demo_stock` / contraseña `DemoPass123!`

Nota sobre backup de base de datos:
- El archivo `full_backup.json` (dump generado con `manage.py dumpdata`) contiene los datos de la base
	y puede incluir emails y hashes de contraseñas. Si el profesor lo pidió, añadilo al repo en la rama
	indicada; si el repo será público, considerar anonimizarlo antes de subir.

Así que el flujo para el profesor es simplemente:

```powershell
Set-Location 'C:\ruta\a\Proyecto\Inventario\inventario'
docker compose up -d --build
```

Luego abrir `http://localhost:8000` y hacer login en `/accounts/login/` (o acceder a `/admin` con el admin).

Si prefieres definir contraseñas personalizadas en lugar de usar las por defecto, edita `.env.example` y copia a `.env` antes de arrancar (opcional). Pero no es necesario para la evaluación.

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
