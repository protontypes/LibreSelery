#!/bin/bash
token_location=~/.openselery/tokens.env

if [ ! -d $database_location ]
then
  mkdir $database_location
  chmod 700 $database_location
fi

if [ ! -f $token_location ]
then
  cat > $token_location <<EOF
  COINBASE_TOKEN=
  COINBASE_SECRET=
  GITHUB_TOKEN=
  LIBRARIES_IO_TOKEN=
  DATABASE_LOCATION=$database_location
EOF
  chmod 700 $token_location
fi

docker build --build-arg UID=$(id -u) --build-arg GID=$(id -g) -t openselery .
