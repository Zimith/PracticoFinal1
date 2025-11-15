# Inventario

Aplicación Django para gestionar productos, clientes y ventas. Proyecto dockerizado para evaluación (levantar con un solo comando).

Resumen rápido
- Stack: Django 5.2.x, Python 3.11, PostgreSQL 15 (en Docker).
- Contenedores: `web` (Django) + `db` (Postgres).
- Funcionalidades: CRUD productos (SKU único), clientes (documento único), ventas con formset, descuento de stock, historial de movimientos, permisos por grupos, interfaz con Bootstrap 4 y crispy-forms.

Índice
- Requisitos
- Levantar con Docker (Windows / Linux / macOS)
- Comandos útiles
- Ejecutar `manage.py` dentro del contenedor
- Backup de la base de datos
- Desarrollo local sin Docker (opcional)
- Credenciales demo y variables de entorno
- Persistencia de `media/` y volúmenes
- Troubleshooting rápido
- Seguridad y privacidad
- Entregables

Requisitos
- Docker Desktop (Windows / Mac) o Docker + docker-compose (Linux).
- Git (opcional, para clonar el repo).
- Espacio en disco suficiente para imágenes Docker.

Levantar con Docker (único comando)
1. Clonar repo y situarse en la carpeta que contiene `docker-compose.yml` (ejemplo Windows):
```powershell
Set-Location 'C:\ruta\a\Proyecto\Inventario\inventario'
```
Linux / macOS:
```bash
cd /ruta/a/Proyecto/Inventario/inventario
```

2. Copiar `.env.example` si querés definir claves o contraseñas personalizadas (opcional pero recomendado):
```powershell
# Windows (PowerShell)
Copy-Item .env.example .env
# editar .env con un editor (ADMIN_PASS, DEMO_VENTAS_PASS, DEMO_STOCK_PASS, SECRET_KEY, etc.)
```
```bash
# Linux/macOS
cp .env.example .env
# editar .env (ADMIN_PASS, DEMO_VENTAS_PASS, DEMO_STOCK_PASS, SECRET_KEY, etc.)
```

3. Ejecutar (reconstruye imagen y arranca en background):
```powershell
docker compose up -d --build
```
o (Linux/macOS):
```bash
docker compose up -d --build
```

Qué hace este comando:
- Construye la imagen del servicio `web` usando el `Dockerfile`.
- Arranca el servicio `db` (Postgres 15) y `web`.
- El entrypoint del contenedor `web` aplica migraciones, ejecuta `collectstatic` y crea usuarios/grupos demo si está configurado.
- La app queda disponible en `http://localhost:8000`.

Acceso
- Abrir en el navegador: `http://localhost:8000`
- Admin: `http://localhost:8000/admin`

Comandos útiles (mantenimiento)
- Reconstruir sin cache:
```bash
docker compose build --no-cache web
docker compose up -d
```
- Parar contenedores:
```bash
docker compose down
```
- Parar y eliminar volúmenes (pierde datos persistentes):
```bash
docker compose down -v
```
- Ver logs del servicio web:
```bash
docker compose logs -f web
```
- Ver contenedores y puertos:
```bash
docker compose ps
```

Ejecutar `manage.py` dentro del contenedor
- Migrate:
```bash
docker compose exec web python manage.py migrate
```
- Crear superuser (interactivo):
```bash
docker compose exec -it web python manage.py createsuperuser
```
- Ejecutar comandos de management/maintenance:
```bash
docker compose exec web python manage.py <comando>
```

Backup de la base de datos (dump)
- Redirección fiable (usar `-T` para evitar problemas con TTY):
PowerShell:
```powershell
Set-Location 'C:\ruta\a\Proyecto\Inventario\inventario'
docker compose exec -T web python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.permission --indent 2 > full_backup.json
```
Bash:
```bash
cd /ruta/a/Proyecto/Inventario/inventario
docker compose exec -T web python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.permission --indent 2 > full_backup.json
```

Alternativa si la redirección falla (crear dentro del contenedor y copiar al host):
```bash
docker compose exec web sh -c "python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.permission --indent 2 > /tmp/full_backup.json"
CID=$(docker compose ps -q web)
docker cp ${CID}:/tmp/full_backup.json ./full_backup.json
```

Ejecutar en PowerShell (alternativa):
```powershell
docker compose exec web sh -c "python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.permission --indent 2 > /tmp/full_backup.json"
$cid = docker compose ps -q web
docker cp "$cid:/tmp/full_backup.json" .\full_backup.json
```

Desarrollo local sin Docker (opcional)
- Crear entorno virtual e instalar dependencias:
```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Linux/macOS
source .venv/bin/activate
pip install -r requirements.txt
```
- Configurar `.env` o variables de entorno (si usás Postgres local).
- Migrar y arrancar:
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

Credenciales demo y variables de entorno
- El proyecto puede crear usuarios demo/administrador automáticamente desde `entrypoint.sh` usando variables definidas en `.env`.
- Por seguridad: evita dejar contraseñas reales en el repo público. Si usás credenciales demo, documentalas en el README pero con la recomendación de cambiarlas.
- Variables importantes (en `.env`):
	- `SECRET_KEY`
	- `DEBUG` (0/1)
	- `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASS`
	- `ADMIN_PASS`, `DEMO_VENTAS_PASS`, `DEMO_STOCK_PASS`
- Si no querés usar usuarios demo, simplemente no rellenes esas variables y crea el superuser manualmente con `createsuperuser`.

Persistencia de `media/` y volúmenes
- `docker-compose.yml` define volúmenes (ej. `media_data`, `postgres_data`) para persistir archivos subidos y la base de datos.
- No se deben eliminar volúmenes si querés conservar datos entre reinicios.

Troubleshooting rápido
- `full_backup.json` vacío al redirigir: usar `-T` con `docker compose exec` o usar la alternativa `docker cp`.
- Error al build por librerías nativas (ej. WeasyPrint): revisar `Dockerfile` y añadir dependencias apt necesarias (pango, cairo, libffi, libpq-dev, shared-mime-info).
- Warning `STATICFILES_DIRS path does not exist`: asegurate de que la carpeta `static/` exista o ajusta `STATICFILES_DIRS` en `settings.py`.
- Duplicado de namespace en urls: revisar `inventario/urls.py` y evitar includes duplicados.

Seguridad y privacidad
- No commitear `SECRET_KEY` ni contraseñas.
- Añadir `.env` al `.gitignore` (usar `.env.example` para mostrar variables necesarias).
- No subir `full_backup.json` con datos reales en repositorio público; si necesitás subirlo, anonimizar emails/nombres/teléfonos o crear un backup parcial.
- Para producción: configurar parámetros `SECURE_*`, `ALLOWED_HOSTS`, HTTPS y revisión de permisos.

Entregables esperados (para la cátedra)
- Repo GitHub con código fuente completo.
- `Dockerfile`, `.dockerignore` y `docker-compose.yml` funcionales.
- `requirements.txt` actualizado.
- `README.md` con instrucciones (este documento).
- `docs/Informe_Entrega.md` o Google Doc para comentarios del docente.
- `full_backup.json` (opcional y anonimizado si el repo será público).

Autor
- [Tu nombre aquí] — (reemplazá por tu nombre o usuario GitHub)

Licencia
- Proyecto desarrollado con fines educativos. No comercializar sin autorización.

¿Querés que:
- A) Reemplace el `README.md` en `inventario/` con esta versión y haga el commit? (si sí, confirmame el mensaje de commit)
- B) Cree `README_clean.md` y lo deje listo para revisar?
- C) Solo lo pegas vos manualmente en GitHub?

Dime la opción y lo ejecuto.
