## <a name="main_help"></a> python3 -m lywsd03mmcaccess.main --help
```
usage: python3 -m lywsd03mmcaccess.main [-h] [-la] [--listtools]
                                        {readdata,readhistory} ...

access Xiaomi Mi Temperature and Humidity Monitor 2 (LYWSD03MMC) device

options:
  -h, --help            show this help message and exit
  -la, --logall         Log all messages (default: False)
  --listtools           List tools (default: False)

subcommands:
  commands

  {readdata,readhistory}
                        commands
    readdata            read current measurement
    readhistory         read history
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

read history

options:
  -h, --help       show this help message and exit
  --mac MAC        MAC address of device (default: None)
  --recent RECENT  Number of recent entries (default: None)
```
