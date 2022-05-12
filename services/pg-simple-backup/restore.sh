#!/bin/bash

set -e # exit on first error

while test $# -gt 0; do
  case "$1" in
    -h|--help)
      echo "PG restore tool"
      echo " "
      echo "Restore databases or whole cluster from file. File should"
      echo "be created with backup script."
      echo "$BASH_SOURCE [options] databases..."
      echo " "
      echo "options:"
      echo "  -h, --help                show brief help"
      echo "  -c, --dbname=CONN_STR     postgres connection string"
      echo "  -f, --file=FILE           specify a directory to store backup in"
      exit 0
      ;;
    -c|--dbname)
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


MYTMPDIR="$(mktemp -d)"
trap 'rm -rf -- "$MYTMPDIR"' EXIT

BACKUP_DIR="${MYTMPDIR}/backup/"
mkdir ${BACKUP_DIR}

cd ${BACKUP_DIR}
tar -xf ${BACKUP_FILE} 
echo ${BACKUP_DIR}

function restore_whole_cluster {
  INPUT="${BACKUP_DIR}/pg_dump_all.sql"
  psql --quiet --dbname $CONNECTION_STR --file $INPUT --no-password postgres
}

function restore_databases {
  for INPUT in $(ls pg_dump_*)
  do
    DB=$(echo "$INPUT" | sed -e "s/^pg_dump_//" -e "s/\.sql$//")
    echo $DB
    # based on https://stackoverflow.com/a/15966279
    DB_NAME=$(echo ${CONNECTION_STR} | sed --regexp-extended "/(postgres(ql)?:\/\/[^\/?]*)(\/[^?$]*|)(.*)/{s//\1\/${DB}\4/;h};\${x;/./{x;q0};x;q1}")
    psql --quiet --dbname $CONNECTION_STR --file $INPUT --no-password postgres
  done
}

if [ -f pg_dumpall.sql ]; then
  echo "Dumpall specified, restoring whole cluster."
  restore_whole_cluster
else
  echo "Dump specified, restoring all specified databases."
  restore_databases
fi
