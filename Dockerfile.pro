FROM python:3.12-slim AS builder

WORKDIR /usr/src/app

COPY requirements/ requirements/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements/production.txt && \
    pip install --no-cache-dir -r requirements/development.txt
    
RUN playwright install-deps && python -m playwright install chromium


FROM python:3.12-slim

WORKDIR /usr/src/app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
