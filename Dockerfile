FROM python:3.8.2-slim

# Set up user and group
ARG groupid=10001
ARG userid=10001

WORKDIR /app/
RUN groupadd --gid $groupid app && \
    useradd -g app --uid $userid --shell /usr/sbin/nologin --create-home app && \
    chown app:app /app/

# Install OS-level things
RUN apt-get update && \
    apt-get install -y apt-transport-https

# Install Socorro Python requirements
COPY --chown=app:app requirements.txt /app/requirements.txt
RUN pip install -U 'pip>=8' && \
    pip install --no-cache-dir -r requirements.txt && \
    pip check --disable-pip-version-check

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# The app user should own everything under /app in the container
USER app

# Copy everything over
COPY --chown=app:app . /app/

# Set entrypoint for this image
ENTRYPOINT ["/app/entrypoint.sh"]
