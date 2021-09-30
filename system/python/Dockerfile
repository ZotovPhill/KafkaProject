FROM python:3.9.0-slim

ENV PYTHONFAULTHANDLER=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=on \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100

RUN python -m pip install -U pip
RUN pip install poetry

WORKDIR /usr/src

COPY /system/python/poetry.lock /system/python/pyproject.toml ./
RUN poetry config virtualenvs.create false \
  && poetry install --no-dev

COPY src src
COPY .env /system/python/entrypoint.sh ./
RUN chmod +x entrypoint.sh

ENV PYTHONPATH=/src

ENTRYPOINT [ "/usr/src/entrypoint.sh" ]
