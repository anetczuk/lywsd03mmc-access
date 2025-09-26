## <a name="main_help"></a> python3 -m lywsd03mmcaccess.main --help
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



## <a name="info_help"></a> python3 -m lywsd03mmcaccess.main info --help
```
usage: python3 -m lywsd03mmcaccess.main info [-h] --mac MAC

read device basic data

options:
  -h, --help  show this help message and exit
  --mac MAC   MAC address of device (default: None)
```



## <a name="readdata_help"></a> python3 -m lywsd03mmcaccess.main readdata --help
```
usage: python3 -m lywsd03mmcaccess.main readdata [-h] --mac MAC

read current measurement

options:
  -h, --help  show this help message and exit
  --mac MAC   MAC address of device (default: None)
```



## <a name="readhistory_help"></a> python3 -m lywsd03mmcaccess.main readhistory --help
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



## <a name="printhistory_help"></a> python3 -m lywsd03mmcaccess.main printhistory --help
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
