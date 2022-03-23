"""Orchestrator which starts VM and then pushes tests to it."""
import logging
import datetime
import json

from ..shared import common

import azure.functions as func
import azure.durable_functions as df


def orchestrator_function(context: df.DurableOrchestrationContext):
    message = context.get_input()
    _ = common.decode_message(message)  # Test if message format is ok
    current_time = context.current_utc_datetime
    for timeout in [90, 90 + 180, 90 + 180 + 320]:  # Timeouts 90, 180, 320
        # Launch vm if possible
        task1 = context.call_activity("start-vm", message)
        # sleep
        task2 = context.create_timer(
            current_time + datetime.timedelta(seconds=timeout)
        )
        yield context.task_all([task1, task2])
        result = yield context.call_activity("orchestrator-push", message)
        if result:
            return "Successfully pushed message to tester"
    logging.error("Finishing orchestrator unsuccesfully %s", message)
    return "Orchestrator failed"

main = df.Orchestrator.create(orchestrator_function)
