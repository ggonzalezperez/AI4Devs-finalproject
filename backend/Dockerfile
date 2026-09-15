FROM python:3.12-slim
WORKDIR /app
ENV PIP_NO_CACHE_DIR=1 PYTHONUNBUFFERED=1
COPY pyproject.toml ./
COPY app ./app
RUN pip install .
COPY alembic ./alembic
COPY alembic.ini ./alembic.ini
COPY docker-entrypoint.sh ./docker-entrypoint.sh
RUN chmod +x docker-entrypoint.sh
# MEDIA_DIR debe existir EN LA IMAGEN y pertenecer a `app`. Si no, Docker crea
# el punto de montaje del volumen como root y el proceso, que corre sin
# privilegios, no puede escribir las imágenes generadas.
RUN mkdir -p /app/media/lessons /app/media/avatars
# Usuario no-root (menos superficie de escalada de privilegios)
RUN adduser --system --group --no-create-home app && chown -R app:app /app
USER app
EXPOSE 8000
ENTRYPOINT ["./docker-entrypoint.sh"]
