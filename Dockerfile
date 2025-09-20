# syntax=docker/dockerfile:1

FROM node:20-slim AS frontend
WORKDIR /app/frontend
COPY frontend ./
RUN npm install && npm run build

FROM python:3.11-slim AS backend
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY pyproject.toml ./
RUN pip install --no-cache-dir .
COPY . .

FROM python:3.11-slim AS runtime
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY --from=backend /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=backend /usr/local/bin /usr/local/bin
COPY --from=backend /app /app
COPY --from=frontend /app/frontend/dist /app/frontend/dist
ENV WINELENS_ENVIRONMENT=prod
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
