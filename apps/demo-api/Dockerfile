FROM python:3.12-slim

WORKDIR /app
COPY app.py /app/app.py

RUN useradd --create-home --uid 10001 appuser
USER appuser

EXPOSE 8080
HEALTHCHECK --interval=10s --timeout=2s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health', timeout=1)"

CMD ["python", "/app/app.py"]
