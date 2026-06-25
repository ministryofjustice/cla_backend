FROM amazon/aws-cli

RUN useradd -m -u 1000 appuser

WORKDIR /app

COPY . .

RUN chown -R appuser:appuser /app

USER 1000