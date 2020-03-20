#!/bin/bash
# Never print SECRETS or TOKENS.

TARGET_DIR="/home/selery/runningrepo/"
DOT_DIR="~/.openselery/"
DOT_DIR="${DOT_DIR/#\~/$HOME}"

# Mount the argument folder into the container \
docker run --rm -t \
--env GITHUB_TOKEN=$GITHUB_TOKEN \
--env LIBRARIES_API_KEY=$LIBRARIES_API_KEY \
--env COINBASE_TOKEN=$COINBASE_TOKEN \
--env COINBASE_SECRET=$COINBASE_SECRET \
--env INITIATE_PAYOUT=$INITIATE_PAYOUT \
-v $@:$TARGET_DIR \
-v $(realpath $DOT_DIR/results):/home/selery/results \
-v $(realpath $DOT_DIR/config):/home/selery/config \
-u $(id -u $USER):$(id -g $USER) \
openselery \
--config $TARGET_DIR/selery.yml --directory $TARGET_DIR --result /home/selery/results --tooling /home/selery/config/tooling_repos.yml


