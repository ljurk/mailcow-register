# mailcow-register

an extenstion to mailcow that lets you create invitations to register in your mailcow instance

## How does it work?

Admin-Tasks:
- create invitation under `/admin`
- set all parameters for the mail account
    - username
    - quota
    - tls in
    - tls out
    - domain
    - active
- it will be saved with a unique token
- a url is created which contains username and token
- send url to user

User-Tasks:
- go to url
- set parameters for the mail account
    - Full Name
    - password
- Submit: Mail-Account will be created

## Installation

### docker-compose(traefik)
in this example `proxy` is the traefik network and `mailcowdockerized_mailcow-network` is mailcows network
```
version: '2'

services:
  redis:
    image: redis:5-alpine
    networks:
      - mailcow-register

  registration:
    image: mailcow-register:latest
    networks:
      - proxy
      - mailcow-register
      - mailcowdockerized_mailcow-network
    environment:
      - REGISTER_QUOTA=128
      - REGISTER_DEFAULT_TOKEN_LENGTH=128
      - ADMIN_PASSWORD=admin
      - API_HOST=http://nginx-mailcow/
      - API_TOKEN=SECRET
    labels:
      - "traefik.enable=true"
      - "traefik.docker.network=proxy"
      - "traefik.http.services.mailcow-register.loadbalancer.server.port=5000"
      - "traefik.http.routers.mailcow-register.rule=Host(`register.303v.cf`)"
      - "traefik.http.routers.mailcow-register.entrypoints=web-secure"
      - "traefik.http.routers.mailcow-register.tls=true"
      - "traefik.http.routers.mailcow-register.tls.certresolver=letsencrypt"

networks:
  proxy:
    external: true
  mailcowdockerized_mailcow-network:
    external: true
  mailcow-register:

```
