"""This is activity function for azure orchestrations. It starts vms."""

import http.client
import logging
import urllib.parse

from ..shared import testers


def main(name: str) -> str:
    tester = testers.get_tester_config(name="default")
    if not tester.start_url:
        raise ValueError(f"Start url for tester {tester.name} is empty")
    return testers.start_automation_job(tester.start_url)

