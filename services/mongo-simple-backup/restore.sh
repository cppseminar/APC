#!/bin/sh

set -e # exit on first error

SCRIPT_NAME=`basename "$0"`

while test $# -gt 0; do
  case "$1" in
    -h|--help)
      echo "mongo restore tool"
      echo " "
      echo "Restore mongo databases from file. File should"
      echo "be created with backup script."
      echo "$SCRIPT_NAME [options]"
      echo " "
      echo "options:"
      echo "  -h, --help                show brief help"
      echo "  -c, --url=CONN_STR        mongo connection string"
      echo "  -f, --file=FILE           specify a file with backup"
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
    -f|--file)
      shift
      if test $# -gt 0; then
        BACKUP_FILE=`readlink -f $1`
      else
        echo "No backup file specified!"
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

if [ -z "$BACKUP_FILE" ]; then
  echo "Backup file is missing!"
  exit 1
fi

mongorestore --uri $CONNECTION_STR --archive=$BACKUP_FILE
