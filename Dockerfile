# FROM apache/airflow:latest
# USER root
# # Install Firefox and Geckodriver for Selenium
# RUN apt-get update \
#     && apt-get install -y --no-install-recommends \
#     firefox-esr \
#     wget \
#     && wget -q -O /tmp/geckodriver.tar.gz https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-linux64.tar.gz \
#     && tar -xzf /tmp/geckodriver.tar.gz -C /usr/local/bin/ \
#     && chmod +x /usr/local/bin/geckodriver \
#     && apt-get autoremove -yqq --purge \
#     && apt-get clean \
#     && rm -rf /var/lib/apt/lists/* /tmp/geckodriver.tar.gz

# USER airflow
# COPY ./requirements.txt /requirements.txt
# RUN pip install --no-cache-dir -r /requirements.txt
# RUn chmod +x /usr/local/bin/geckodriver
FROM apache/airflow:latest

USER root

# Install dependencies required for Firefox and Geckodriver
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    libdbus-glib-1-2 \
    libgtk-3-0 \
    libasound2 \
    libx11-xcb1 \
    libxtst6 \
    libxrender1 \
    libxrandr2 \
    libfontconfig1 \
    libxcb-shm0 \
    libxcb-render0 \
    xdg-utils

# Download and install the latest Firefox
RUN wget -O /tmp/firefox.tar.bz2 "https://download.mozilla.org/?product=firefox-latest&os=linux64&lang=en-US" \
    && tar -xjf /tmp/firefox.tar.bz2 -C /opt/ \
    && ln -s /opt/firefox/firefox /usr/local/bin/firefox \
    && rm /tmp/firefox.tar.bz2

# Download and install the latest Geckodriver
RUN wget -O /tmp/geckodriver.tar.gz https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-linux64.tar.gz \
    && tar -xzf /tmp/geckodriver.tar.gz -C /usr/local/bin/ \
    && chmod +x /usr/local/bin/geckodriver \
    && rm /tmp/geckodriver.tar.gz

# Clean up unnecessary files to reduce image size
RUN apt-get autoremove -y && apt-get clean && rm -rf /var/lib/apt/lists/*

# Switch back to non-root user airflow
USER airflow

# Install Python dependencies from requirements.txt
COPY ./requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
