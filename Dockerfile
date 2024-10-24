FROM apache/airflow:latest
USER root
# Install Firefox and Geckodriver for Selenium
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    firefox-esr \
    wget \
    && wget -q -O /tmp/geckodriver.tar.gz https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-linux64.tar.gz \
    && tar -xzf /tmp/geckodriver.tar.gz -C /usr/local/bin/ \
    && chmod +x /usr/local/bin/geckodriver \
    && apt-get autoremove -yqq --purge \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/geckodriver.tar.gz

USER airflow
COPY ./requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

