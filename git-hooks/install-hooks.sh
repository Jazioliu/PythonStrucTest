#!/bin/bash

readonly ROOT_PATH=$(git rev-parse --show-toplevel)
readonly GIT_DIR=$(git rev-parse --git-dir)

readonly GIT_PREPUSH_PATH=$GIT_DIR/hooks/pre-push
readonly PREPUSH_PATH=$ROOT_PATH/git-hooks/pre-push/pre-push.sh

echo "Installing hooks..."

# this command creates symlink to our pre-push script
sed -i 's/\r$//' $PREPUSH_PATH
ln -s -f $PREPUSH_PATH $GIT_PREPUSH_PATH

echo "Done!"
read -r -p "Press any key to continue" -n 1
