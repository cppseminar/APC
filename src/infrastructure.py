"""Module containing core infrastructure for testscripts."""

import abc
import collections
import configparser
import contextlib
import dataclasses
import enum
import itertools
import os
import re
import logging
import sys

from dataclasses import MISSING
from typing import Any, Deque, Dict, Iterable, List, Tuple

import constants

# pylint: disable=too-few-public-methods


def build_wildcard_regex(pattern: str):
    """We want to support only asterix as wildcard, so this function builds
    regex, from asterix only notation"""
    regex_parts: Iterable[Tuple[str, str]] = [(re.escape(part), r'\S*')
                                              for part in pattern.split('*')]
    parts: List[str] = list(itertools.chain.from_iterable(regex_parts))
    parts.pop()  # Last one is not asterix
    parts = ['^'] + parts + ['$']
    return re.compile(''.join(parts))


def _map_to_strings(iterable: Iterable):
    """Transform values in ITER to strings"""
    return map(lambda x: str(x), iterable)


def config_section_to_dict(parser: configparser.ConfigParser,
                           section_name: str):
    """Simply extracts section from ConfigParser (PARSER) as dictionary"""
    values = dict()
    for option in parser.options(section_name):
        values[option] = parser.get(section_name, option)
    return values


def _get_event_name(event):
    if hasattr(event, '__name__'):
        return str(event.__name__)
    return str(event)


def get_valid_event(event: Any):
    """There might be a scenario, with event only as str having just a name"""
    try:
        event.name
        return event
    except AttributeError:
        # We could instead set name attribute for event, but I think it's not
        # wise to modify it here
        return _NamedEvent(str(event))


def set_logger(name, console=True, filename=None):
    """Retrieves from logging NAME logger and sets formats depending on
    CONSOLE and FILENAME"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    if filename:
        raise NotImplementedError("C'mon")
    if console:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(constants.CONFIG.CONSOLE_LOG_FORMAT)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


_logger = set_logger(__name__, console=True)


######################################################
#                   # EVENTS #                       #
######################################################


@dataclasses.dataclass()
class Event:
    """Abstract class for representing an event."""
    # Handled true/false # TestScript must know
    # Return to ....
    # For whom
    # Payload
    # Private data
    # Response

    def __post_init__(self):
        self.names = list(map(lambda x: x.__name__, self.__class__.__mro__))
        self.name = self.names[0]


class _NamedEvent(Event):
    """This class really shouldn't be used, it's here just in case someone
    enters string instead of evnet"""
    def __init__(self, name):
        super().__init__()
        self.name = name


@dataclasses.dataclass
class Notification(Event):
    message: str = ''
    severity: int = logging.INFO
    payload: str = ''

############################################
#              # END EVENTS #              #
############################################


class ConfigError(ValueError):
    def __init__(self, message):
        super().__init__(f"\nCONFIG ERROR:"
                         f"\n============\n\t\t{message}")

############################################
#               # PARSERS #                #
############################################


class SettingsParser:
    """Abstract class for parsing setting values.  If you don't know possible
    values in advance (like file name), you must use parser"""

    @property
    def default(self):
        return MISSING

    @abc.abstractmethod
    def is_valid(self, value: str) -> bool:
        """Returns True if value is valid. False otherwise, or raise config
        error"""
        raise ConfigError(f"Default parser doesn't accept anything ({value})")

    @abc.abstractmethod
    def get_options(self) -> Iterable[str]:
        """Return iterable of strings, representing possible values"""
        return ["<Example1>", "[Example 2]"]

    def __str__(self):
        return NotImplemented

    def __repr__(self):
        return NotImplemented


class FileNameParser(SettingsParser):
    def __init__(self, accept_ne=False):
        super().__init__()
        self.check_exist = not accept_ne

    def is_valid(self, value):
        """If accept_ne is false, checks whether file exists"""
        if self.check_exist and not os.path.exists(str(value)):
            raise ConfigError(f"File doesn't exist {value}")
        return True

    def get_options(self):
        return ["<file name>"]


class AnyStringParser(SettingsParser):
    """Accept any one word string as valid"""

    def is_valid(self, value:str) -> bool:
        """Return true if value is only one word"""
        if value and value.split()[0] == value:
            return True
        return False

    def get_options(self):
        return ["<any one word answer>"]

############################################
#             # END PARSERS #              #
############################################


class ModuleSettings(collections.UserDict):
    def __init__(self):
        super().__init__()
        self._settings = dict()
        self._defaults = set()  # keys with default options
        self._parsers = set()  # keys with parsers

    def add_options(self, key: str, values: List, default=MISSING):
        """Set possible options for KEY. VALUES must be iterable, with every
        member having __str__ implemented"""
        assert key not in self.data, "Key already registered"
        assert len(values)
        key = str(key)
        self.data[key] = list(values)
        if default != dataclasses.MISSING:
            self[key] = str(default)
            i = self.data[key].index(default)
            # Move default parameter to position 0, for better ini output
            self.data[key][i], self.data[key][0] = self.data[key][0], self.data[key][i]
            self._defaults.add(key)

    def add_parser(self, key: str, parser: SettingsParser):
        """Register PARSER for KEY. If setting with key is present, PARSER
        methods will be called"""
        assert key not in self.data, f"Key already registered {key}"
        self.data[key] = parser
        self._parsers.add(key)
        if parser.default != MISSING:
            try:  # This seems like common error to me
                assert parser.is_valid(parser.default), \
                       f"Parser default invalid {parser.default}"
            except TypeError as e:
                txt = f"Don't forget to instantiate parser {parser}!"
                raise ConfigError(txt) from e
            self[key] = parser.default

    def __setitem__(self, key: str, value: str):
        """Check whether value is registered and save it"""
        if key not in self.data:
            raise ConfigError(f"Invalid key '{key}'")
        # Parser
        if key in self._parsers:
            if not self.data[key].is_valid(value):
                raise ConfigError(f"Invalid value {value} for parser {key}")
            self._settings[key] = value
            return
        # Defined as options (no parser provided)
        index = -1
        # Find item with similar text representation
        with contextlib.suppress(ValueError):
            index = [str(item) for item in self.data[key]].index(value)
        if index == -1:
            raise ConfigError(f"Invalid value '{value}' for key '{key}'"
                              f"(also must be str)")
        # Use actual item, not given text representation
        self._settings[key] = self.data[key][index]

    def __getitem__(self, key):
        """Return value, if already set"""
        with contextlib.suppress(KeyError):
            return self._settings[key]
        raise ConfigError(f"No setting set for key {key}")

    def __bool__(self):
        """Check if all settings which class requires are already set"""
        return set(self._settings.keys()) == set(self.data.keys())

    def get_ini_dict(self):
        """Returns dictionary prepared to be inserted into standard
        ConfigParser. Dictionary has specific format for documentation and
        shouldn't be used for anything else"""
        ret = {}
        for key, value in self.data.items():
            # Parsers
            if key in self._parsers:
                if self.data[key].default != MISSING:
                    ret['#' + key] = ' # '.join(self.data[key].get_options())
                else:
                    ret[key] = ' # '.join(self.data[key].get_options())
                continue
            # Default options
            value = _map_to_strings(value)
            if key in self._defaults:
                ret['# ' + key] = ' # '.join(value)
            # Standard options
            else:
                ret[key] = ' # '.join(value)
        return ret


class TestScript:
    """Class representing current run of testscript"""
    class EventPriority(enum.IntEnum):
        LOW = 0
        HIGH = 10

    def __init__(self):
        self.modules: Iterable[Module] = collections.deque()
        self.event_stack: Deque[Event] = collections.deque()
        self.notifications: Deque[Event] = collections.deque()
        self.module_classes = []

    def register(self, module):
        """Call to register module to this object. All events will be sent to
        the module.handle_event function."""
        assert module not in self.modules, f"Module already registered"
        _logger.debug(f"Registering module {module.name} - "
                      f"{module.__class__.__name__}")
        self.modules.append(module)
        module.register(self)
        _logger.debug(f"Registered in {self.__class__}")

    def add_event(self, event, priority=EventPriority.LOW):
        """Adds event, wich will be processsed when run() function gets to
        it. Depending on priority, it might be last event in whole program"""
        event = get_valid_event(event)
        _logger.debug(f"{event.name}")
        if priority > TestScript.EventPriority.LOW:
            self.event_stack.append(event)
        else:  # This is only temporary solution, but who cares for now
            self.event_stack.appendleft(event)

    def add_notification(self, event: Event):
        """Notifications are events, which are not meant to trigger any other
        events.  In other words, logging info.  They take precedence over
        any other events that are in stack"""
        _logger.debug(f"{event.__repr__()}")
        self.notifications.append(event)

    def run(self):
        """Cycle which runs while there are still some events. This should be
        called only once per session"""
        _logger.debug(f"run called size {len(self.event_stack)}")
        while self.event_stack:
            event = self.event_stack.pop()
            _logger.debug(f"Event {event.name}")
            for module in self.modules:
                if module.handle_event(event):
                    _logger.debug(f"{event.name} handled by {module.name}")
                self._run_notifications()
        self._run_notifications()
        _logger.debug(f"run stopping size {len(self.event_stack)}")

    def _run_notifications(self):
        while self.notifications:
            event = self.notifications.pop()
            for module in self.modules:
                module.handle_event(event)

    def add_class(self, module_class):
        """Register class ass module. If module will be in config, it will be
        instantiated"""
        self.module_classes.append(module_class)

    def _add_module(self, unique_name, settings):
        module_name = None
        with contextlib.suppress(KeyError):
            module_name = settings[constants.CONFIG.MODULE]
        if not module_name:
            raise ConfigError(f"\n\tIn '{unique_name}' define module with "
                              f"'{constants.CONFIG.MODULE}'")
        module_class = self.find_module_by_name(module_name)
        module: Module = module_class(unique_name)

        # Fill module with settings
        for key, value in settings.items():
            if key == constants.CONFIG.MODULE:
                continue
            module.set(key, value)
        self.register(module)

    def load_ini_settings(self, open_file):
        """Given ini file open for reading, loads all modules in file and tries
        to set them up with given settings."""
        parser = configparser.ConfigParser(inline_comment_prefixes=['#'])
        parser.read_file(open_file)
        for module in parser.sections():
            module_settings = config_section_to_dict(parser, module)
            self._add_module(module, module_settings)

    def dump_ini_settings(self, open_file):
        """To OPEN_FILE, writes in ini format all modules, with all their
        settings. This creates something like example config. Current
        onfiguration doesn't have any effect on format of settings."""
        c = configparser.ConfigParser()
        temp_modules = [klass("fake name") for klass in self.module_classes]
        counter = 0
        for module in temp_modules:
            name = module.__class__.__name__
            counter += 1

            c.add_section(str(counter))
            for key, value in module.settings.get_ini_dict().items():
                c.set(str(counter), key, value)
            # Set also module name
            c.set(str(counter), constants.CONFIG.MODULE, name)
        open_file.write(constants.CONFIG.PROLOG)
        c.write(open_file)

    def find_module_by_name(self, name: str):
        """Given module name, returns class with same name if registered
        here"""
        modules = list(map(lambda x: x.__name__, self.module_classes))
        with contextlib.suppress(ValueError):
            return self.module_classes[modules.index(name)]
        # let's have nicer error
        raise ConfigError(f"No module named {name}")


class Module(abc.ABC):
    """Class serving as module for TestScript class. All other modules shall
    inherit from this class.

    Note: handle_event and register_event are tied together, so in case of
    overriding them, do neither or both"""
    # TODO: Explain settings

    SETTINGS: Dict[str, Any] = {
        'verbose': [True, False]
    }

    def __init__(self, name):
        self.name = name
        self.owner = None
        self.events: Deque[Tuple[re.Pattern, callable]] = collections.deque()
        self.settings = ModuleSettings()
        self.parse_settings_from_dict(self.SETTINGS)

    def register(self, parent_object: TestScript):
        """Registers parent, so module can send events to them"""
        assert not self.owner
        self.owner = parent_object

    def register_event(self, event, callback=None):
        """Given EVENT name, or wildcard string, or normal string, if
        matching event ever comes to handle_event, callback will be called,
        with event as its only argument. If you want to override this method,
        override also handle_event

        TODO: I'm wondering, maybe we could id classes with their memory
        addresses (id())"""
        event_name = _get_event_name(event)
        regex = build_wildcard_regex(event_name)

        if not callback:
            callback = self.handle_internal

        self.events.append((regex, callback))

    def send(self, event):
        """Send event to owner (testscripts), if any."""
        _logger.debug(f"Sending event {self.__class__} - {event.__repr__()}")
        if self.owner:
            self.owner.add_event(event)

    def notify(self, event):
        """Send event to owner. Event shall be Notifiaction or derived"""
        assert isinstance(event, Notification)
        if self.owner:
            self.owner.add_notification(event)

    def handle_event(self, event):
        """Given event, decides whether to process it or not. If event was
        registered via self.register_event, callback is called."""
        _logger.debug(f"{self.__class__.__name__} - event {event.name}")
        for regex, callback in self.events:
            if regex.fullmatch(event.name):
                _logger.debug(f"Event accepted {event.__repr__()}")
                ret = callback(event)
                if ret is not None:
                    return ret
                return True
        return False

    def register_setting(self,
                         key: str,
                         values: Iterable = None,
                         parser=None,
                         default=MISSING):
        """Register setting for this class. You must specify either values, or
        parser"""
        assert (values and not parser) or (not values and parser)
        if values:
            self.settings.add_options(key,
                                      list((values)),
                                      default=default)
        else:
            self.settings.add_parser(key, parser=parser)

    def set(self, key, value):
        """Set setting"""
        self.settings[key] = value

    def parse_settings_from_dict(self, settings: Dict[str, Any]):
        """Given settings in SETTINGS. Add them to this object via
        REGISTER_SETTING. """
        for key, value in settings.items():
            try:
                # If it's not iterable, it's parser
                iter(value)
                self.register_setting(key, values=value)
            except TypeError:
                self.register_setting(key, parser=value)

    @abc.abstractmethod
    def handle_internal(self, event):
        # This should be overridden
        return False


@enum.unique
class MessageSeverity(enum.IntEnum):
    CRITICAL = logging.CRITICAL
    ERROR = logging.ERROR
    WARNING = logging.WARNING
    INFO = logging.INFO
    DEBUG = logging.DEBUG


class ConsoleWriter(Module):
    SETTINGS = {'severity': [MessageSeverity.CRITICAL, MessageSeverity.INFO]}

    def __init__(self, name):
        super().__init__(name)
        self.register_event(Notification)

    def handle_internal(self, event):
        if event.severity == MessageSeverity.INFO:
            print(constants.KEYWORDS.OK + " " + event.message)
        elif event.severity == MessageSeverity.WARNING:
            print(constants.KEYWORDS.WARNING + " " + event.message)
        elif event.severity in [
                MessageSeverity.ERROR, MessageSeverity.CRITICAL
        ]:
            print(constants.KEYWORDS.ERROR + " " + event.message)
        else:
            print(event.message)
        return True
