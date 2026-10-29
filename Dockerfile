FROM apache/airflow:3.0.6

COPY requirements.txt /requirements.txt
COPY requirements-dev.txt /requirements-dev.txt
COPY .flake8 /opt/airflow/.flake8
COPY pyproject.toml /opt/airflow/pyproject.toml
COPY .isort.cfg /opt/airflow/.isort.cfg

RUN pip install --no-cache-dir -r /requirements.txt \
    && pip install --no-cache-dir -r /requirements-dev.txt