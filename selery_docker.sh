#!/bin/bash
# Never print SECRET or TOKENS.

TARGET_DIR="/home/selery/runningrepo"

# Mount the argument folder into the container \
docker run --rm \
--env GITHUB_TOKEN=$GITHUB_TOKEN \
--env LIBRARIES_IO_TOKEN=$LIBRARIES_IO_TOKEN \
--env COINBASE_TOKEN=$COINBASE_TOKEN \
--env COINBASE_SECRET=$COINBASE_SECRET \
-v $@:$TARGET_DIR \
openselery \
bash -c "python selery.py --config $TARGET_DIR/openselery.yml --directory $TARGET_DIR" \

