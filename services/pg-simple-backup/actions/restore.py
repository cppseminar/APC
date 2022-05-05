"""
Functions to be use for db restore.
"""
import logging
import tempfile
import os
import gzip
import shutil
import subprocess
import tarfile

from pathlib import Path
from urllib.parse import urlparse, urlunparse
from azure.storage.blob import BlobServiceClient

logger = logging.getLogger(__name__)

class UnknownBackupType(Exception):
    """
    Exception is thrown when unknow format of backup is excountered. Currently
    we support .gz for whole database backups and .tar.gz for some databases
    backup.
    """


def download_file(azure_container, azure_blob, azure_connection):
    """
    Donwload azure blob to file.
    """
    logger.info('Downloading blob %s from container %s...', azure_blob, azure_container)

    service = BlobServiceClient.from_connection_string(azure_connection)

    container_client = service.get_container_client(azure_container)
    blob_client = container_client.get_blob_client(azure_blob)
    stream = blob_client.download_blob()

    temp_dir = tempfile.mkdtemp()

    file_path = os.path.join(temp_dir, blob_client.blob_name)
    with open(file_path, 'wb') as file:
        stream.readinto(file)

    logger.info('File downloaded to %s.', file_path)
    return file_path


def decompress_file(in_file):
    """
    Compress selected file and return name of compressed file.
    """
    logger.info('Decompressing %s', in_file)

    out_file = os.path.splitext(in_file)[0] + '.out'

    with gzip.open(in_file, 'rb') as fin, open(out_file, 'wb') as fout:
        shutil.copyfileobj(fin, fout)

    logger.debug('Compressed size %d', os.stat(in_file).st_size)
    logger.debug('Decompressed size %d', os.stat(out_file).st_size)

    logger.info('Decompressed to %s', out_file)

    return out_file

def restore_postgres_db(postgres_conn_str, src_file):
    """
    Restore postgres server from single file.
    """
    args = [
        'psql',
        '--dbname', postgres_conn_str,
        '--file', src_file,
        '--no-password',
        'postgres',
    ]

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

        logger.info('psql succeeded to restore db')
        logger.debug(process.stdout)
    except subprocess.CalledProcessError as exc:
        logger.error(exc.stdout)
        raise


def restore_databases(db_connection, backup_file):
    temp_dir = tempfile.mkdtemp()
    logger.info('Decompressing files to folder %s', temp_dir)

    with tarfile.open(backup_file) as tarball:
        tarball.extractall(temp_dir)

    for file in os.listdir(temp_dir):
        db_name = Path(file).stem

        url_parts = urlparse(db_connection)
        db_connection = urlunparse(url_parts._replace(path=f'/{db_name}'))

        restore_postgres_db(db_connection, os.path.join(temp_dir, file))


def restore_whole_cluster(db_connection, backup_file):
    file = decompress_file(backup_file)

    restore_postgres_db(db_connection, file)


def restore_backup(azure_container, azure_blob, azure_connection, db_connection):
    """
    Restore databases from one file in azure blob storage.
    """
    downloaded_file = download_file(azure_container, azure_blob, azure_connection)
    try:
        if downloaded_file.endswith('.tar.gz'):
            restore_databases(db_connection, downloaded_file)
        elif downloaded_file.endswith('.gz'):
            restore_whole_cluster(db_connection, downloaded_file)
        else:
            raise UnknownBackupType('Only .gz and .tar.gz files are supported!')
    finally:
        os.remove(downloaded_file)
