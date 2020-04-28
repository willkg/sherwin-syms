#!/bin/bash

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

set -e

if [ -z "$*" ]; then
    echo "usage: entrypoint.sh CMD"
    exit 1
fi

CMD=$1
shift

export FLASK_APP=/app/src/sherwin_syms/main.py

case ${CMD} in
    appdev)
        # This activates reloading, stack traces, etc
        export FLASK_ENV=development
        flask run --host=0.0.0.0 --port=5000
        ;;
    shell)
        exec bash
        ;;
    *)
        echo "Unknown CMD ${CMD}"
        exit 1
esac
