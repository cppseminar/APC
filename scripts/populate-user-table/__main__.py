import os
import argparse

from azure.data.tables import TableClient
from azure.core.exceptions import ResourceExistsError, HttpResponseError


def create_entities(file_path, is_admin):
    entities = []
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line == '':
                continue

            entities.append({
                "PartitionKey": line,
                "RowKey": "isStudent",
                "ClaimValue": True,
            })

            entities.append({
                "PartitionKey": line,
                "RowKey": "isAdmin",
                "ClaimValue": is_admin,
            })

    return entities

def run(args):
    connection_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')

    with TableClient.from_connection_string(connection_str, args.table) as table_client:
        try:
            table_client.create_table()
        except HttpResponseError:
            print("Table already exists, do you want to replace? If no data will be merged. (yes/no)")
            answer = input()
            if answer == 'yes':
                table_client.delete_table()
                print('Table deleted, try to run the script after some time...')
                return

        entities = create_entities(args.students, False)
        entities += create_entities(args.admins, True)

        for i in entities:
            try:
                table_client.create_entity(i)
            except ResourceExistsError:
                print(f'Entity already exists ${i.PartitionKey}, skipped!')


if __name__ == '__main__':
    parser = argparse.ArgumentParser("populate-user-table")

    parser.add_argument('--table', type=str, default='usersTable')
    parser.add_argument('--students', type=str, required=True)
    parser.add_argument('--admins', type=str, required=True)

    args = parser.parse_args()

    run(args)
