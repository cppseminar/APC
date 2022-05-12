#!/bin/bash

set -e # exit on first error

while test $# -gt 0; do
  case "$1" in
    -h|--help)
      echo "PG backup tool"
      echo " "
      echo "Backup databases or whole cluster to file. Output is simple"
      echo "text format in .gz or .tar.gz what is more appropriate. Use"
      echo "restore script to restore database."
      echo "$BASH_SOURCE [options] databases..."
      echo " "
      echo "options:"
      echo "  -h, --help                show brief help"
      echo "  -c, --dbname=CONN_STR     postgres connection string"
      echo "  -o, --output-dir=DIR      specify a directory to store backup in"
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
    -o|--output-dir)
      shift
      if test $# -gt 0; then
        OUTPUT_DIR=`readlink -f $1`
      else
        echo "No output dir specified!"
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


MYTMPDIR="$(mktemp -d)"
trap 'rm -rf -- "$MYTMPDIR"' EXIT

BACKUP_DIR="${MYTMPDIR}/backup/"
mkdir ${BACKUP_DIR}

function backup_whole_cluster {
  OUTPUT="${BACKUP_DIR}/pg_dumpall.sql"
  pg_dumpall --dbname $CONNECTION_STR --clean --if-exists --lock-wait-timeout=150000 --no-password --file ${OUTPUT}
}

function backup_databases {
  for DB in "$@"
  do
    OUTPUT="${BACKUP_DIR}/pg_dump_${DB}.sql"
    # based on https://stackoverflow.com/a/15966279
    DB_NAME=$(echo ${CONNECTION_STR} | sed --regexp-extended "/(postgres(ql)?:\/\/[^\/?]*)(\/[^?$]*|)(.*)/{s//\1\/${DB}\4/;h};\${x;/./{x;q0};x;q1}")
    pg_dump --dbname $DB_NAME --clean --if-exists --lock-wait-timeout=150000 --no-password --file ${OUTPUT}
  done
}

if [ "$#" -eq 0 ]; then
  echo "No databases specified, backuping whole cluster."
  backup_whole_cluster
else
  echo "Databases specified: $@"
  backup_databases $@
fi

DATE=`date -u +"%Y-%m-%dT%H-%M-%SZ"` 
FILENAME=`mktemp ${MYTMPDIR}/pg_backup-${DATE}.XXXXXXX.tar.gz`
cd ${BACKUP_DIR}
echo "Creating tar file..."
tar -zcvf ${FILENAME} *
mv ${FILENAME} ${OUTPUT_DIR}
echo "Finished, output ${OUTPUT_DIR}/$(basename ${FILENAME})."
