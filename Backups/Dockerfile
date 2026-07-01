FROM amazon/aws-cli:2.35.13

WORKDIR /tmp

## Copy application files
COPY . .

ENV HOME=/tmp

# Switch to the non-root user
USER 1000:1000
