
#!/bin/sh

python /app/fuel-cards/manage.py createcachetable

python /app/fuel-cards/manage.py runserver 0.0.0.0:${WEB_PORT}

