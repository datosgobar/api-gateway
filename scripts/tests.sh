#!/usr/bin/env bash
set -e
DIR=$(dirname "$0")
cd ${DIR}/..

echo "py.test"
DJANGO_SETTINGS_MODULE=conf.settings.testing py.test $@
echo "py.test OK :)"


