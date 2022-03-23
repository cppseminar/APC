import datetime
import logging
import zipfile
import io
import os
import contextlib

import azure.functions as func
from azure.storage.blob import BlobClient, ContainerClient, generate_blob_sas
from bson import ObjectId

from ..shared import http, mongo, common, decorators, users

ROUTE_SETTINGS = {
    "task_id" : {
        decorators.DESTINATION: "task_id",
        decorators.VALIDATOR: decorators.object_id_validator,
    }
}

@decorators.login_required
@decorators.validate_parameters(route_settings=ROUTE_SETTINGS)
def get_download_link(request: func.HttpRequest, user: users.User, task_id=None):
    ...
    if task_id is None:
        return http.response_client_error()
    if not user.is_admin:
        return http.response_forbidden()

    task = mongo.MongoTasks().get_task(task_id)
    if task is None:
        return http.response_not_found()
    # Ok all checks are now fine, so let's go
    azure_container = ContainerClient.from_connection_string(
        os.environ[common.ENV_STORAGE_STRING],
        "tmp-downloads",
    )
    with contextlib.suppress(Exception):
        azure_container.create_container() # Ignore failure if already exists

    result = mongo.MongoSubmissions.get_aggregate_submissions(ObjectId(task_id))
    file_emulator = io.BytesIO()
    zip_file = zipfile.ZipFile(file_emulator, mode='w')
    for entry in result:
        if len(entry.files) > 1:
            # Write directory
            for file_entry in entry.files:
                zip_file.writestr(
                    f"{entry.user}/{file_entry['fileName']}",
                    file_entry["fileContent"]
                    )
        elif len(entry.files) == 1:
            zip_file.writestr(
                f"{entry.user}-{entry.files[0]['fileName']}",
                entry.files[0]['fileContent']
            )
        else:
            logging.error("Didn't find any files on submission %s", entry._id)
            return http.response_server_error()
    zip_file.close()

    # Upload
    zip_name = f"{task_id}-{task.name}.zip"
    azure_blob = azure_container.get_blob_client(zip_name)
    azure_blob.upload_blob(file_emulator.getbuffer().tobytes(), overwrite=True)
    # Generate signature
    token = generate_blob_sas(
        azure_blob.account_name,
        azure_blob.container_name,
        azure_blob.blob_name,
        account_key=azure_container.credential.account_key,
        permission='r',
        expiry=datetime.datetime.now() + datetime.timedelta(hours=1),
    )

    return http.response_ok({"link": azure_blob.url + "?" + token})


def main(req: func.HttpRequest) -> func.HttpResponse:
    dispatch = http.dispatcher(get=get_download_link)
    return dispatch(req)
