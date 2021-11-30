import argparse
import pathlib
from azure.cosmos import cosmos_client
from azure.storage.blob import ContainerClient

DB_NAME = "submissionsDb"
CONTAINER_TASKS = "tasks"
CONTAINER_SUBMISSIONS  = "submissions"
STORAGE_SUBMISSIONS = "submissions"

QUERY_DATES = """
SELECT DISTINCT VALUE submissions.UserEmail
 FROM submissions  
 WHERE submissions.TaskId = @TaskId
"""

QUERY_USER = """
SELECT VALUE  submissions.id
 FROM submissions  
 WHERE submissions.TaskId = @TaskId
  AND submissions.UserEmail = @UserEmail
 ORDER BY submissions.SubmittedOn DESC
 OFFSET 0 LIMIT 1
"""

def parse_arguments():
    parser = argparse.ArgumentParser(description="Submission downloader")
    parser.add_argument("--cosmos-string",
        dest="connection_string",
        help="Connection string from cosmos DB with SQL API (use READ only)",
        required=True)
    parser.add_argument("--storage-string",
        dest="storage_string",
        help="Connection string from storage account",
        required=True)
    parser.add_argument("--taskid",
        dest="task",
        help="Task id (guid) of task you want to download",
        required=True)
    return parser.parse_args()

def get_container(connection_string):
    client = cosmos_client.CosmosClient.from_connection_string(connection_string)
    database = client.get_database_client(DB_NAME)
    return database.get_container_client(CONTAINER_SUBMISSIONS)
    
def users_for_task(task_id: str, container):
    results = container.query_items(
            QUERY_DATES, parameters=[{"name": "@TaskId", "value": task_id}],
            enable_cross_partition_query=True)
    for user in results:
        yield user

def get_user_task_id(user, task, container):
    results = container.query_items(
            QUERY_USER, parameters=[
                {"name": "@TaskId", "value": task},
                {"name": "@UserEmail", "value": user}],
            enable_cross_partition_query=False)
    results = list(results)
    assert len(results) == 1, "More than one thing per 'id' in user table"
    return results[0]

def download_user_file(user, submission_id, blob_container):
    blob = blob_container.get_blob_client(f"{user}/{submission_id}")
    stream_downloader = blob.download_blob()
    return stream_downloader

def generate_downloader(task_id: str, container, storage_container, folder_path):
    def _func(user: str):
        unique_id = get_user_task_id(user, task_id, container)
        file_name = f"{user}-{unique_id}.cpp"
        with open(pathlib.Path(folder_path).joinpath(file_name), "wb") as f:
            stream = download_user_file(user, unique_id, storage_container)
            stream.download_to_stream(f)
    return _func

def get_download_folder_path(task_id):
    my_dir = pathlib.Path(__file__).parent
    target = my_dir.joinpath(task_id)
    target.mkdir(exist_ok=True)
    assert target.is_dir(), "Cleanup files around main.py!"
    assert not len(list(target.iterdir())), "Please remove old folder"
    return str(target)

if __name__ == "__main__":
    arguments = parse_arguments()
    connection_string = arguments.connection_string
    storage_string = arguments.storage_string
    task_id = arguments.task

    folder = get_download_folder_path(task_id)
    container = get_container(connection_string)
    storage_string = arguments.storage_string
    storage_container = ContainerClient.from_connection_string(
        storage_string, STORAGE_SUBMISSIONS
    )
    download_user_func = generate_downloader(
        task_id, container, storage_container, folder
    )

    print(f"Downloading all files to \"{folder}\"")
    users = list(users_for_task(task_id, container))
    print(f"[{' ' * len(users)}] ({len(users)})\n[", end='')
    for user in users_for_task(task_id, container):
        download_user_func(user)
        print("x", end='', flush=True)
    print("]")

