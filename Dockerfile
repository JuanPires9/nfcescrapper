ARG PYTHON_VERSION=3.11.7

FROM python:${PYTHON_VERSION}-slim as base

# Set webdriver environment variables
ENV GECKDRIVER_VERSION=0.34.0
ENV LOCAL_BIN_PATH=/usr/local/bin
ENV WEBDRIVER_PATH=$LOCAL_BIN_PATH/geckodriver

# Update the package list and install the required dependencies and Firefox webdriver.
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates gnupg wget curl unzip firefox-esr libpq-dev build-essential \
    && curl -L "https://github.com/mozilla/geckodriver/releases/download/v$GECKDRIVER_VERSION/geckodriver-v$GECKDRIVER_VERSION-linux64.tar.gz" | tar xz -C $LOCAL_BIN_PATH \
    && chmod +x $LOCAL_BIN_PATH/geckodriver \
    && ln -sf /usr/bin/firefox-esr /usr/bin/firefox \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the source code into the container.
COPY . .

# Install the application's dependencies.
RUN pip install --upgrade pip
RUN python -m pip install -r requirements.txt --no-cache-dir

ENV PYTHONPATH=/app/src

# Expose the port that the application listens on.
EXPOSE 80

# Command to start the FastAPI server
CMD ["sh", "-c", "uvicorn api:app --host 0.0.0.0 --port ${PORT:-80}"]
