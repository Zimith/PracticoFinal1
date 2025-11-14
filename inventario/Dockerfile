FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# dependencias del sistema para psycopg2 si usás Postgres
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

# instalar dependencias Python
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt
RUN pip install whitenoise==6.11.0

# copiar proyecto
COPY . /app/

# entrypoint para migraciones/collectstatic
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
RUN sed -i 's/\r$//' /entrypoint.sh || true

EXPOSE 8000

ENTRYPOINT ["sh", "/entrypoint.sh"]
CMD ["gunicorn", "inventario.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
