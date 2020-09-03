#!/usr/bin/env bash
# Never print SECRETS or TOKENS.

LIBRESELERY_TARGET_PROJECT=$1
if [ -z ${LIBRESELERY_TARGET_PROJECT} ]; then 
    echo "Please provide the directory path of the project you want to use with libreselery!"
    echo "run.sh <some_project_dir>"
    exit
fi


DOT_DIR="~/.libreselery/"
DOT_DIR="${DOT_DIR/#\~/$HOME}"
RESULT_DIR="${DOT_DIR/results}"
DOCKER_PATH_TARGET_DIR="/home/selery/runningrepo"

### opening permission for whoever wants to write here (docker container)
chmod 777 $RESULT_DIR

# Mount the argument folder into the container \
docker run --rm -it \
--env GITHUB_TOKEN=$GITHUB_TOKEN \
--env LIBRARIES_API_KEY=$LIBRARIES_API_KEY \
--env COINBASE_TOKEN=$COINBASE_TOKEN \
--env COINBASE_SECRET=$COINBASE_SECRET \
-v $LIBRESELERY_TARGET_PROJECT:$DOCKER_PATH_TARGET_DIR \
-v $(realpath $RESULT_DIR):/home/selery/ \
-v $(realpath $DOT_DIR/config):/home/selery/config \
-u $(id -u $USER):$(id -g $USER) \
  libreselery \
    --config $DOCKER_PATH_TARGET_DIR/selery.yml \
    --directory $DOCKER_PATH_TARGET_DIR \
    --result /home/selery/results \
    --tooling /home/selery/config/tooling_repos.yml

