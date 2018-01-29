#!/usr/bin/env bash
set -e
DIR=$(dirname "$0")
cd ${DIR}/..

echo "py.test py.test"
py.test
echo "py.test OK :)"


