import os
import http
import logging

import azure.functions as func
from azure.durable_functions import DurableOrchestrationClient

from ..shared import common, mongo, testers


async def main(msg: func.QueueMessage, starter: str) -> None:
    body = msg.get_body()
    request = testers.message_to_request(body)
    tester = testers.get_tester_config(name="default")
    try:
        code, _ = testers.send_message(dict(request), "/test", tester)
        if code < 200 or code > 299:
            # Either VM is shutting down, or we have an error
            if code == http.HTTPStatus.SERVICE_UNAVAILABLE:
                # Vm is shutting down, this is the same as already turned off.
                # So let's emulate turned of vm by throwing timeout error
                raise TimeoutError("Vm is shutting down")
            # Message was not sent. Vm returned error.
            # There is no point in retrying this, so let's just swallow this
            # event
            logging.error(
                "Tester %s refused event with code(%s) %s",
                tester.name,
                code,
                body,
            )
    except TimeoutError as error:
        logging.info("Starting vm tester %s", tester.name)
        client = DurableOrchestrationClient(starter)
        await client.start_new("start-vm-orchestrator", client_input=body.decode("utf-8"))
    except Exception as error:
        logging.error("Error during queue processing %s %s", type(error), error)
        raise
