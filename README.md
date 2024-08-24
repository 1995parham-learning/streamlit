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

## References

- [Streamlit Documentation](https://docs.streamlit.io/)
