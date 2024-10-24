FROM apache/airflow:latest
USER root
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
  chromium \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

USER airflow
RUN pip install --no-cache-dir -r /requirements.txt
