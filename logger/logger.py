from datetime import datetime
# This file contains fuinctions that are useful for debugging
# The different functions are disabled based on the variables set below

INFO = True
WARN = True
DEBUG = False
ERROR = True

# This lets us print things to the console in different colours which makes it easier to spot error logs
# I don't fully understand this code, I stole it from:
# https://www.geeksforgeeks.org/python/print-colors-python-terminal/#printing-colored-text-in-python-using-ansi-escape-codes
def _print_red(s): 
    print("\033[91m {}\033[00m".format(s))

def _print_green(s): 
    print("\033[92m {}\033[00m".format(s))

def _print_yellow(s): 
    print("\033[93m {}\033[00m".format(s))

def _format_log(message, level):
    return f"[{datetime.now()}]:{level} - {message}"

def info(message):
    if not INFO:
        return
    
    log = _format_log(message, "info")
    print(log)

def warn(message):
    if not WARN:
        return
    
    log = _format_log(message, "error")
    _print_yellow(log)

def debug(message):
    if not DEBUG:
        return
    
    log = _format_log(message, "debug")
    _print_green(log)

def error(message):
    if not ERROR:
        return
    
    log = _format_log(message, "error")
    _print_red(log)