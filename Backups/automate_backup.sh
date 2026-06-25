FROM amazon/aws-cli

WORKDIR /app

COPY . .

RUN chmod +x Backups/automate_backup.sh

CMD ["sh", "Backups/automate_backup.sh"]