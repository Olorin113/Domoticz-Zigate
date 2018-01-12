# Domoticz-Zigate

## Description
-------------------

Zigate plugin for Domoticz.

zigate module web site : http://www.zigate.fr


## Installation
-------------------

### Pre-request

- a computer... (Raspberry, PC, MAC, other...)

- Domoticz version 8.71xx or upper started (and its pre-equest) 

- Zigate module with its program downloaded

### Configuration Zigate USB

1. After install Domoticz, create on your computer a directory for this plugin.

  (your domoticz path)/Plugin/**Zigate** (the name of directory could be other) 

2. And copy plugin.py in this directory (keep this name).

  (your domoticz path)/Plugin/**Zigate**/plugin.py (the name of directory could be other) 

3. Plug zigate module in USB port.

4.  Under Domoticz, create a new hardware
    1. fill fiels :
      - type : Zigate USB plugin
      - Serial port : /dev/ttyUSB**X** (under linux)
      - Mode debug : true (it's could be usefull to see if your devices are detected or not)

5. After create it, the module listen during 5 minutes all zigbee devices for pairing.

6. Paired your devices (you could see log to follow the pairing)

7. After zigate and your devices pairing, under domoticz, go to "devices" and click on "not used" to see all devices paired with you module zigate.

8. And click on green arrow to change state of the device from "not used" to "used".
