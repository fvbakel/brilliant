#!/usr/bin/bash
SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
sqlite3 gadgetbridge-export.db <$SCRIPTPATH/extract.sql