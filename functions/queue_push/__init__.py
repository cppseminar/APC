import base64
import http.client
import json
import logging
import os

import azure.functions as func
from jose import jws

from ..shared import common, mongo


def main(msg: func.QueueMessage) -> None:
    try:
        body = msg.get_body().decode("utf-8")
        url, case_id, submission_id = common.decode_message(body)
        submission = mongo.MongoSubmissions().get_submission(submission_id)
        test_case = mongo.MongoTestCases().get_case(case_id)
        files = dict()
        # TODO: Change format on frontend backend db ...
        for file_entry in submission.files:
            files[file_entry["fileName"]] = file_entry["fileContent"]
        query = json.dumps(
            {
                "returnUrl": url,
                "files": files,
                "maxRunTime": 20,
                "dockerImage": test_case.docker,
            }
        )
        logging.info("Ok %s", query)
        secret_key64 = os.environ[common.ENV_QUEUE_SECRET]
        decoded_key = base64.decodebytes(secret_key64.encode("utf-8"))

        request = jws.sign(query.encode("utf-8"), decoded_key, algorithm="HS256")

        connection = http.client.HTTPConnection(
            os.environ[common.ENV_QUEUE_URL], timeout=10
        )
        connection.request("POST", os.environ[common.ENV_QUEUE_URL], request)
        response = connection.getresponse()
        if response.status != 200:
            raise RuntimeError(f"Error status in queue {response.status}")

    except Exception as error:
        logging.error("Error during queue processing %s", error)
        raise
