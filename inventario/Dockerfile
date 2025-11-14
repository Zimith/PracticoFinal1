FROM python:3.11-slim

## Variables para evitar .pyc y forzar salida sin buffer
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

## Directorio de trabajo dentro de la imagen
WORKDIR /app

## Instalar dependencias del sistema necesarias para:
## - compilar paquetes Python (build-essential)
## - usar psycopg2 con Postgres (libpq-dev)
## - bibliotecas gráficas (cairo/pango) en caso de procesar imágenes/PDFs
RUN apt-get update && apt-get install -y \
	build-essential \
	libpq-dev \
	libcairo2 \
	libpango-1.0-0 \
	libpangocairo-1.0-0 \
	libpangoft2-1.0-0 \
	libgdk-pixbuf-xlib-2.0-0 \
	libffi-dev \
	shared-mime-info \
	--no-install-recommends && rm -rf /var/lib/apt/lists/*

## Copiar el listado de dependencias e instalarlas
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

## Instalación explícita de WhiteNoise como respaldo (opcional)
RUN pip install whitenoise==6.11.0

## Copiar el código del proyecto dentro de la imagen
COPY . /app/

## Copiar el entrypoint que prepara la app al iniciar el contenedor
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
RUN sed -i 's/\r$//' /entrypoint.sh || true

## Exponer el puerto usado por gunicorn
EXPOSE 8000

## ENTRYPOINT: script que aplica migraciones, crea grupos demo y ejecuta collectstatic
ENTRYPOINT ["sh", "/entrypoint.sh"]
## CMD por defecto: iniciar gunicorn para servir la aplicación
CMD ["gunicorn", "inventario.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
