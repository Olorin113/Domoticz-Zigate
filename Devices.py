
## MODULE Device

## Création Dictionnaire

Dict_Create{"Temp":{
	DeviceID=str(DeviceID),
	Name=str(t) + " - " + str(DeviceID),
	Unit=len(Devices)+1,
	TypeName="Temperature",
	Options={"Zigate":str(self.ListOfDevices[DeviceID]), "TypeName":t}
	}  # Detecteur temp
	 
Dict_Create{"Humi":{
	DeviceID=str(DeviceID),
	Name=str(t) + " - " + str(DeviceID),
	Unit=len(Devices)+1,
	TypeName="Humidity",
	Options={"Zigate":str(self.ListOfDevices[DeviceID]), "TypeName":t}
	}  # Detecteur hum
	
Dict_Create{"Baro":{
	DeviceID=str(DeviceID),
	Name=str(t) + " - " + str(DeviceID),
	Unit=len(Devices)+1,
	TypeName="Barometer",
	Options={"Zigate":str(self.ListOfDevices[DeviceID]), "TypeName":t}}
	}   # Detecteur Baro
		
Dict_Create{"Door":{
	DeviceID=str(DeviceID),
	Name=str(t) + " - " + str(DeviceID),
	Unit=len(Devices)+1,
	Type=244, Subtype=73, Switchtype=2 ,
	Options={"Zigate":str(self.ListOfDevices[DeviceID]), "TypeName":t}
	}   # capteur ouverture/fermeture xiaomi
	
Dict_Create{"Motion":{
	DeviceID=str(DeviceID),
	Name=str(t) + " - " + str(DeviceID),
	Unit=len(Devices)+1,
	Type=244, Subtype=73, Switchtype=8 ,
	Options={"Zigate":str(self.ListOfDevices[DeviceID]), "TypeName":t}
	}   # detecteur de presence
	
Dict_Create{"MSwitch":{
	DeviceID=str(DeviceID),
	Name=str(t) + " - " + str(DeviceID),
	Unit=len(Devices)+1,
	Type=244, Subtype=62, Switchtype=18,
	Options = {"LevelActions": "||||", "LevelNames": "Off|1 Click|2 Clicks|3 Clicks|4 Clicks", "LevelOffHidden": "true", "SelectorStyle": "0","Zigate":str(self.ListOfDevices[DeviceID]), "TypeName":t}
	}  # interrupteur multi lvl
	
	Dict_Create{"DSwitch":{
	DeviceID=str(DeviceID),
Name=str(t) + " - " + str(DeviceID),
	Unit=len(Devices)+1,
	Type=244, Subtype=62, Switchtype=18,
 	Options = {"LevelActions": "|||", "LevelNames": "Off|Left Click|Right Click|Both Click", "LevelOffHidden": "true", "SelectorStyle": "0","Zigate":str(self.ListOfDevices[DeviceID]), "TypeName":t}
	}   # interrupteur double sur EP different
	
Dict_Create{"Smoke":{
	DeviceID=str(DeviceID),
	Name=str(t) + " - " + str(DeviceID),
	Unit=len(Devices)+1,
	Type=244, Subtype=73, Switchtype=5,
	Options={"Zigate":str(self.ListOfDevices[DeviceID]), "TypeName":t}
	}   # detecteur de fumee
	
Dict_Create{"Lux":{
	DeviceID=str(DeviceID),
	Name=str(t) + " - " + str(DeviceID),
	Unit=len(Devices)+1,
	Type=246, Subtype=1, Switchtype=0,
	Options={"Zigate":str(self.ListOfDevices[DeviceID]),
	"TypeName":t}
	}    # Lux sensors
	
Dict_Create{"Switch":{
	DeviceID=str(DeviceID),
	Name=str(t) + " - " + str(DeviceID),
	Unit=len(Devices)+1,
	Type=244, Subtype=73, Switchtype=9,
	Options={"Zigate":str(self.ListOfDevices[DeviceID]),"TypeName":t}
	}   # inter sans fils 1 touche 86sw1 xiaomi
	
Dict_Create{"XCube":{
	DeviceID=str(DeviceID),
	Name=str(t) + " - " + str(DeviceID),
	Unit=len(Devices)+1,
	Type=244, Subtype=62, Switchtype=18,
 	Options = {"LevelActions": "||||||||", "LevelNames": "Off|Shake|Slide|90°|Clockwise|Tap|Move|Free Fall|Anti Clockwise|180°", "LevelOffHidden": "true", "SelectorStyle": "0","Zigate":str(self.ListOfDevices[DeviceID]), "TypeName":t}
	}   # Xiaomi Magic Cube
	
Dict_Create{"Water":{
	DeviceID=str(DeviceID),
	Name=str(t) + " - " + str(DeviceID),
	Unit=len(Devices)+1,
	Type=244, Subtype=73, Switchtype=0,
	Options={"Zigate":str(self.ListOfDevices[DeviceID]),"TypeName":t}
	}   # detecteur d'eau (v1) xiaomi
	
Dict_Create{"Smoke":{
	DeviceID=str(DeviceID),
	Name=str(t) + " - " + str(DeviceID),
	Unit=nbrdevices,
	Type=244, Subtype=73, Switchtype=5,
	Options={"Zigate":str(self.ListOfDevices[DeviceID]),"TypeName":t}
	}   # detecteur de fumee (v1) xiaomi

def Create(self, DeviceID) :
	#DeviceID=Addr #int(Addr,16)
	for Ep in self.ListOfDevices[DeviceID]['Ep'] :
		if self.ListOfDevices[DeviceID]['Type']== {} :
			Type=GetType(self, DeviceID, Ep).split("/")
		else :
			Type=self.ListOfDevices[DeviceID]['Type'].split("/")
		Domoticz.Debug("CreateDomoDevice - Device ID : " + str(DeviceID) + " Device EP : " + str(Ep) + " Type : " + str(Type) )
	
		if for t in Type :
			if t in Dict_Create:
				self.ListOfDevices[DeviceID]['Status']="inDB"
				
			Domoticz.Device(DeviceID=Dict_Create[t]["DeviceID"],
					Name=Dict_Create[t]["Name"],
					Unit=Dict_Create[t]["Unit"],
					TypeName=Dict_Create[t]["DeviceID"],
					Options=Dict_Create[t]["Options"]).Create()
			
		
