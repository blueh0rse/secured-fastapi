# Base image pinned by digest so a rebuild always resolves the same layers.
# Tag: python:3.13.15-alpine3.24
ARG PYTHON_IMAGE=python@sha256:540c7d91f98ff6880174c40e99067bf5941eb54d818a7a5e094d188b196a934d

# --- build stage -------------------------------------------------------------
# pip and uv live here only. Neither reaches the runtime image.
FROM ${PYTHON_IMAGE} AS builder

RUN pip install --no-cache-dir uv==0.12.7

WORKDIR /app
COPY pyproject.toml uv.lock ./

# Export the locked runtime dependencies only. --no-dev drops the test and
# lint tooling. The export carries hashes, so uv verifies every wheel.
# --only-binary=:all: keeps the build honest: every dependency must ship a
# musllinux wheel, so this stage needs no compiler. The build fails loudly
# if a future dependency would need one, instead of silently pulling in gcc.
RUN uv export --frozen --no-dev --no-emit-project \
        --format requirements-txt > /tmp/requirements.txt \
 && uv venv /opt/venv \
 && uv pip install --python /opt/venv/bin/python --no-cache \
        --only-binary=:all: -r /tmp/requirements.txt

# --- runtime stage -----------------------------------------------------------
FROM ${PYTHON_IMAGE}

# apk upgrade picks up OS patches published after the base image was built.
# The digest above fixes the starting point. This line deliberately floats the
# OS package set forward, because an unpatched openssl is the worse trade.
RUN apk upgrade --no-cache \
 && adduser -D -u 10001 appuser

# The base image ships pip, which vendors its own copies of msgpack and
# setuptools. The application never calls pip, so remove it with them.
# The path is derived, not hardcoded, so overriding PYTHON_IMAGE cannot
# silently skip this. The import check fails the build if anything survives.
RUN SITE="$(python -c 'import site; print(site.getsitepackages()[0])')" \
 && rm -rf "$SITE"/pip "$SITE"/pip-*.dist-info \
           "$SITE"/setuptools "$SITE"/setuptools-*.dist-info \
           "$SITE"/pkg_resources \
 && rm -f /usr/local/bin/pip /usr/local/bin/pip3 /usr/local/bin/pip3.* \
 && if python -c 'import pip' 2>/dev/null; then echo 'pip survived removal' && exit 1; fi

# psycopg2-binary ships its own libpq inside the wheel, so the runtime stage
# needs no postgresql packages.
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app
COPY app app
COPY db db

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
