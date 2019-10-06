# http://example.com/
server {
    listen 80;
    listen [::]:80;
    server_name ungeeks.com ungeeks;
    root /var/www/ungeeks.com;
}

# http://www.example.com/ => http://example.com/
server {
    listen 80;
    listen [::]:80;
    server_name www.ungeeks.com;
    return 301 http://ungeeks.com$request_uri;
}
