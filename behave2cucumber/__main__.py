"""Main script."""

import getopt
import json
import logging
import sys
from pprint import pprint
from typing import TypedDict

from behave2cucumber import convert


class Options(TypedDict, total=False):
    short: str
    long: list[str]
    descriptions: list[str]
    shortlist: list[str]


# Global Parameters
_name = "behave2cucumber"
_debug = logging.WARNING

# Logging
log_formatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-10.10s]  %(message)s")
short_formatter = logging.Formatter("[%(levelname)-8.8s]  %(message)s")
log = logging.getLogger()
log.setLevel(_debug)
file_handler = logging.FileHandler("{0}/{1}.log".format("./", _name))
file_handler.setFormatter(log_formatter)
console_handler = logging.StreamHandler()
console_handler.setFormatter(short_formatter)
log.addHandler(file_handler)
log.addHandler(console_handler)


options: Options = {
    "short": "hd:i:o:rfD",
    "long": ["help", "debug=", "infile=", "outfile=", "remove-background", "format-duration", "deduplicate"],
    "descriptions": [
        "Print help message",
        "Set debug level",
        "Specify the input JSON",
        "Specify the output JSON, otherwise use stdout",
        "Remove background steps from output",
        "Format the duration",
        "Remove duplicate scenarios caused by @autoretry",
    ],
}


def usage() -> None:
    """Print out a usage message."""
    global options
    opt_len = len(options["long"])
    options["shortlist"] = [s for s in options["short"] if s != ":"]

    print("python -m behave2cucumber [-h] [-d level|--debug=level]")
    for i in range(opt_len):
        print("    -{0}|--{1:20} {2}".format(options["shortlist"][i], options["long"][i], options["descriptions"][i]))


print(options["short"], options["long"])
print(type(options["short"]), type(options["long"]))


def main(argv: list[str] = sys.argv[1:]) -> None:
    """Main."""
    global options

    opts = None
    try:
        print(options["short"], options["long"])
        print(type(options["short"]), type(options["long"]))
        opts, args = getopt.getopt(argv, options["short"], options["long"])
    except getopt.GetoptError:
        usage()
        exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            exit()
        elif opt in ("-d", "--debug"):
            try:
                arg_int = int(arg)
                log.debug(f"Debug level received: {arg}")
            except ValueError:
                log.warning(f"Invalid log level: {arg}")
                continue

            if 0 <= arg_int <= 5:
                log.setLevel(60 - (arg_int * 10))
                log.critical(f"Log level changed to: {logging.getLevelName(60 - (arg_int * 10))}")
            else:
                log.warning(f"Invalid log level: {arg}")

    infile = None
    outfile = None
    remove_background = False
    duration_format = False
    deduplicate = False

    for opt, arg in opts:
        if opt in ("-i", "--infile"):
            log.info("Input File: " + arg)
            infile = arg
        if opt in ("-o", "--outfile"):
            log.info("Output File: " + arg)
            outfile = arg
        if opt in ("-r", "--remove-background"):
            log.info("Remove Background: Enabled")
            remove_background = True
        if opt in ("-f", "--format-duration"):
            log.info("Format Duration: Enabled")
            duration_format = True
        if opt in ("-D", "--deduplicate"):
            log.info("Deduplicate: Enabled")
            deduplicate = True

    if infile is None:
        log.critical("No input JSON provided.")
        usage()
        exit(3)

    with open(infile) as f:
        cucumber_output = convert(
            json.load(f), remove_background=remove_background, duration_format=duration_format, deduplicate=deduplicate
        )

    if outfile is not None:
        with open(outfile, "w") as f:
            json.dump(cucumber_output, f, indent=4, separators=(",", ": "))
    else:
        pprint(cucumber_output)


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        sys.exit(0)
    except EOFError:
        sys.exit(0)
    # except:
    #     sys.exit(0)
