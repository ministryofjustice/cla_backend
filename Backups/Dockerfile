FROM amazon/aws-cli:latest

# Create a non-root user and group with UID/GID 1000
#RUN groupadd -g 1000 appuser && \
#    useradd --uid 1000 --gid 1000 --create-home --shell /bin/bash appuser
#
WORKDIR /tmp
#
## Copy application files
COPY . .
#
## Ensure the non-root user owns the application files
#RUN chown -R 1000:1000 /app

ENV HOME=/tmp

# Switch to the non-root user
USER 1000:1000
