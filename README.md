<h6 align="center"> When Nostradamus uses Streamlit </h6>
<h1 align="center"> Streamlit </h1>

<p align="center">
  <img alt="banner" src="./.github/assets/banner.png" height="200px" />
</p>

<p align="center">
  <img alt="GitHub Workflow Status (with event)" src="https://img.shields.io/github/actions/workflow/status/1995parham-learning/streamlit/ci.yaml?style=for-the-badge&logo=github">
  <img alt="GitHub Pipenv locked Python version" src="https://img.shields.io/github/pipenv/locked/python-version/1995parham-learning/streamlit?style=for-the-badge&logo=python">
</p>

## Introduction

With [Streamlit](https://streamlit.io/), you can easily host your Python scripts as web applications,
making it a great tool for demonstrating your results or models.

## Development

It's best to deploy your Streamlit applications separately rather than using a single deployment for all of them.
Since Streamlit is built on Python, it's crucial to use a dependency manager for your application.
Please consider one of the following options:

- [Pipenv](https://pipenv.pypa.io/)
- [Poetry](https://python-poetry.org/)
- [Rye](https://rye.astral.sh/)

In this example, we're using `pipenv` as our dependency manager, but feel free to choose any of the others.
Most of these dependency managers can provide a specific Python version for your project,
allowing you to use a different version than your system's default Python installation.

```shell
pipenv install streamlit
```

You may need following libraries too:

- [`numpy`](https://numpy.org/)
- [`pandas`](https://pandas.pydata.org/)
- [`polars`](https://pola.rs/)

```shell
pipenv install numpy
pipenv install pandas
pipenv install polars
```

After installing the requirements, you have `Pipfile` (which is written in TOML
and you can also manually change it) and `Pipfile.lock`:

```toml
[[source]]
url = "https://pypi.org/simple"
verify_ssl = true
name = "pypi"

[packages]
streamlit = "*"
pandas = "*"

[dev-packages]
ruff = "*"
mypy = "*"
pandas-stubs = "*"

[requires]
python_version = "3.12"
```

Python is a dynamically typed language, so we **strongly** suggest use following
linters in your code:

- [`mypy`](https://mypy.readthedocs.io/en/stable/)
- [`ruff`](https://docs.astral.sh/ruff/)

## How to run?

```bash
streamlit config show

streamlit run main.py
```

## Deployment

When you're ready to deploy your application to production, you should build your Docker image and integrate
this process into your CI pipeline.

The following Dockerfile installs the requirements using `pipenv` and then serve
Streamlit application on port 1378.

```dockerfile
FROM python:3.12-slim

ENV TZ="Asia/Tehran"

RUN apt-get update && apt-get install -y --no-install-recommends \
  build-essential \
  curl \
  software-properties-common \
  git \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

RUN pip install --no-cache-dir pipenv && \
  pipenv install --system --clear

COPY . .

EXPOSE 1378

HEALTHCHECK CMD curl --fail http://localhost:1378/_stcore/health
ENTRYPOINT ["streamlit", "run", "main.py", "--server.port=1378", "--server.address=0.0.0.0"]
```

Then you can build docker image in your CI:

- GitHub

  ```yaml
  name: ci
  on:
    - push
  jobs:
  # you can remove lint stage, but remember to remove it from docker stage
  # requirements too.
  lint:
    name: lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install pipenv
      - run: pipenv install --dev -v
      - run: pipenv run mypy .

  docker:
    name: docker
    runs-on: ubuntu-latest
    needs:
      - lint
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/setup-qemu-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.repository_owner }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/bake-action@v5
        with:
          files: "docker-bake.json"
          push: true
  ```

- GitLab

  ```yaml
  lint:
  stage: lint
  # set this to true if you don't want to have linting
  allow_failure: false
  image: python:3.12-slim
  variables:
    # proxy variables are required because GitLab workers are in Iran.
    http_proxy: "http://proxy.snappcloud.io:3128"
    https_proxy: "http://proxy.snappcloud.io:3128"
    no_proxy: ".snappcloud.io,.snapp.ir"
  before_script:
    - pip install -U pipenv pip
    - pipenv install --dev -v
    - echo "lint stage ${CI_PROJECT_NAME} on ${CI_COMMIT_REF_SLUG} branch"
  script:
    - pipenv run ruff check main.py rides.py
    - pipenv run mypy .
  ```

  ```yaml
  build-and-release:
  image: docker:latest
  stage: build
  when: manual
  variables:
    # set these variables according your target namespace in which you want to
    # push the image.
    OKD4_TEH1_REGISTRY: "image-registry.apps.private.okd4.teh-1.snappcloud.io"
    RELEASE_CONTAINER_REGISTRY_ADDRESS: "$OKD4_TEH1_REGISTRY"
    RELEASE_CONTAINER_REGISTRY_IMAGE: "$OKD4_TEH1_REGISTRY/visualization/$CI_PROJECT_NAME"
    RELEASE_CONTAINER_REGISTRY_USERNAME: "gitlab-runner"
    RELEASE_CONTAINER_REGISTRY_PASSWORD: ${OKD4_TEH1_VISUALIZATION_TOKEN}
  before_script:
    - docker info
    - docker login -u ${CI_REGISTRY_USER} -p ${CI_REGISTRY_PASSWORD} ${CI_REGISTRY}
    - docker login -u ${RELEASE_CONTAINER_REGISTRY_USERNAME} -p ${RELEASE_CONTAINER_REGISTRY_PASSWORD} ${RELEASE_CONTAINER_REGISTRY_ADDRESS}
  script:
    - export CURRENT_DATETIME=$(TZ=Asia/Tehran date '+%FT%T')
    # proxy variables are required because GitLab workers are in Iran.
    - docker build --build-arg BUILD_DATE=$CURRENT_DATETIME --build-arg VCS_REF=${CI_COMMIT_SHA} --build-arg BUILD_VERSION=${CI_COMMIT_REF_NAME} --build-arg HTTP_PROXY=http://proxy.snappcloud.io:3128/ --build-arg HTTPS_PROXY=http://proxy.snappcloud.io:3128/ -t ${CI_PROJECT_NAME}:${CI_COMMIT_REF_NAME} -f Dockerfile .
    - docker tag ${CI_PROJECT_NAME}:${CI_COMMIT_REF_NAME} ${RELEASE_CONTAINER_REGISTRY_IMAGE}:${CI_COMMIT_REF_NAME}
    - docker push ${RELEASE_CONTAINER_REGISTRY_IMAGE}:${CI_COMMIT_REF_NAME}
  ```

## Kubernetes

To Deploy the application on Kubernetes, you only need to have a `deployment` and
`httpproxy`. If your application has configuration (the easiest way for handling
configuration in python is environment variables) then you may need `secret` and
`configmap` too.

```yaml
---
kind: Service
apiVersion: v1
metadata:
  name: <name>
  labels:
    app: <name>
spec:
  ports:
    - protocol: TCP
      port: 1378
      targetPort: 1378
  selector:
    app: <name>

---
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: <name>
  name: <name>
spec:
  replicas: 1
  selector:
    matchLabels:
      app: <name>
  template:
    metadata:
      labels:
        app: <name>
    spec:
      containers:
        - name: <name>-main
          image: <image>
          imagePullPolicy: Always
          env:
            - name: CLICKHOUSE_HOST
              value: "****"
            - name: CLICKHOUSE_PORT
              value: "****"
          resources:
            limits:
              cpu: 1
              ephemeral-storage: 1Gi
              memory: 1Gi
            requests:
              cpu: 300m
              ephemeral-storage: 1Gi
              memory: 1Gi
      volumes:
        - name: data
          emptyDir: {}
---
kind: Route
apiVersion: route.openshift.io/v1
metadata:
  name: <name>
  labels:
    app: <name>
    router: private
spec:
  host: <url>
  path: /
  to:
    kind: Service
    name: <name>
    weight: 100
  port:
    targetPort: 1378
  tls:
    termination: edge
    insecureEdgeTerminationPolicy: Redirect
  wildcardPolicy: None
```

## References

- [Streamlit Documentation](https://docs.streamlit.io/)
