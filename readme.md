# Installation

## Pre-request

- Domoticz 8.7 or upper. (11 jan 2018 : beta version)

  [Domoticz download](http://www.domoticz.com/downloads/) + [Visit domoticz web site for its installation](http://www.domoticz.com/wiki/Main_Page)

- [Module Zigate](zigate.fr) (of course! And don't forget to upload program in module at the first utilisation)

## Installation procedure for Zigate USB 

- After uploading program in zigate, plug it in usb port of your domoticz server.

- Create directory (your directory where domoticz is install)/plugin/**Zigate**/. (eg : /etc/domoticz/plugin/Zigate/, you could change the name)

- From Domoticz-Zigate github, download plugin.py to your directory (...)/domoticz/plugin/Zigate/**plugin.py** (don't change the name)

- Restart or start your Domoticz software

- In *Hardware*, create a new hard. Fill field below :
  - Type : Zigate USB plugin
  - Serial port : /dev/tty/USB**X** (X >= 0)
  - Mode Debug : yes (to see trace in log, after you may disable it)
  
- After click "Add", the module Zigate listen Zigbee devices for association during 5 minutes. Link your devices !

- Under domoticz, click on Setup->devices, then click on 'Not used'. Now you could see your associates devices, and switch it to "used" mode 
