FROM python:3.13-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

RUN pip install uv

COPY pyproject.toml uv.lock ./

ENV UV_SYSTEM_PYTHON=1

RUN uv export --no-dev --frozen > requirements.txt && pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 3000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000"]