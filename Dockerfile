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
# Sử dụng image chuẩn của Airflow
FROM apache/airflow:2.5.0

# Cập nhật hệ thống và cài đặt các gói cần thiết
USER root
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    firefox-esr \
    gnupg \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Tải xuống và cài đặt phiên bản Geckodriver mới nhất (v0.35.0)
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.35.0/geckodriver-v0.35.0-linux64.tar.gz && \
    tar -xvzf geckodriver-v0.35.0-linux64.tar.gz && \
    mv geckodriver /usr/local/bin/ && \
    rm geckodriver-v0.35.0-linux64.tar.gz

# Thiết lập thư mục cache Selenium và thay đổi quyền cho phép
RUN mkdir -p /home/airflow/.cache/selenium && \
    chown -R airflow:airflow /home/airflow/.cache/selenium

# Thiết lập quyền cho thư mục làm việc của Airflow
RUN chown -R airflow:airflow /opt/airflow

# Quay lại sử dụng người dùng airflow
USER airflow

# # Thiết lập biến môi trường cho Selenium để sử dụng đường dẫn cache đã chỉ định
# ENV XDG_CACHE_HOME=/home/airflow/.cache

# # Khởi chạy Airflow
# ENTRYPOINT ["tini", "--"]
# CMD ["bash", "-c", \
#     "airflow db upgrade && \
#     airflow users create --username admin --firstname Airflow --lastname Admin --role Admin --password admin --email admin@example.com && \
#     airflow webserver & airflow scheduler"]

