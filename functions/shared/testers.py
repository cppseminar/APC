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

from ..shared import common

from jose import jws
from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.models import Entity

@dataclasses.dataclass
class TesterConfig:
    name: str
    url: str
    start_url: str
    stop_url: str
    start_time: datetime.datetime
    secret: bytes

def build_message(
    *, return_url: str, files: Dict[str, Any], docker_image: str, memory: int, key: bytes
) -> bytes:
    """Returns signed message, which should be sent to vm.

    Signature is timestamped, so it should be sent as soon as possible.
    """
    formatted_message = json.dumps(
        {
            "timestamp": math.floor(datetime.datetime.now().timestamp()),
            "uri": "/test",
            "payload": {
                "returnUrl": return_url,
                "files": files,
                "maxRunTime": 60 * 5,
                "dockerImage": docker_image,
                "memory": memory,
            },
        }
    )
    signed = jws.sign(formatted_message.encode("utf-8"), key, algorithm="HS256")
    return signed.encode("utf-8")


def get_tester_config(*, name: str) -> TesterConfig:
    """Given vm name finds tester in db and retuns it's configuration.

    If vm doesn't exists, or it's entry is somehow corrupted, error will be
    raised.
    """
    try:
        table_service = TableService(
            connection_string=os.environ[common.ENV_STORAGE_STRING]
        )
        tester_entry = table_service.get_entity(
            common.TABLE_VM_NAME,
            name,
            "config",
            timeout=10,
            select="secret,startURL,stopURL,startTime,url,PartitionKey"
        )
        return TesterConfig(
            name=tester_entry["PartitionKey"],
            start_time=tester_entry["startTime"],
            url=tester_entry["url"],
            stop_url=tester_entry["stopURL"],
            start_url=tester_entry["startURL"],
            secret=base64.decodebytes(tester_entry["secret"].encode("utf-8"))
        )
    except Exception as error:
        logging.error("Unable to query Tables for %s tester. %s %s", name, type(error), error)
        raise



def send_message(message: bytes, tester: TesterConfig) -> bool:
    """Sends message to tester and returns boolean indicating success.

    We swallow all kinds of errors.
    """
    try:
        connection = http.client.HTTPConnection(
            tester.url, timeout=10
        )
        connection.request("POST", "/test", message)
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
