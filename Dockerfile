# Python 3.13 slim multi-platform manifest-list digest, resolved 2026-08-12.
FROM python:3.13-slim@sha256:ffb752e139c0a19692a43af8d8523b274222dd68eebad5d583b45c2201c6e30a AS builder
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /build
COPY pyproject.toml requirements.runtime.lock ./
COPY src ./src
RUN python -m pip install --no-cache-dir --target /opt/runtime --no-deps --requirement requirements.runtime.lock \
    && python -m pip wheel --no-cache-dir --no-deps --wheel-dir /tmp/wheels . \
    && python -m pip install --no-cache-dir --target /opt/runtime --no-deps /tmp/wheels/secure_url_shortener-0.1.0-py3-none-any.whl

FROM python:3.13-slim@sha256:ffb752e139c0a19692a43af8d8523b274222dd68eebad5d583b45c2201c6e30a AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/opt/runtime
WORKDIR /app
RUN addgroup --system app && adduser --system --ingroup app app \
    && rm -rf /usr/local/lib/python3.13/site-packages/pip* /usr/local/lib/python3.13/site-packages/setuptools* \
    /usr/local/bin/pip /usr/local/bin/pip3 /usr/local/bin/pip3.13
COPY --from=builder /opt/runtime /opt/runtime
COPY migrations ./migrations
COPY scripts ./scripts
COPY templates ./templates
COPY static ./static
COPY alembic.ini ./
RUN chown -R app:app /app /opt/runtime
USER app
EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=3s --start-period=20s --retries=5 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz')"
CMD ["python", "-m", "uvicorn", "secure_shortener.main:app", "--host", "0.0.0.0", "--port", "8000"]
