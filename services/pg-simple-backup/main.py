"""
Main file.
"""

import argparse
import logging
import sys


from actions.backup import backup_database
from actions.list import list_backups
from actions.restore import restore_backup


logger = logging.getLogger(__name__)

def set_up_logging():
    """
    Setup logging on stdout and setup levels.
    """
    root_logger = logging.getLogger('')
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(logging.StreamHandler(stream=sys.stdout))

    azure_logger = logging.getLogger('azure')
    azure_logger.setLevel(logging.WARNING)


def list_action(args):
    """
    Handler for list action.
    """
    logger.info('List action started.')

    try:
        list_backups(args.container, args.storage)

        logger.info('List action finished.')
        return True
    except Exception as exc: # pylint: disable=broad-except
        logger.exception('Exception occured while listing...', exc_info=exc)
        return False


def restore_action(args):
    """
    Handler for restore action.
    """
    logger.info('Restore action started.')

    try:
        restore_backup(args.container, args.file, args.storage, args.dbname)

        logger.info('Restore action finished.')
        return True
    except Exception as exc: # pylint: disable=broad-except
        logger.exception('Exception occured while restoring...', exc_info=exc)
        return False


def backup_action(args):
    """
    Handler for backup action.
    """
    logger.info('Backup action started.')

    try:
        backup_database(args.dbname, args.container, args.storage, args.database)

        logger.info('Backup action finished.')
        return True
    except Exception as exc: # pylint: disable=broad-except
        logger.exception('Exception occured while backuping...', exc_info=exc)
        return False


def main():
    """
    Main entry point.
    """
    args_parser = argparse.ArgumentParser(description='Postgres database backup and restore')
    actions = args_parser.add_subparsers(title='actions', description='possible actions')

    list_group = actions.add_parser(name='list', description='list all backups')
    list_group.add_argument('--storage', required=True, help='azure storage connection string')
    list_group.add_argument('--container', required=True, help='azure storage container name')
    list_group.set_defaults(func=list_action)

    restore_group = actions.add_parser(name='restore', description='restore databases or whole cluster from backup')
    restore_group.add_argument('--dbname',  required=True, help='postgres connection string (on whole cluster you should specify superuser)')
    restore_group.add_argument('--storage', required=True, help='azure storage connection string')
    restore_group.add_argument('--container', metavar='CONT', required=True, help='azure storage container name')
    restore_group.add_argument('--file', metavar='BLOB', required=True, help='blob in storage from where the backup is taken')
    restore_group.set_defaults(func=restore_action)

    backup_group = actions.add_parser(name='backup', description='backup databases or whole cluster')
    backup_group.add_argument('--dbname',  required=True, help='postgres connection string (on whole cluster you should specify superuser)')
    backup_group.add_argument('--storage', required=True, help='azure storage connection string')
    backup_group.add_argument('--container', metavar='CONT', required=True, help='azure storage container name')
    backup_group.add_argument('database', nargs='*', default=[], help='list of databases to backup (if empty it will backup everything)')
    backup_group.set_defaults(func=backup_action)

    args = args_parser.parse_args()
    # call the action func
    return args.func(args)


if __name__ == '__main__':
    set_up_logging()

    sys.exit(0 if main() else 1)
