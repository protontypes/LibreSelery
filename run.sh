#!/bin/bash
# Never print SECRET or TOKENS.

TARGET_DIR="/home/selery/runningrepo"

# Mount the argument folder into the container \
docker run --rm -t \
--env GITHUB_TOKEN=$GITHUB_TOKEN \
--env LIBRARIES_API_KEY=$LIBRARIES_API_KEY \
--env COINBASE_TOKEN=$COINBASE_TOKEN \
--env COINBASE_SECRET=$COINBASE_SECRET \
-v $@:$TARGET_DIR \
-v $(pwd):$(pwd)/results \
-u $(id -u ${USER}):$(id -g ${USER}) \
openselery \
    bash -c "python selery.py --config $TARGET_DIR/selery.yml --directory $TARGET_DIR --result $(pwd)/results"

