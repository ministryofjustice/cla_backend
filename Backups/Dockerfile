FROM amazon/aws-cli:latest

WORKDIR /tmp

## Copy application files
COPY . .

ENV HOME=/tmp

# Switch to the non-root user
USER 1000:1000
