#!/usr/bin/env python3
#
# Copyright (c) 2025, Arkadiusz Netczuk <dev.arnet@gmail.com>
# All rights reserved.
#
# This source code is licensed under the BSD 3-Clause license found in the
# LICENSE file in the root directory of this source tree.
#

import contextlib

with contextlib.suppress(ImportError):
    ## following import success only when file is directly executed from command line
    ## otherwise will throw exception when executing as parameter for "python -m"
    # pylint: disable=E0401,W0611
    # ruff: noqa: F401
    import __init__

    ## when import fails then it means that the script was executed indirectly
    ## in this case __init__ is already loaded

import sys
import argparse
import logging

from lywsd03mmcaccess.thermometeraccess import ThermometerAccess, pretty_measurement

from lywsd03mmcaccess import logger


if __name__ == "__main__":
    _LOGGER = logging.getLogger("lywsd03mmcaccess.main")
else:
    _LOGGER = logging.getLogger(__name__)


# =======================================================================


def process_read_data(args):
    mac = args.mac
    device = ThermometerAccess(mac)

    with device.connect():
        data = device.get_current_measurements()
        message = pretty_measurement(data)
        print("measurement:", message)


def process_read_history(args):
    mac = args.mac
    recent = args.recent
    if recent is not None:
        try:
            recent = int(recent)
        except ValueError:
            _LOGGER.warning("unable to convert '%s' to integer", args.recent)
            recent = None
    device = ThermometerAccess(mac)

    with device.connect():
        data = device.get_history_measurements(recent_entries=recent)
        for key, item in data.items():
            item[0] = item[0].strftime("%Y-%m-%d %H:%M:%S")
            print(f"Entry {key}: {item[0]} Tmin: {item[1]} Tmax: {item[3]} Hmin: {item[2]} Hmax: {item[4]}")


# =======================================================================


def main():
    parser = argparse.ArgumentParser(
        prog="python3 -m lywsd03mmcaccess.main",
        description="access Xiaomi Mi Temperature and Humidity Monitor 2 (LYWSD03MMC) device",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-la", "--logall", action="store_true", help="Log all messages")
    # have to be implemented as parameter instead of command (because access to 'subparsers' object)
    parser.add_argument("--listtools", action="store_true", help="List tools")
    parser.set_defaults(func=None)

    subparsers = parser.add_subparsers(help="commands", description="commands", dest="command", required=False)

    ## =================================================

    description = "read current measurement"
    subparser = subparsers.add_parser(
        "readdata",
        help=description,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    subparser.description = description
    subparser.set_defaults(func=process_read_data)
    subparser.add_argument("--mac", action="store", required=True, help="MAC address of device")

    ## =================================================

    description = "read history"
    subparser = subparsers.add_parser(
        "readhistory",
        help=description,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    subparser.description = description
    subparser.set_defaults(func=process_read_history)
    subparser.add_argument("--mac", action="store", required=True, help="MAC address of device")
    subparser.add_argument("--recent", action="store", required=False, help="Number of recent entries")
    # subparser.add_argument("--outdir", action="store", required=True, help="Path to output directory")

    ## =================================================

    args = parser.parse_args()

    if args.listtools is True:
        tools_list = list(subparsers.choices.keys())
        # ruff: noqa: T201
        print(", ".join(tools_list))
        return 0

    if args.logall is True:
        logger.configure(log_level=logging.DEBUG)
    else:
        logger.configure(log_level=logging.INFO)

    if "func" not in args or args.func is None:
        ## no command given -- print help message
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    code = main()
    sys.exit(code)
