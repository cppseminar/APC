import os
import logging

import azure.functions as func

from ..shared import common, mongo, testers


def main(msg: func.QueueMessage) -> None:
    try:
        body = msg.get_body().decode("utf-8")
        url, case_id, submission_id = common.decode_message(body)
        submission = mongo.MongoSubmissions().get_submission(submission_id)
        test_case = mongo.MongoTestCases().get_case(case_id)
        files = dict()
        for file_entry in submission.files:
            files[str(file_entry["fileName"])] = file_entry["fileContent"]

        signed_message = testers.build_message(
            return_url=url,
            files=files,
            docker_image=test_case.docker,
            memory=test_case.memory
        )
        tester = testers.get_tester_config(name="default")
        if not testers.send_message(signed_message, tester):
            # Message was not sent. Vm may be turned of
            logging.warning("Cannot send message to tester %s", tester.name)
            # Here launch orchestrator
            # But for now raise error
            raise Exception("Cannot send message to tester")
    except Exception as error:
        logging.error("Error during queue processing %s", error)
