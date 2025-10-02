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
import pprint
import bluepy

import matplotlib.pyplot as plt

from lywsd03mmcaccess import logger
from lywsd03mmcaccess.io import read_json, write_object, read_list
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
        dev_time_data = device.client.time
        dev_time = dev_time_data[0]
        dev_tz_offset = dev_time_data[1]
        print("device time:           ", dev_time)
        print("device timestamp:      ", int(dev_time.timestamp()))
        print("device tz offset:      ", dev_tz_offset)
        print("client tz offset:      ", device.client.tz_offset)
        print("device start time:     ", device.start_time)   ## last bootup
        print("device current time:   ", device.get_device_current_time())   ## last bootup
        print("measurement:           ", device.get_current_measurements())
        print("units:                 ", device.client.units)
        print("comfort levels:        ", device.get_comfort_levels())
        
        recent_hist_entry = device.get_recent_history_entry()
        recent_hist_delta = datetime.timedelta(seconds=recent_hist_entry["timestamp"]) 
        recent_device_hist_date = datetime.datetime(1970, 1, 1) + recent_hist_delta
        recent_wall_hist_date = device.start_time + recent_hist_delta
        print("recent history entry:  ", recent_hist_entry) 
        print("entry device time:     ", recent_device_hist_date)
        print("entry time:            ", recent_wall_hist_date)

        history = device.get_history_measurements(recent_entries=3)
        print("recent history entries:")
        pprint.pprint(history, indent=2)

        print("history indexes:       ", device.get_last_and_next_history_index())
        print("history first index:   ", device.get_first_history_index())


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
            for item in data:
                index = item["index"]
                print(f"Entry {index}: {item}")
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
        for hist_item in history_data:
            item_timestamp = hist_item["timestamp"]
            item_datetime = hist_item["datetime"]
            hist_item_datetime = datetime.datetime.fromisoformat(item_datetime)
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
            new_items.append(hist_item)
            entry = dict(hist_item)
            _LOGGER.info("adding history entry: %s", entry)
        if not new_items:
            _LOGGER.info("no new history entries to append")
            return
        _LOGGER.info("writing history new %s items to file: %s", len(new_items), outfile)
        data_list.extend(new_items)
        write_object(data_list, outfile, indent=2)


def process_print_data(args):
    infile = args.infile
    data_list = read_json(infile)
    if data_list is None:
        _LOGGER.error("unable to read data from path %s", infile)
        return
    if not data_list:
        return

    recent = parse_int(args.recent)
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

    if "Tmin" in data_list[0]:
        plot_history(data_list)
    else:
        plot_measurements(data_list)

    if outchart:
        _LOGGER.info("storing plot to file '%s'", outchart)
        plt.savefig(outchart)

    if showchart:
        _LOGGER.info("opening plot window")
        plt.show()


def plot_history(data_list):
    xpoints = []
    ytemperature = []
    ytemperature_diff = []
    yhumidity = []
    yhumidity_diff = []

    for item in data_list:
        curr_datetime = item["datetime"]
        curr_time = datetime.datetime.fromisoformat(curr_datetime)

        xpoints.append(curr_time)
        temp_min = item["Tmin"]
        temp_max = item["Tmax"]
        ytemperature.append((temp_min, temp_max))
        ytemperature_diff.append(temp_max - temp_min)
        hum_min = item["Hmin"]
        hum_max = item["Hmax"]
        yhumidity.append((hum_min, hum_max))
        yhumidity_diff.append(hum_max - hum_min)

    axes = plt.subplot(4, 1, 1)
    plt.plot(xpoints, ytemperature)  # type: ignore[arg-type]
    plt.title("Minimum and maximum temperature")
    # plt.ylabel('Temperature')
    axes.minorticks_on()
    axes.grid()

    axes = plt.subplot(4, 1, 2)
    plt.plot(xpoints, ytemperature_diff)  # type: ignore[arg-type]
    plt.title("Temperature difference")
    # plt.ylabel('Temperature')
    axes.minorticks_on()
    axes.grid()

    axes = plt.subplot(4, 1, 3)
    plt.plot(xpoints, yhumidity)  # type: ignore[arg-type]
    plt.title("Minimum and maximum humidity")
    # plt.ylabel('Humidity')
    axes.minorticks_on()
    axes.grid()

    axes = plt.subplot(4, 1, 4)
    plt.plot(xpoints, yhumidity_diff)  # type: ignore[arg-type]
    plt.title("Humidity difference")
    # plt.ylabel('Humidity')
    axes.minorticks_on()
    axes.grid()

    plt.tight_layout()


def plot_measurements(data_list):
    xpoints = []
    ytemperature = []
    yhumidity = []
    ybattery = []

    curr_timezone = current_timezone()
    start_time = None
    for item in data_list:
        curr_timestamp = item["timestamp"]
        curr_time = datetime.datetime.fromtimestamp(curr_timestamp, tz=curr_timezone)

        if start_time is None:
            start_time = curr_time
        time_diff = curr_time - start_time
        delta = time_diff.total_seconds()

        xpoints.append(delta)
        temp = item["T"]
        ytemperature.append(temp)
        hum = item["H"]
        yhumidity.append(hum)
        batt = item["B"]
        ybattery.append(batt)

    def format_deltatime(value, _pos=None):
        delta = datetime.timedelta(seconds=value)
        return f"{delta}"

    axes = plt.subplot(3, 1, 1)
    plt.plot(xpoints, ytemperature, marker=".")
    plt.title("Temperature")
    axes.xaxis.set_major_formatter(format_deltatime)
    axes.minorticks_on()
    axes.grid()

    axes = plt.subplot(3, 1, 2)
    plt.plot(xpoints, yhumidity, marker=".")
    plt.title("Humidity")
    axes.xaxis.set_major_formatter(format_deltatime)
    axes.minorticks_on()
    axes.grid()

    axes = plt.subplot(3, 1, 3)
    plt.plot(xpoints, ybattery, marker=".")
    plt.title("Battery")
    axes.xaxis.set_major_formatter(format_deltatime)
    axes.minorticks_on()
    axes.grid()

    plt.tight_layout()


def print_raw(data_list):
    curr_timezone = current_timezone()
    for index, item in enumerate(data_list):
        if "Tmin" in item:
            curr_timestamp = item["timestamp"]
            curr_datetime = item["datetime"]
            curr_time = datetime.datetime.fromisoformat(curr_datetime)
            print(
                f"""Entry {index}: {curr_timestamp} {curr_time} Tmin: {item["Tmin"]} Tmax: {item["Tmax"]}""",
                f""" Hmin: {item["Hmin"]} Hmax: {item["Hmax"]}""",
            )
        else:
            curr_timestamp = item["timestamp"]
            curr_time = datetime.datetime.fromtimestamp(curr_timestamp, tz=curr_timezone)
            print(
                f"""Entry {index}: {curr_time} T: {item["T"]} H: {item["H"]} B: {item["B"]}""",
            )


def process_convert_measurements(args):
    input_file = args.infile
    output_file = args.outfile
    no_print = args.noprint

    data_list = read_list(input_file)

    hour_offset = 0
    recent_date_data = None
    out_list = []
    for item in data_list:
        item_elements = item.split(" ")

        date_content = item_elements[0]
        date_content = date_content[1:-1]
        temp_content = item_elements[3]
        hum_content = item_elements[5]
        batt_content = item_elements[7]

        converted_date = convert_to_datetime(date_content)
        date_data = converted_date + datetime.timedelta(hours=hour_offset)
        if recent_date_data is not None and recent_date_data > date_data:
            hour_offset += 24
            date_data = converted_date + datetime.timedelta(hours=hour_offset)
        recent_date_data = date_data

        temp_data = float(temp_content[:-1])
        hum_data = int(hum_content[:-1])
        batt_data = int(batt_content[:-1])

        data_dict = {"timestamp": date_data.timestamp(), "T": temp_data, "H": hum_data, "B": batt_data}
        out_list.append(data_dict)

    if not no_print:
        # ruff: noqa: T203
        pprint.pprint(out_list)

    if output_file:
        _LOGGER.info("writing to file: %s", output_file)
        write_object(out_list, output_file, indent=2)


def convert_to_datetime(date_string):
    ## format codes: https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes

    ## example: [23:03:52.888767] measurement: Temperature: 23.25C Humidity: 61% Battery: 77%
    ret_date = datetime.datetime.strptime(date_string, "%H:%M:%S.%f")
    time_obj = ret_date.time()
    date_obj = datetime.date.today()
    return datetime.datetime.combine(date_obj, time_obj)


# =======================================================================


def prepare_parser():
    parser = argparse.ArgumentParser(
        prog="python3 -m lywsd03mmcaccess.main",
        description="access Xiaomi Mi Temperature and Humidity Monitor 2 (LYWSD03MMC) device",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-la", "--logall", action="store_true", help="Log all messages")
    parser.add_argument("-nl", "--nolog", action="store_true", help="No diagnostics log messages")
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

    description = "print data file (history or measurements)"
    subparser = subparsers.add_parser(
        "printhistory",
        help=description,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    subparser.description = description
    subparser.set_defaults(func=process_print_data)
    subparser.add_argument(
        "--infile",
        action="store",
        required=True,
        help="Path to JSON file with data",
    )
    subparser.add_argument("--recent", action="store", required=False, help="Number of recent entries")
    subparser.add_argument("--noprint", action="store_true", required=False, help="Do not print raw data")
    subparser.add_argument("--showchart", action="store_true", required=False, help="Show data chart")
    subparser.add_argument(
        "--outchart",
        action="store",
        required=False,
        help="Print data in form of chart",
    )

    ## =================================================

    description = "convert measurements list to JSON"
    subparser = subparsers.add_parser(
        "convertmeasurements",
        help=description,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    subparser.description = description
    subparser.set_defaults(func=process_convert_measurements)
    subparser.add_argument(
        "--infile",
        action="store",
        required=True,
        help="Path to measurements file",
    )
    subparser.add_argument(
        "--outfile",
        action="store",
        required=False,
        help="Path to output JSON",
    )
    subparser.add_argument("--noprint", action="store_true", required=False, help="Do not print raw data")

    return parser, subparsers


def parse_int(input_value):
    if input_value is None:
        return None
    try:
        return int(input_value)
    except ValueError:
        _LOGGER.warning("unable to convert '%s' to integer", input_value)
    return None


def main():
    parser, subparsers = prepare_parser()

    args = parser.parse_args()

    if args.listtools is True:
        tools_list = list(subparsers.choices.keys())
        # ruff: noqa: T201
        print(", ".join(tools_list))
        return 0

    if args.nolog is True:
        logger.configure(log_level=logging.CRITICAL)
    elif args.logall is True:
        logger.configure(log_level=logging.DEBUG)
    else:
        logger.configure(log_level=logging.INFO)

    if "func" not in args or args.func is None:
        ## no command given -- print help message
        parser.print_help()
        return 1

    try:
        return args.func(args)
    except bluepy.btle.BTLEDisconnectError as exc:
        _LOGGER.error("unable to connect, reason: %s", exc)
        return 1


if __name__ == "__main__":
    code = main()
    sys.exit(code)
