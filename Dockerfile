FROM python:3.13-slim AS BUILDER

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock ./

ENV UV_SYSTEM_PYTHON=1

RUN uv export --no-dev --frozen > requirements.txt && pip install --no-cache-dir -r requirements.txt


FROM python:3.13-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY --from=BUILDER /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/

COPY --from=BUILDER /usr/local/bin/ /usr/local/bin/

COPY . .

EXPOSE 3000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000"]