#!/bin/bash

echo "!!! DO NOT FORGET TO CONFIGURE YOUR DNS TO RESOLVE *.example.com TO TRAEFIK !!!"

if [ ! -f "volumes/traefik_data/example.com.crt" ]; then
  (
    cd volumes/traefik_data;
    ./generate-certificate.sh
  )
fi

docker compose up --build -d --wait &>/dev/null
sleep 10 # give time to traefik to setup

echo -n "Requesting 'www.example.com' should return httpservice => "
curl -sk https://www.example.com | head -n1
echo

echo -n "Requesting 'otherdomain.example.com' should return httpservice => "
curl -sk https://otherdomain.example.com | head -n1
echo

docker compose down -v &>/dev/null
