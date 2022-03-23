import contextlib
import datetime
import json
import logging

from ..shared import testers

import azure.functions as func


def main(mytimer: func.TimerRequest) -> None:
    tester = testers.get_tester_config(name="default")
    stop_after = tester.stop_after
    if stop_after is None:
        return  # This vm is not configured to stop
    should_stop = False
    with contextlib.suppress(TimeoutError):
        code, result = testers.send_message({}, "/status", tester, method="GET")
        if code == 200:
            # Status returned successfully, let's check response
            try:
                result = json.loads(result)
                running = bool(result["running"])
                last_run = datetime.datetime.fromtimestamp(result["timestamp"])
                stop_when = last_run + datetime.timedelta(seconds=stop_after)

                if stop_when < datetime.datetime.now():
                    should_stop = True
                if not running:  # Someone else is stopping this VM
                    # Warn, because this might be problem with azure automation
                    logging.warning(f"VM {tester.name} is in stopping state!")
                    should_stop = False
            except KeyError as error:
                logging.error(f"Tester {tester.name} missing {error} in status")
            except ValueError as error:
                logging.error(f"Cannot parse status from {tester.name} {error}")

    if not should_stop:
        return
    # We don't expect timeout here, so fail if it happens
    code, _ = testers.send_message({}, "/stop", tester)
    if code > 299 or code < 200:
        # Also suspicious
        logging.warning("VM %s /stop returned %s", tester.name, code)
        return
    successfully_stopped = False
    with contextlib.suppress(ValueError):
        successfully_stopped = testers.start_automation_job(tester.stop_url)
    if not successfully_stopped:
        logging.error("Stop Automation failed for %s. Starting", tester.name)
        testers.send_message({}, "/start", tester)
    else:
        logging.info("Succesfully stopped vm %s", tester.name)



