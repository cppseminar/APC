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

# next line will change the connection string to not contain admin database
# this is quite a hack, but mongodb operator used in this project will add
# the admin db to its connection strings and once mongodump sees it, it will
# no longer dump whode server (all dbs), but just this database, this will
# fis it :(
CONNECTION_STR_WHOLE_DB=`echo ${CONNECTION_STR} | sed -e s#\/admin\?#\/\?#g`

# restore can be done by running
# mongorestore --uri $CONNECTION_STR_WHOLE_DB --archive=$BACKUP_FILE

mongodump --uri $CONNECTION_STR_WHOLE_DB --archive=$OUTPUT_DIR/$(date +"%Y-%m-%dT%H-%M-%S")-dump-${DUMP_VER}.mongodump
