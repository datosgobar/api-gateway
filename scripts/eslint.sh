#!/usr/bin/env bash
set -e
DIR=$(dirname "$0")
cd ${DIR}/..

echo "Running eslint"
npm run jscpd
echo "eslint OK :)"


