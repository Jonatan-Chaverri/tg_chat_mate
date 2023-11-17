docker-compose down
docker volume prune -f
docker system prune -af
echo "Docker cleanup complete."
git pull
docker compose up -d

set -a
source .env
set +a


if [[ test5.telegram-crm.work =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "ip conf from sh skipped"
else
    docker exec anonymous_support_bot-nginx-service-1 /bin/bash -c "apt-get update && apt-get install -y python3 && \
    apt-get install -y certbot python3-certbot-nginx && \
    sed -i \"s/SERVER_IP_PLACEHOLDER/test5.telegram-crm.work/g\" /home/cert_bot_base.conf && \
    sed -i \"s/SERVER_IP_PLACEHOLDER/test5.telegram-crm.work/g\" /home/cert_bot_default.conf && \
    cp /home/cert_bot_base.conf /etc/nginx/conf.d/default.conf && \
    certbot --nginx -d test5.telegram-crm.work --register-unsafely-without-email --agree-tos --no-eff-email --force-renewal && \
    cp /home/cert_bot_default.conf /etc/nginx/conf.d/default.conf && \
    cp /etc/letsencrypt/live/test5.telegram-crm.work/fullchain.pem /nginx-certs/test5.telegram-crm.work/fullchain.pem && \
    cp /etc/letsencrypt/live/test5.telegram-crm.work/privkey.pem /nginx-certs/test5.telegram-crm.work/privkey.pem && \
    cp /etc/letsencrypt/options-ssl-nginx.conf /nginx-certs/ && \
    cp /etc/letsencrypt/ssl-dhparams.pem /nginx-certs/ "

fi

docker compose down
docker compose up -d

