"""Module containing core infrastructure for testscripts."""

import abc
import dataclasses
import re
import itertools
import collections
import enum
from typing import Iterable, Deque, Tuple, List

def build_event_regex(pattern: str):
    """We want to support only asterix as wildcard, so this function builds
    regex, from asterix only notation"""
    regex_parts: Iterable[Tuple[str, str]] = [(re.escape(part), r'\S*')
                                              for part in pattern.split('*')]
    parts: List[str] = list(itertools.chain.from_iterable(regex_parts))
    parts.pop() # Last one is not asterix
    parts = ['^'] + parts + ['$']
    return re.compile(''.join(parts))


def get_event_name(event):
    if hasattr(event, '__name__'):
        return str(event.__name__)
    return str(event)


class TestScript:
    """Class representing current run of testscript"""
    class EventPriority(enum.IntEnum):
        LOW = 0
        HIGH = 10

    def __init__(self):
        """asd"""
        self.modules: Iterable[Module] = collections.deque()
        self.event_stack: Deque[Event] = collections.deque()

    def register(self, module):
        """Call to register module to this object. All events will be sent to
        the module.handle_event function."""
        assert module not in self.modules, f"Module already registered"
        self.modules.append(module)
        module.register(self)

    def add_event(self, event, priority=EventPriority.LOW):
        """Adds event, wich will be processsed when run() function gets to
        it. Depending on priority, it might be last event in whole program"""
        if priority > TestScript.EventPriority.LOW:
            self.event_stack.append(event)
        else:
            self.event_stack.appendleft(event)

    def run(self):
        """Cycle which runs while there are still some events"""
        while self.event_stack:
            event = self.event_stack.pop()
            for module in self.modules:
                module.handle_event(event)

# class TestScriptProxy: # Maybe later



class Module(abc.ABC):
    """Class serving as module for TestScript class"""
    SETTINGS = {
        'verbose' : [True, False]
    }

    def __init__(self):
        self.owner = None
        self.events: Deque[Tuple[re.Pattern, callable]] = collections.deque()

    def register(self, parent_object: TestScript):
        """Registers parent, so module can send events to them"""
        assert not self.owner
        self.owner = parent_object

    def register_event(self, event, callback=None):
        event_name = get_event_name(event)
        regex = build_event_regex(event_name)

        if not callback:
            callback = self.handle_internal

        self.events.append((regex, callback))

    def send(self, event):
        """Do somethings"""
        if self.owner:
            self.owner.add_event(event)

    def handle_event(self, event):
        # Decide whether to accept or pass
        for regex, callback in self.events:
            if regex.fullmatch(event.name):
                ret = callback(event)
                if ret is not None:
                    return ret
                return True
        return False

    @abc.abstractmethod
    def handle_internal(self, event):
        # This should be overridden
        return False

@dataclasses.dataclass
class Event:
    # Handled true/false # TestScript must know
    # Return to ....
    # For whom
    # Payload
    # Private data
    # Response

    def __init__(self, name=None):
        self.name = name
        self.names = []

        if not self.name: # Name will be name of class
            self.names = list(map(lambda x: x.__name__, self.__class__.__mro__))
            self.name = self.names[0]
