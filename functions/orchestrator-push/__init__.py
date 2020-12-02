"""Try to push message to vm and on failure wake up VM."""
import os
import logging

import azure.functions as func
from azure.durable_functions import DurableOrchestrationClient

from ..shared import common, mongo, testers

def main(message: str) -> str:
    try:
        url, case_id, submission_id = common.decode_message(message)
        submission = mongo.MongoSubmissions().get_submission(submission_id)
        test_case = mongo.MongoTestCases().get_case(case_id)
        files = dict()
        for file_entry in submission.files:
            files[str(file_entry["fileName"])] = file_entry["fileContent"]

        tester = testers.get_tester_config(name="default")
        signed_message = testers.build_message(
            return_url=url,
            files=files,
            docker_image=test_case.docker,
            memory=test_case.memory,
            key=tester.secret
        )
        return testers.send_message(signed_message, tester)
    except Exception as error:
        logging.error("Error with processing message %s %s", error, message)
        raise
