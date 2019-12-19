[ -d ~/db ] || mkdir ~/db
chmod 700 ~/db
docker build --build-arg UID=$(id -u) --build-arg GID=$(id -g) -t protontypes .
