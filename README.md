# lywsd03mmc-access

Access *Xiaomi Mi Temperature and Humidity Monitor 2* (*LYWSD03MMC*) device.


## Features

Some features of the project:
- reading current measurement,
- reading history data,
- storing history data to JSON,
- plotting history data.

Example of history chart:
![History chart](examples/example_history.png "Temperature and humidity chart")


## Device

*Xiaomi Mi Temperature and Humidity Monitor 2* is nice and cheap temperature and humidity sensor that allows to read 
measurements remotely through *Bluetooth*. Device has very useful feature related to remote read: it is 
able to store history of measurements.

Every history entry consists of: 
- entry index,
- entry timestamp,
- maximum and minimum tempreature,
- maximum and minimum humidity.

Min and max values are designated in the range on one hour, so history of two full days consists of 48 entries. 
Unfortunately it is impossible to change given range of one hour.


## Battery consumption

Manufacturer claims that it works up to one year on battery. It becomes clear that it does not involve BT connections.

#### Subscription

Following listing presents measurements log in *subscription* mode:

```
received data: 2025-09-19 18:49:33.882839 Temp: 22.95C Humidity: 63% Battery: 89%
received data: 2025-09-19 18:49:39.915296 Temp: 22.94C Humidity: 63% Battery: 89%
received data: 2025-09-19 18:49:45.945374 Temp: 22.94C Humidity: 63% Battery: 89%
...
received data: 2025-09-19 19:09:02.709446 Temp: 22.98C Humidity: 63% Battery: 84%
received data: 2025-09-19 19:09:08.739266 Temp: 23.01C Humidity: 63% Battery: 84%
``` 
Full log is accessible [here](examples/data_subscribe.txt).

There are 195 samples in time span of 19 minutes and 35 seconds. Time step between each sample is 6 seconds (unable 
to change). Battery drop is ~5%, so:
- battery consumption is ~15.3% / h,
- battery consumption is 0.026% per sample.

#### Polling

Following listing presents measurements log in polling mode:

```
[2025-09-19 01:11:57.829490] Temp: 25.16C Humidity: 58% Battery: 97%
[2025-09-19 01:32:07.809542] Temp: 23.61C Humidity: 61% Battery: 96%
[2025-09-19 01:52:15.276131] Temp: 23.36C Humidity: 62% Battery: 96%
...
[2025-09-19 14:39:02.402049] Temp: 22.88C Humidity: 62% Battery: 92%
[2025-09-19 14:59:13.925522] Temp: 22.91C Humidity: 62% Battery: 91%

``` 
Full log is accessible [here](examples/data_poll.txt).

There are 42 samples in time span of 13 hours, 47 minutes and 16 seconds. Time step between each sample is 20 minutes 
(can be any duration). Battery drop is ~6%, so:
- battery consumption is ~0.44% / h,
- battery consumption is 0.14% per sample.

It becomes clear that active polling consumes more energy than receiving notification. On other hand normally there is 
no need to measure temperature every 6 seconds. Active polling to be less efficient than notifications has to be 
performed with period shorter than **30 seconds**.


## Running the application

Application accepts following arguments:

<!-- insertstart include="doc/cmdargs.txt" pre="\n" post="\n" -->
```
usage: python3 -m lywsd03mmcaccess.main [-h] [-la] [--listtools]
                                        {info,readdata,readhistory,printhistory}
                                        ...

access Xiaomi Mi Temperature and Humidity Monitor 2 (LYWSD03MMC) device

options:
  -h, --help            show this help message and exit
  -la, --logall         Log all messages (default: False)
  --listtools           List tools (default: False)

subcommands:
  commands

  {info,readdata,readhistory,printhistory}
                        commands
    info                read device basic data
    readdata            read current measurement
    readhistory         read history
    printhistory        print history file
```



```
usage: python3 -m lywsd03mmcaccess.main info [-h] --mac MAC

read device basic data

options:
  -h, --help  show this help message and exit
  --mac MAC   MAC address of device (default: None)
```



```
usage: python3 -m lywsd03mmcaccess.main readdata [-h] --mac MAC

read current measurement

options:
  -h, --help  show this help message and exit
  --mac MAC   MAC address of device (default: None)
```



```
usage: python3 -m lywsd03mmcaccess.main readhistory [-h] --mac MAC
                                                    [--recent RECENT]
                                                    [--outappend OUTAPPEND]

read history

options:
  -h, --help            show this help message and exit
  --mac MAC             MAC address of device (default: None)
  --recent RECENT       Number of recent entries (default: None)
  --outappend OUTAPPEND
                        Path to output JSON file to append history data
                        (default: None)
```



```
usage: python3 -m lywsd03mmcaccess.main printhistory [-h] --histfile HISTFILE
                                                     [--recent RECENT]
                                                     [--noprint] [--showchart]
                                                     [--outchart OUTCHART]

print history file

options:
  -h, --help           show this help message and exit
  --histfile HISTFILE  Path to JSON file with history data (default: None)
  --recent RECENT      Number of recent entries (default: None)
  --noprint            Do not print raw data (default: False)
  --showchart          Show history chart (default: False)
  --outchart OUTCHART  Print history in form of chart (default: None)
```

<!-- insertend -->


## Installation

Installation of package can be done by:
 - to install package from downloaded ZIP file execute: `pip3 install --user -I file:lywsd03mmc-access-master.zip#subdirectory=src`
 - to install package directly from GitHub execute: `pip3 install --user -I git+https://github.com/anetczuk/lywsd03mmc-access.git#subdirectory=src`
 - uninstall: `pip3 uninstall lywsd03mmcaccess`

Installation for development:
 - `install-deps.sh` to install package dependencies only (`requirements.txt`)
 - `install-package.sh` to install package in standard way through `pip` (with dependencies)
 - `install-devel.sh` to install package in developer mode using `pip` (with dependencies)


## Development

All tests, linters and content generators can be executed by simple script `./process-all.sh`.

Unit tests are executed by `./src/testlywsd03mmcaccess/runtests.py`.

Code linters can be run by `./tools/checkall.sh`.

In case of pull requests please run `process-all.sh` before the request.


## References

- Python `struct` format string: https://docs.python.org/3/library/struct.html#format-strings


## License

```
BSD 3-Clause License

Copyright (c) 2025, Arkadiusz Netczuk <dev.arnet@gmail.com>

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
```
