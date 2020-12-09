"""Try to push message to vm and on failure wake up VM."""
import os
import logging

import azure.functions as func
from azure.durable_functions import DurableOrchestrationClient

from ..shared import common, mongo, testers

def main(message: str) -> str:
    try:
        request = testers.message_to_request(message.encode("utf-8"))
        tester = testers.get_tester_config(name="default")
        try:
            code, _ = testers.send_message(dict(request), "/test", tester)
        except TimeoutError:
            return False
        if code < 200 or code > 299:
            logging.error("Tester %s returned code %s after wake up", tester.name, code)
            raise RuntimeError(f"Tester {tester.name} failed to send message")
        return True  # We sent message ok
    except Exception as error:
        logging.error("Error with processing message %s %s", error, message)
        raise
