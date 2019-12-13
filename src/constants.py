"""Just constants for testscripts"""
import types

_CONFIG_TEXT = (
    f"# This is config file (ini format) for testscripts\n"
    f"# This file was generated from testcripts. It shows\n"
    f"# all available modules in testscripts. You can add one\n"
    f"# module multiple times, just ensure that you change\n"
    f"# section name to anything that is unique.\n"
    f"# If some setting has default value, it will be commented\n"
    f"# out and set to first value in list.\n"
    f"#######################################################\n"
    f"#######################################################\n"
    f"\n"
)

CONFIG = types.SimpleNamespace(
    MODULE='module',
    PROLOG=_CONFIG_TEXT,
    CONSOLE_LOG_FORMAT='%(levelname)9s | %(name)10s | %(funcName)15s | %(message)s',
)
