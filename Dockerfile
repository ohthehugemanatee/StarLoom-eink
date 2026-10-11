FROM python:3.13-slim

WORKDIR /app
COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir . && rm -rf /app/src

USER 65534:65534
EXPOSE 8080
CMD ["uvicorn", "starloom_eink.app:app", "--host", "0.0.0.0", "--port", "8080"]
