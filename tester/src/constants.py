"""Just constants for testscripts"""

import types
import colorama

colorama.init()

_CONFIG_TEXT = (f"# This is config file (ini format) for testscripts\n"
                f"# This file was generated from testcripts. It shows\n"
                f"# all available modules in testscripts. You can add one\n"
                f"# module multiple times, just ensure that you change\n"
                f"# section name to anything that is unique.\n"
                f"# If some setting has default value, it will be commented\n"
                f"# out and set to first value in list.\n"
                f"#######################################################\n"
                f"#######################################################\n"
                f"\n")

CONFIG = types.SimpleNamespace(
    MODULE="module",
    PROLOG=_CONFIG_TEXT,
    CONSOLE_LOG_FORMAT=
    "%(levelname)12s | %(name)18s | %(funcName)15s | %(message)s",
    HTML_HEADER="<html>\n<head>\n</head>\n<body>\n"
    '<div style="background-color: #494478;">\n',
    HTML_INFO='\t<h4 style="color: #00ff00;">\n\t\t{}\n\t</h4>\n'
    '<p><span style="color: white;">{}</span></p>\n',
    HTML_WARNING='\t<h4 style="color: #ff6600;">\n\t\t{}\n\t</h4>\n'
    '\t<p>\n\t\t<span style="color: white;">{}</span>\n\t</p>\n',
    HTML_ERROR='\t<h4 style="color: #ff0000;">\n\t\t{}\n\t</h4>\n'
    '\t<p>\n\t\t<span style="color: white;">{}</span>\n\t</p>\n',
    HTML_FOOTER="\n</div>\n</body>\n</html>",
)

KEYWORDS = types.SimpleNamespace(
    WARNING="[" + colorama.Fore.LIGHTYELLOW_EX + "WARNING" +
    colorama.Style.RESET_ALL + "]",
    OK="[" + colorama.Fore.LIGHTGREEN_EX + "OK" + colorama.Style.RESET_ALL +
    "]",
    ERROR="[" + colorama.Fore.LIGHTRED_EX + "ERROR" +
    colorama.Style.RESET_ALL + "]",
)
