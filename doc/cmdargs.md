## <a name="main_help"></a> python3 -m lywsd03mmcaccess.main --help
```
usage: python3 -m lywsd03mmcaccess.main [-h] [-la] [-nl] [--listtools]
                                        {info,readdata,readhistory,printhistory,convertmeasurements}
                                        ...

access Xiaomi Mi Temperature and Humidity Monitor 2 (LYWSD03MMC) device

options:
  -h, --help            show this help message and exit
  -la, --logall         Log all messages (default: False)
  -nl, --nolog          No diagnostics log messages (default: False)
  --listtools           List tools (default: False)

subcommands:
  commands

  {info,readdata,readhistory,printhistory,convertmeasurements}
                        commands
    info                read device basic data
    readdata            read current measurement
    readhistory         read history
    printhistory        print data file (history or measurements)
    convertmeasurements
                        convert measurements list to JSON
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
usage: python3 -m lywsd03mmcaccess.main printhistory [-h] --infile INFILE
                                                     [--recent RECENT]
                                                     [--noprint] [--showchart]
                                                     [--outchart OUTCHART]

print data file (history or measurements)

options:
  -h, --help           show this help message and exit
  --infile INFILE      Path to JSON file with data (default: None)
  --recent RECENT      Number of recent entries (default: None)
  --noprint            Do not print raw data (default: False)
  --showchart          Show data chart (default: False)
  --outchart OUTCHART  Print data in form of chart (default: None)
```



## <a name="convertmeasurements_help"></a> python3 -m lywsd03mmcaccess.main convertmeasurements --help
```
usage: python3 -m lywsd03mmcaccess.main convertmeasurements
       [-h] --infile INFILE [--outfile OUTFILE] [--noprint]

convert measurements list to JSON

options:
  -h, --help         show this help message and exit
  --infile INFILE    Path to measurements file (default: None)
  --outfile OUTFILE  Path to output JSON (default: None)
  --noprint          Do not print raw data (default: False)
```
