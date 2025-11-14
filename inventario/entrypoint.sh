#!/bin/sh
set -e

#!/bin/sh
set -e

# Este script se ejecuta cuando se inicia el contenedor `web`.
# Tareas que realiza:
#  - aplicar migraciones de base de datos
#  - crear grupos y usuarios demo mediante el comando `setup_groups`
#  - ejecutar `collectstatic` para reunir archivos estáticos en STATIC_ROOT

# Usamos `|| true` en `makemigrations` y `setup_groups` para no detener
# el arranque si no hay cambios o si el comando devuelve un error no crítico.
python manage.py makemigrations --noinput || true
python manage.py migrate --noinput
python manage.py setup_groups || true
python manage.py collectstatic --noinput

# Finalmente ejecutamos el comando pasado por CMD (normalmente gunicorn)
exec "$@"
