#
# Copyright (c) 2025, Arkadiusz Netczuk <dev.arnet@gmail.com>
# All rights reserved.
#
# This source code is licensed under the BSD 3-Clause license found in the
# LICENSE file in the root directory of this source tree.
#

# pylint: disable=W0212
# ruff: noqa: SLF001

import struct
import datetime
import logging
import contextlib

from lywsd03mmc import Lywsd03mmcClient
from lywsd02.client import UUID_DATA


_LOGGER = logging.getLogger(__name__)


class ThermometerAccess:

    def __init__(self, mac, access_timeout=25.0):
        self.client = Lywsd03mmcClient(mac=mac, notification_timeout=access_timeout)

    @contextlib.contextmanager
    def connect(self):
        with self.client.connect() as item:
            yield item

    ## { "temperature": float,
    ##   "humidity": int,
    ##   "battery": int
    ## }
    def get_current_measurements(self) -> dict:
        return self.client.data

    def get_history_measurements(self, recent_entries=None):
        if recent_entries is None:
            return self.client.history_data
        hist_index_data = self.get_last_and_next_history_index()
        hist_index = hist_index_data[0]
        start_index = hist_index - recent_entries
        if start_index < 1:
            return self.client.history_data
        self.set_first_history_index(start_index)
        _LOGGER.debug("getting recent %s entries", recent_entries)
        return self.client.history_data

    def get_last_history_entry(self):
        res = self.read_characteristic("ebe0ccbb-7a0a-4b0c-8a1a-6ff2997da3a6")
        data = struct.unpack_from("<IIhBhB", res)
        ts = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(seconds=data[1])
        return {
            "idx_num": data[0],
            "timestamp": ts,
            "temperature_row_max": data[2] / 10.0,
            "humidity_max": data[3],
            "temperature_row_min": data[4] / 10.0,
            "humidity_min": data[5],
        }

    ## returns (<recent-index>, <next-index>)
    def get_last_and_next_history_index(self):
        res = self.read_characteristic("ebe0ccb9-7a0a-4b0c-8a1a-6ff2997da3a6")
        return struct.unpack_from("II", res)

    def get_comfort_levels(self):
        res = self.read_characteristic("ebe0ccd7-7a0a-4b0c-8a1a-6ff2997da3a6")
        data = struct.unpack("HHBB", res)
        return {"temp_hi": data[0] / 100.0, "temp_lo": data[1] / 100.0, "hum_hi": data[2], "hum_low": data[3]}

    def get_first_history_index(self):
        res = self.read_characteristic("ebe0ccba-7a0a-4b0c-8a1a-6ff2997da3a6")
        data = struct.unpack_from("I", res)
        return data[0]

    ## works only for next history read (after the next read consecutive history reads will return full history)
    def set_first_history_index(self, history_index: int):
        data = struct.pack("I", history_index)
        self.write_characteristic("ebe0ccba-7a0a-4b0c-8a1a-6ff2997da3a6", data)

    def get_custom_measurements(self):
        res = self.read_characteristic("8edfffef-3d1b-9c37-4623-ad7265f14076")
        data = struct.unpack("<HBH", res)
        return {"temp1": data[0] / 100.0, "hum": data[1], "temp2": data[2] / 100.0}

    def get_custom_last_and_next_history_index(self):
        res = self.read_characteristic("8edffff1-3d1b-9c37-4623-ad7265f14076")
        return struct.unpack("II", res)

    def read_characteristic(self, uuid):
        _LOGGER.debug("reading character: %s", uuid)
        char_list = self.client._peripheral.getCharacteristics(uuid=uuid)
        ch = char_list[0]
        value = ch.read()
        _LOGGER.debug("got raw data: %s length: %s", value, len(value))
        return value

    def write_characteristic(self, uuid, value):
        _LOGGER.debug("writing character: %s %s", uuid, value)
        char_list = self.client._peripheral.getCharacteristics(uuid=uuid)
        ch = char_list[0]
        ch.write(value, withResponse=False)

    def listen_measurements(self):
        listener = ThermometerListener(self.client)
        listener.listen()


class ThermometerListener:

    def __init__(self, client: Lywsd03mmcClient):
        self.client: Lywsd03mmcClient = client

    ## drains battery a lot, ~10%/h
    ## or 0.025% per notification (every 6secs)
    ## direct read drains: 0.143% per read
    ## notifications are about 6 times more efficient than read, but are triggered in too often
    def listen(self):
        with self.client.connect():
            self.client._subscribe(UUID_DATA, self._notified_data)

            while True:
                if not self.client._peripheral.waitForNotifications(self.client._notification_timeout):
                    timeout = self.client._notification_timeout
                    _LOGGER.warning("No data from device for %s seconds", timeout)

    def _notified_data(self, data):
        self.client._process_sensor_data(data)
        recent = self.client._data
        curr_time = datetime.datetime.now(datetime.timezone.utc)
        message = pretty_measurement(recent)
        # ruff: noqa: T201
        print("received:", curr_time, message)


def pretty_measurement(data):
    return f"Temperature: {data.temperature}C Humidity: {data.humidity}% Battery: {data.battery}%"
