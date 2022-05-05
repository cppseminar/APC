"""
File implementing all functions for backup.
"""
import contextlib
import logging
import subprocess
import tempfile
import os
import gzip
import shutil
import tarfile

from urllib.parse import urlparse, urlunparse
from datetime import datetime
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError

logger = logging.getLogger(__name__)

def backup_postgres_pg_dump(postgres_conn_str, dest_file, verbose=False, database=None):
    """
    Backup postgres db to a signle file.

    :param database: Name of database to backup (if None, we will dump all)
    """
    tool = 'pg_dumpall' if database is None else 'pg_dump'

    if database is not None:
        url_parts = urlparse(postgres_conn_str)
        postgres_conn_str = urlunparse(url_parts._replace(path=f'/{database}'))

    args = [
        tool,
        '--dbname', postgres_conn_str,
        '--clean',
        '--if-exists',
        '--file', dest_file,
        '--lock-wait-timeout=150000',
        '--no-password'
    ]

    if verbose:
        args.append('--verbose')

    env = {}
    if os.getenv('PGPASSWORD'):
        env['PGPASSWORD'] = os.getenv('PGPASSWORD')

    try:
        process = subprocess.run(args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=True,
            timeout=150,
            env=env
        )

        logger.info('%s succeeded', tool)
        logger.debug(process.stdout)
        
    except subprocess.CalledProcessError as exc:
        logger.error(exc.stdout)
        raise


def compress_file(in_file):
    """
    Compress selected file and return name of compressed file.
    """
    logger.info('Compressing %s', in_file)

    out_file = in_file + '.gz'

    with open(in_file, 'rb') as fin, gzip.open(out_file, 'wb') as fout:
        shutil.copyfileobj(fin, fout)

    logger.info('Compressed to %s', out_file)

    return out_file

def upload_file(filepath, container, azure_connection):
    """
    Uploads file to azure.

    Tries to create container, but is happy with it already existed.
    """
    service = BlobServiceClient.from_connection_string(azure_connection)

    container_client = service.get_container_client(container)

    with contextlib.suppress(ResourceExistsError):
        container_client.create_container()

    blob_client = container_client.get_blob_client(os.path.basename(filepath))

    with open(filepath, 'rb') as data:
        blob_client.upload_blob(data, timeout=300)


def backup_databases(db_connection, databases):
    """
    Backup selected databases.
    """
    logger.info('Backing up database(s) [%s] to azure storage started.', ', '.join(databases))

    path = tempfile.mkdtemp(suffix=datetime.now().isoformat())
    try:
        logger.info('Backup folder is %s', path)

        for database in databases:
            logger.info('Backing up db %s', database)
            db_path = os.path.join(path, database + '.out')
            backup_postgres_pg_dump(db_connection, db_path, False, database=database)

        file_desc, output_path = tempfile.mkstemp(prefix='pg_backup-', suffix=f'-{datetime.now().isoformat()}.tar.gz')
        logger.info('Output file is %s', output_path)
        try:
            with tarfile.open(output_path, "w:gz") as tar:
                for name in os.listdir(path):
                    tar.add(os.path.join(path, name), arcname=name)
        finally:
            os.close(file_desc)

        return output_path
    finally:
        shutil.rmtree(path)


def backup_whole_cluster(db_connection):
    """
    Backup whole database cluster, ideally db_connection should have
    superuser rights, otherwise some pieces of informations may be
    lost. 
    """
    logger.info('Backing up whole cluster started.')

    fd, path = tempfile.mkstemp(prefix='pg_backup_all-', suffix='-' + datetime.now().isoformat())
    try:
        logger.info('Backup file is %s', path)

        backup_postgres_pg_dump(db_connection, path, True)

        return compress_file(path)
    finally:
        os.close(fd)
        os.remove(path)


def backup_database(db_connection, azure_container, azure_connection, databases):
    """
    Function solely responsible for backup to azure blob storage.
    """
    if len(databases) == 0:
        path = backup_whole_cluster(db_connection)
    else:
        path = backup_databases(db_connection, databases)

    upload_file(path, azure_container, azure_connection)       
