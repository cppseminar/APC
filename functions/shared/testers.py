"""Functions for communication (and work) with testers running in some VMs."""
import base64
import contextlib
import dataclasses
import datetime
import http.client
import json
import logging
import math
import os
import socket
import urllib.parse
from typing import Dict, Any, Optional, Tuple

from ..shared import common, core, mongo

from jose import jws
from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.models import Entity

@dataclasses.dataclass
class TesterConfig:
    name: str
    url: str
    secret: bytes
    stop_url: Optional[str]   = None
    start_url: Optional[str]  = None
    stop_after: Optional[int] = None

@dataclasses.dataclass
class TestRequest(core.DataclassDict):
    return_url: str
    files: Dict[str, Any]
    docker_image: str
    max_run_time: int = 300
    memory: int = 512

    def map_item(self, item):
        mapper = {
            "return_url": "returnUrl",
            "files": "files",
            "max_run_time": "maxRunTime",
            "docker_image": "dockerImage",
            "memory": "memory",
        }
        key, value = item
        if key in mapper:
            key = mapper[key]
        return key, value



def send_message(message: dict, path: str, tester: TesterConfig, method="POST") -> Tuple[int, str]:
    """Sign and send message to tester.

    Returns tuple of (return code, body).
    """
    # First let's sign message
    formatted_message = json.dumps(
        {
            "timestamp": math.floor(datetime.datetime.now().timestamp()),
            "uri": str(path),
            "payload": dict(message)
        }
    )
    signed_message = jws.sign(
        formatted_message.encode("utf-8"),
        tester.secret,
        algorithm="HS256"
    )
    # Now send
    try:
        connection = http.client.HTTPConnection(
            tester.url, timeout=10
        )
        connection.request(method, path, signed_message)
        response = connection.getresponse()
        str_response = response.read()
        return response.getcode(), str_response.decode("utf-8")
    except (ConnectionRefusedError, TimeoutError, socket.timeout):
        logging.warning("Connection to vm %s (%s) timeout", tester.name, path)
        raise TimeoutError(f"Tester {tester.name} is offline")
    except Exception as error:
        logging.error(
            "Something went wrong with connection to server %s. %s %s",
            tester.name,
            type(error),
            error,
        )
        raise

def message_to_request(msg: bytes) -> TestRequest:
    """Convert message encoded by common.encode_message to request."""
    url, case_id, submission_id = common.decode_message(msg.decode("utf-8"))
    # We assume here, that data is valid, because it was generated by our code,
    # and not by user... so we skip error handling
    submission = mongo.MongoSubmissions().get_submission(submission_id)
    test_case = mongo.MongoTestCases().get_case(case_id)
    files = dict()
    for file_entry in submission.files:
        files[str(file_entry["fileName"])] = file_entry["fileContent"]
    return TestRequest(
        return_url=url,
        files=files,
        docker_image=test_case.docker,
    )


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
        )
        return dict_to_tester(tester_entry)
    except Exception as error:
        logging.error("Unable to query Tables for %s tester. %s %s", name, type(error), error)
        raise


def dict_to_tester(entry: dict):
    """Given result from Azure TABLE (dict), convert it to Tester dataclass.

    If this dictionary doesn't contain all required fields, error is logged
    and raised.
    """
    # This is a bit more complicated logic, to determine if this entry is
    # sufficient
    name = entry[common.TESTER_PARTITION_KEY]
    url = entry.get(common.TESTER_URL)
    stop_url = entry.get(common.TESTER_STOP_URL)
    start_url = entry.get(common.TESTER_START_URL)
    secret = base64.decodebytes(entry.get(common.TESTER_SECRET,"").encode("utf-8"))
    with contextlib.suppress(ValueError):
        stop_after = -1
        stop_after = int(entry.get(common.TESTER_STOP_AFTER, 0))
    if not url or not secret:
        raise ValueError(f"Url and Secret are required for vm f{name}")
    if stop_after > 0 and (not start_url or not stop_url):
        raise ValueError(f"Missing start and stop urls for f{name}")
    if not stop_after > 0:  # Stop after not set, or set to invalid value
        stop_after = 0
    return TesterConfig(
        name=name,
        url=url,
        stop_url=stop_url,
        start_url=start_url,
        secret=secret,
        stop_after=stop_after or None,
    )

def start_automation_job(url: str) -> bool:
    """Posts to azure automation."""
    url = str(url)
    url_parts = urllib.parse.urlparse(url)
    # Remove protocol from url
    uri = urllib.parse.urlunparse(["", *url_parts[1:]]).lstrip('/')
    # Remove also HOST, but not slash after HOST
    uri = uri.replace(url_parts.netloc, "", 1)

    connection = None
    if url_parts[0] != "https" or not url_parts.netloc:
        raise ValueError(f"Bad url format/protocol {url}")
    connection = http.client.HTTPSConnection(
        url_parts.netloc, timeout=10
    )

    try:
        connection.request("POST", uri , bytes())
        response = connection.getresponse()
        if response.status > 299:
            logging.error(
                "Azure automation returned http %s for %s",
                response.status,
                url
            )
            return False
        return True
    except (TimeoutError, ConnectionRefusedError, socket.timeout):
        logging.error("Azure automation to wake up %s timed out", tester.name)
        return False
