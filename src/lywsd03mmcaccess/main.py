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
import datetime

import matplotlib.pyplot as plt

from lywsd03mmcaccess import logger
from lywsd03mmcaccess.io import read_json, write_object
from lywsd03mmcaccess.thermometeraccess import ThermometerAccess, pretty_measurement, current_timezone


if __name__ == "__main__":
    _LOGGER = logging.getLogger("lywsd03mmcaccess.main")
else:
    _LOGGER = logging.getLogger(__name__)


# =======================================================================


def process_info(args):
    mac = args.mac
    device = ThermometerAccess(mac)
    with device.connect():
        dev_time = device.client.time
        print("time:", dev_time, dev_time[0].timestamp())
        print("start time:", device.client.start_time)
        print("tz offset:", device.client.tz_offset)
        print("measurement:", device.get_current_measurements())
        print("units:", device.client.units)
        print("comfort levels:", device.get_comfort_levels())
        print("recent history entry:", device.get_last_history_entry())
        print("history indexes:", device.get_last_and_next_history_index())
        print("history first index:", device.get_first_history_index())


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

    outfile = args.outappend

    device = ThermometerAccess(mac)
    if outfile is None:
        ## print history to screen
        with device.connect():
            data = device.get_history_measurements(recent_entries=recent)
            for key, item in data.items():
                # item[0] = item[0].strftime("%Y-%m-%d %H:%M:%S")
                print(f"Entry {key}: {item[0]} Tmin: {item[1]} Tmax: {item[3]} Hmin: {item[2]} Hmax: {item[4]}")
        return

    ## write history to file
    with device.connect():
        data_list = read_json(outfile)
        json_recent_timestamp = None
        json_recent_datetime = None
        if data_list is None:
            data_list = []
        else:
            recent_entry = data_list[-1]
            json_recent_timestamp = recent_entry["timestamp"]
            json_recent_datetime = datetime.datetime.fromtimestamp(json_recent_timestamp, tz=device.tzinfo)

        history_data = device.get_history_measurements(recent_timestamp=json_recent_timestamp)
        new_items = []
        for hist_item in history_data.values():
            hist_item_datetime = hist_item[0]
            item_timestamp = hist_item_datetime.timestamp()
            if json_recent_timestamp is not None:
                timestamp_diff_minutes = (item_timestamp - json_recent_timestamp) / 60
                if timestamp_diff_minutes <= 5.0:
                    ## skipping entry
                    _LOGGER.debug(
                        "skipping entry: %s[s] ts: %s recent json entry: %s",
                        timestamp_diff_minutes * 60,
                        hist_item_datetime,
                        json_recent_datetime,
                    )
                    continue
            entry = {
                "timestamp": item_timestamp,
                "Tmin": hist_item[1],
                "Tmax": hist_item[3],
                "Hmin": hist_item[2],
                "Hmax": hist_item[4],
            }
            new_items.append(entry)
        if not new_items:
            _LOGGER.info("no new history entries to append")
            return
        _LOGGER.info("writing history new %s items to file: %s", len(new_items), outfile)
        data_list.extend(new_items)
        write_object(data_list, outfile, indent=2)


def process_print_history(args):
    histfile = args.histfile
    data_list = read_json(histfile)
    if data_list is None:
        _LOGGER.error("unable to read history from path %s", histfile)
        return

    recent = args.recent
    if recent is not None:
        try:
            recent = int(recent)
        except ValueError:
            _LOGGER.warning("unable to convert '%s' to integer", args.recent)
            recent = None
    if recent:
        recent = min(recent, len(data_list))
        data_list = data_list[-recent:]

    noprint = args.noprint

    if not noprint:
        ## print data
        _LOGGER.info("printing raw data")
        print_raw(data_list)

    showchart = args.showchart
    outchart = args.outchart

    if not showchart and not outchart:
        return

    ## show plot
    _LOGGER.info("generating plot data")

    xpoints, ytemperature, ytemperature_diff, yhumidity, yhumidity_diff = prepare_plot_data(data_list)

    plt.subplot(4, 1, 1)
    plt.plot(xpoints, ytemperature)
    plt.title("Minimum and maximum temperature")
    # plt.ylabel('Temperature')
    plt.subplot(4, 1, 2)
    plt.plot(xpoints, ytemperature_diff)
    plt.title("Temperature difference")
    # plt.ylabel('Temperature')

    plt.subplot(4, 1, 3)
    plt.plot(xpoints, yhumidity)
    plt.title("Minimum and maximum humidity")
    # plt.ylabel('Humidity')
    plt.subplot(4, 1, 4)
    plt.plot(xpoints, yhumidity_diff)
    plt.title("Humidity difference")
    # plt.ylabel('Humidity')

    plt.tight_layout()

    if outchart:
        _LOGGER.info("storing plot to file '%s'", outchart)
        plt.savefig(outchart)

    if showchart:
        _LOGGER.info("opening plot window")
        plt.show()


def print_raw(data_list):
    curr_timezone = current_timezone()
    for index, item in enumerate(data_list):
        curr_timestamp = item["timestamp"]
        curr_time = datetime.datetime.fromtimestamp(curr_timestamp, tz=curr_timezone)
        print(
            f"""Entry {index}: {curr_time} Tmin: {item["Tmin"]} Tmax: {item["Tmax"]}""",
            f""" Hmin: {item["Hmin"]} Hmax: {item["Hmax"]}""",
        )


def prepare_plot_data(data_list):
    xpoints = []
    ytemperature = []
    ytemperature_diff = []
    yhumidity = []
    yhumidity_diff = []

    curr_timezone = current_timezone()
    for item in data_list:
        curr_timestamp = item["timestamp"]
        curr_time = datetime.datetime.fromtimestamp(curr_timestamp, tz=curr_timezone)

        xpoints.append(curr_time)
        temp_min = item["Tmin"]
        temp_max = item["Tmax"]
        ytemperature.append((temp_min, temp_max))
        ytemperature_diff.append(temp_max - temp_min)
        hum_min = item["Hmin"]
        hum_max = item["Hmax"]
        yhumidity.append((hum_min, hum_max))
        yhumidity_diff.append(hum_max - hum_min)

    return (xpoints, ytemperature, ytemperature_diff, yhumidity, yhumidity_diff)


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

    description = "read device basic data"
    subparser = subparsers.add_parser(
        "info",
        help=description,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    subparser.description = description
    subparser.set_defaults(func=process_info)
    subparser.add_argument("--mac", action="store", required=True, help="MAC address of device")

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
    subparser.add_argument(
        "--outappend",
        action="store",
        required=False,
        help="Path to output JSON file to append history data",
    )

    ## =================================================

    description = "print history file"
    subparser = subparsers.add_parser(
        "printhistory",
        help=description,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    subparser.description = description
    subparser.set_defaults(func=process_print_history)
    subparser.add_argument(
        "--histfile",
        action="store",
        required=True,
        help="Path to JSON file with history data",
    )
    subparser.add_argument("--recent", action="store", required=False, help="Number of recent entries")
    subparser.add_argument("--noprint", action="store_true", required=False, help="Do not print raw data")
    subparser.add_argument("--showchart", action="store_true", required=False, help="Show history chart")
    subparser.add_argument(
        "--outchart",
        action="store",
        required=False,
        help="Print history in form of chart",
    )

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
