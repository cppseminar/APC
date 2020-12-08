"""This is activity function for azure orchestrations. It starts vms."""

import http.client
import logging
import urllib.parse

from ..shared import testers


def main(name: str) -> str:
    tester = testers.get_tester_config(name="default")
    if not tester.start_url:
        raise ValueError(f"Start url for tester {tester.name} is empty")

    url_parts = urllib.parse.urlparse(tester.start_url)
    # Remove protocol from url
    uri = urllib.parse.urlunparse(["", *url_parts[1:]]).lstrip('/')
    # Remove also HOST, but not slash after HOST
    uri = uri.replace(url_parts.netloc, "", 1)

    connection = None
    if url_parts[0] == "https":
        connection = http.client.HTTPSConnection(
           url_parts.netloc, timeout=10
        )
    else:
        connection = http.client.HTTPConnection(
            url_parts.netloc, timeout=10
        )
    try:
        connection.request("POST", uri , bytes())
        response = connection.getresponse()
        if response.status > 299:
            logging.error(
                "Azure automation returned http %s for %s",
                response.status,
                tester.name
            )
            raise PermissionError("Unable to turn on virtual machine {tester.name}")
        logging.info("Succesfully started job (turn on) tester %s", tester.name)
        return True
    except TimeoutError:
        logging.error("Azure automation to wake up %s timed out", tester.name)
        raise

