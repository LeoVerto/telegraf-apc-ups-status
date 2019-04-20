#!/usr/bin/env python3

import sys
import re

from datetime import datetime

tags_map = {
    "UPSNAME": "ups_name", # UPS name from configuration file (dumb) or EEPROM (smart)
    "SERIALNO": "serial_no", # UPS serial number
}
fields_map = {
    "DATE": "time", # Date and time of last update from UPS
    "STATUS": "status", # UPS status (online, charging, on battery etc)
    "LINEV": "input_line_voltage", # Current input line voltage
    "LOADPCT": "load_capacity_used", # Percentage of UPS load capacity used as estimated by UPS
    "BCHARGE": "battery_capacity_charge", # Current battery capacity charge percentage
    "TIMELEFT": "runtime_left_minutes", # Remaining runtime left on battery as estimated by the UPS
    "OUTPUTV": "output_voltage", # Current UPS output voltage
    "ITEMP": "internal_temperature_celcius", # UPS internal temperature in degrees Celcius
    "BATTV": "battery_voltage", # Current battery voltage
    "LINEFREQ": "line_frequency_hz", # Current line frequency in Hertz
    "TONBATT": "time_on_battery_seconds", # Seconds currently on battery
}

influx_tags = {}
influx_fields = {}
timestamp = ""

kv_pattern = re.compile(r"([A-Z ]+):(.*)")
value_pattern = re.compile(r"[0-9.]*")

for line in sys.stdin:
    match = kv_pattern.match(line);
    if not match:
        continue

    key = match.group(1).strip()
    value = match.group(2).strip()

    if key == "DATE":
        time = datetime.strptime(value, "%Y-%m-%d %H:%M:%S %z")
        timestamp = int(time.timestamp())
        continue

    if key in tags_map:
        value = value.replace(",", "\,")
        value = value.replace(" ", "\ ")
        influx_tags[tags_map[key]] = value

    if key in fields_map:
        if key == "STATUS":
            value = "\"" + value.strip() + "\""
        else:
            value = value_pattern.search(value).group(0)

        influx_fields[fields_map[key]] = value


if timestamp:
    # Tags should be sorted by key before being sent for best performance of InfluxDB
    influx_tags = {k: influx_tags[k] for k in sorted(influx_tags)}

    line_protocol_tags = []
    for k, v in influx_tags.items():
        line_protocol_tags.append(k + "=" + v)

    line_protocol_fields = []
    for k, v in influx_fields.items():
        line_protocol_fields.append(k + "=" + v)

    print("ups_apc,{} {} {}000000000".format(
          ",".join(line_protocol_tags),
          ",".join(line_protocol_fields),
          timestamp)
    )
