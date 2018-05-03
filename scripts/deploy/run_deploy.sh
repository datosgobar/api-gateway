#!/bin/bash

set -e;

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

ENVIRONMENT="$1"

# Cargo variables dependiendo del ambiente
echo "Inicializando"
. "$DIR/variables.sh" "$ENVIRONMENT"
echo "Preparando"
"$DIR/prepare.sh"
echo "Deploying"
"$DIR/update.sh" "$ENVIRONMENT"
