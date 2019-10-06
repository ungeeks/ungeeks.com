# https://example.com/
server {
    listen 443 ssl;
    listen [::]:443 ssl;

    server_name ungeeks.com ungeeks;

    ssl_certificate /etc/letsencrypt/live/ungeeks.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ungeeks.com/privkey.pem;

    root /var/www/ungeeks.com;
}

# https://www.example.com/ => https://example.com/
server {
    listen 443 ssl;
    listen [::]:443 ssl;

    server_name www.ungeeks.com;

    ssl_certificate /etc/letsencrypt/live/ungeeks.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ungeeks.com/privkey.pem;

    return 301 https://ungeeks.com$request_uri;
}

# http://example.com/, http://www.example.com/ => https://example.com/
server {
    listen 80;
    listen [::]:80;
    server_name ungeeks.com www.ungeeks.com;
    return 301 https://ungeeks.com$request_uri;
}
