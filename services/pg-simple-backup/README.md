# Tool for remote pg (full) backup

It only uses `pg_dump`, `pg_dumpall` and `psql` commands. And upload the files to azure blob storage. Backups are done in text mode, so the files are quite large.

## Usage

Run it with `--help` to see the usage. 

There are three modes you can run the tool.

1. `backup` for making full backup
2. `list` for listing of avaiable backups
3. `restore` for clean cluster restore

### Backup

Parameters are 

* `--storage` connection string for azure storage, e.g. `DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://172.27.128.1:10000/devstoreaccount1;` default connection string for azurite
* `--container` name of container within azure storage, e.g. `db-backup`
* `--dbname` coonection string for postgres server, e.g. `postgresql://postgres@172.27.128.1`, it can point to no database or even random database, it doesn't matter we will always backup either all or selected databases. *Note for whole cluster backup do not include password in the connection string, it is not considered secure, and `pg_dumpall` do not work very well with it.*
* 0-N positional parameters specifying databases to be stored (if empty whole cluster is tored)

All parameters are required. If it succeed it will get the backup, compress it and upload it to azure blob storage. 

## List

Parameters are

* `--storage` connection string for azure storage, e.g. `DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://172.27.128.1:10000/devstoreaccount1;` default connection string for azurite
* `--container` name of container within azure storage, e.g. `db-backup`

All parameters are required. It will list all the backups, you can use the name to restore the backup. 

### Backup

Parameters are 

* `--storage` connection string for azure storage, e.g. `DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://172.27.128.1:10000/devstoreaccount1;` default connection string for azurite
* `--container` name of container within azure storage, e.g. `db-backup`
* `--dbname` coonection string for postgres server, e.g. `postgresql://postgres@172.27.128.1`, it can point to no database or even random database, it doesn't matter we will always backup all, do not include password in the connection string, it is not considered secure, and `pg_dumpall` do not word very well wit it
* `--file` blob in azure storage we want to use for restore, e.g. `pg_backup-zer3kvx_-2022-05-03T09:34:48.723705.gz`. It should be either `.gz` for whole cluster backups or `.tar.gz` for only selected databases.

All parameters are required. If it succeed it will get the backup from storage, decompress it and apply to the server. It will replace the databases/tables.

## Passwords

Currently there are three ways to supply password for postgres user. 

1. Use environment `PGPASSWORD`, it is not considered secure, on some systems it will show in some logs. You will get warning, but it do work.
2. Use `.pgpass` file <https://www.postgresql.org/docs/current/libpq-pgpass.html>.
3. Embed it directly to connection string, still not very secure. For some reason this method do not work for whole cluster backup on at least some versions of postgres client tools. 