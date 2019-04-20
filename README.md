# Python APC UPS data collector for telegraf
This is a port of this PHP script by Walter Nasich: https://bitbucket.org/snippets/wnasich/7Kg89/

## Usage
Create `/usr/local/sbin/apc_collector.sh` with the following content:
 
    #!/bin/bash
    apcaccess | python3 /path/to/apc2telegraf.py

Make it executable:
    
    $ chmod a+x /usr/local/sbin/apc_collector.sh
 
Edit your telegraf.conf, add an 'exec' input:

    [[inputs.exec]]
       commands = ["/usr/local/bin/apc_collector.sh"]
       data_format = "influx"

Restart telegraf. Data will be collected under the measurement 'ups_apc'.

## Collecting UPS events

If you want to collect UPS events:
* Add this to /etc/rc.local:
  `$ touch /tmp/upsapcevents.log`

* Add to /etc/apcupsd/apccontrol at line 32 the line below:

      echo "ups_apc_event,ups_name=$1 status=\"$2\" `date +%s%N`" >> /tmp/upsapcevents.log

* Enable inputs.tail at /etc/telegraf/telegraf.conf
  Spec next settings:
  
      files = ["/tmp/upsapcevents.log"]
      from_beginning = false
      data_format = "influx"
