"""Functions for communication (and work) with testers running in some VMs."""
import base64
import dataclasses
import datetime
import http.client
import json
import logging
import math
import os
from typing import Dict, Any

from jose import jws
from ..shared import common

@dataclasses.dataclass
class TesterConfig:
    name: str
    url: str
    start_url: str
    stop_url: str
    start_time: datetime.datetime

def build_message(
    *, return_url: str, files: Dict[str, Any], docker_image: str, memory: int
) -> bytes:
    """Returns signed message, which should be sent to vm.

    Signature is timestamped, so it should be sent as soon as possible.
    """
    formatted_message = json.dumps(
        {
            "timestamp": math.floor(datetime.datetime.now().timestamp()),
            "uri": "/",
            "payload": {
                "returnUrl": return_url,
                "files": files,
                "maxRunTime": 60 * 5,
                "dockerImage": docker_image,
                "memory": memory,
            },
        }
    )
    secret_key64 = os.environ[common.ENV_QUEUE_SECRET]
    decoded_key = base64.decodebytes(secret_key64.encode("utf-8"))
    signed = jws.sign(formatted_message.encode("utf-8"), decoded_key, algorithm="HS256")
    return signed.encode("utf-8")

def get_tester_config(*, name: str) -> TesterConfig:
    """Given vm name finds tester in db and retuns it's configuration.

    If vm doesn't exists, or it's entry is somehow corrupted, error will be
    raised.
    """
    if name != "default":
        raise Exception("Wrong tester name")
    return TesterConfig(
        name="default",
        start_time=datetime.datetime.now(),
        url=os.environ[common.ENV_QUEUE_URL],
        stop_url="",
        start_url="",
    )

def send_message(message: bytes, tester: TesterConfig) -> bool:
    """Sends message to tester and returns boolean indicating success."""
    try:
        connection = http.client.HTTPConnection(
            tester.url, timeout=10
        )
        connection.request("POST", "/", message)
        response = connection.getresponse()
        if response.status != 200:
            logging.warning("Tester %s returned status %s", tester.name, response.status)
            return False
        return True
    except ConnectionRefusedError:
        logging.warning("Connection to tester %s refused.", tester.name)
        return False
    except Exception as error:
        logging.error(
            "Something went wrong with connection to server %s. %s",
            tester.name,
            error
        )
        return False
