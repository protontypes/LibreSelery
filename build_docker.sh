[ -d ~/db ] || mkdir ~/db
docker build --build-arg UID=$(id -u) --build-arg GID=$(id -g) -t protontypes .
