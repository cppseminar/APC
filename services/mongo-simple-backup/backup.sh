#!/bin/sh

set -e # exit on first error

SCRIPT_NAME=`basename "$0"`

while test $# -gt 0; do
  case "$1" in
    -h|--help)
      echo "mongo backup tool"
      echo " "
      echo "Backup database to file. Output is archive file."
      echo "Use restore script to restore database."
      echo "$SCRIPT_NAME [options]"
      echo " "
      echo "options:"
      echo "  -h, --help                show brief help"
      echo "  -c, --url=CONN_STR        mongo connection string"
      echo "  -o, --output=DIR          specify an output archive dir"
      exit 0
      ;;
    -c|--url)
      shift
      if test $# -gt 0; then
        CONNECTION_STR=$1
      else
        echo "No connection string specified!"
        exit 1
      fi
      shift
      ;;
    -o|--output)
      shift
      if test $# -gt 0; then
        OUTPUT_DIR=`readlink -f $1`
      else
        echo "No output directory specified!"
        exit 1
      fi
      shift
      ;;
    *)
      break
      ;;
  esac
done

if [ -z "$CONNECTION_STR" ]; then
  echo "Connection string is missing!"
  exit 1
fi

if [ -z "$OUTPUT_DIR" ]; then
  echo "Output directory is missing!"
  exit 1
fi

DUMP_VER=`mongodump --version | head -1 | cut -d\  -f3 | cut -d- -f1`

mongodump --uri $CONNECTION_STR --archive=$OUTPUT_DIR/$(date +"%Y-%m-%dT%H-%M-%S")-dump-${DUMP_VER}.mongodump
