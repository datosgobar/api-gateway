#!/usr/bin/env bash
set -e
DIR=$(dirname "$0")
cd ${DIR}/..

echo "Running flake8"
flake8 --exclude = .git,__pycache__,docs/,requirements/, .env/, **/migrations/, deploy/
echo "flake8 OK :)"


