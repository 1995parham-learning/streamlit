FROM python:3.12-slim

WORKDIR /app

ENV TZ="Asia/Tehran"

RUN apt-get update && apt-get install -y --no-install-recommends \
  build-essential \
  curl \
  software-properties-common \
  git \
  && rm -rf /var/lib/apt/lists/*

COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

RUN pip install --no-cache-dir --upgrade pipenv \
  && pipenv install --system

COPY . .

EXPOSE 1378

HEALTHCHECK CMD curl --fail http://localhost:1378/_stcore/health

ENTRYPOINT ["streamlit", "run", "main.py", "--server.port=1378", "--server.address=0.0.0.0"]
