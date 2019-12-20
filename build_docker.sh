#!/bin/bash
database_location=~/.protontypes/db
[ -d $database_location ] || mkdir $database_location
chmod 700 $database_location
docker build --build-arg UID=$(id -u) --build-arg GID=$(id -g) -t protontypes .
