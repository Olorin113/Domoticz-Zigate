## MODULE DevicesDomo

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

def UpdateDevice(Unit, nValue, sValue):
	# Make sure that the Domoticz device still exists (they can be deleted) before updating it 
	if (Unit in Devices):
		if (Devices[Unit].nValue != nValue) or (Devices[Unit].sValue != sValue):
			Devices[Unit].Update(nValue=nValue, sValue=str(sValue))
			Domoticz.Log("Update "+str(nValue)+":'"+str(sValue)+"' ("+Devices[Unit].Name+")")
	return	
	
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

def DomoUpdate(self,DeviceID,Ep,clusterID,value) :
	Domoticz.Debug("MajDomoDevice - Device ID : " + str(DeviceID) + " - Device EP : " + str(Ep) + " - Type : " + str(clusterID)  + " - Value : " + str(value) )
	x=0
	Type=TypeFromCluster(clusterID)
	for x in Devices:
		if Devices[x].DeviceID == str(DeviceID) :
			DOptions = Devices[x].Options
			Dtypename=DOptions['TypeName']
			if Type==Dtypename=="Temp" :  # temperature
				Update(x,0,str(value))				
			if Type==Dtypename=="Humi" :   # humidite
				Update(x,int(value),"0")				
			if Type==Dtypename=="Baro" :  # barometre
				CurrentnValue=Devices[x].nValue
				CurrentsValue=Devices[x].sValue
				Domoticz.Debug("MajDomoDevice baro CurrentsValue : " + CurrentsValue)
				SplitData=CurrentsValue.split(";")
				valueBaro='%s;%s' % (value,SplitData[0])
				Update(x,0,str(valueBaro))
			if Type=="Switch" and Dtypename=="Door" :  # porte / fenetre
				if value == "01" :
					state="Open"
				elif value == "00" :
					state="Closed"
				Update(x,int(value),str(state))
			if Type==Dtypename=="Switch" : # switch simple
				if value == "01" :
					state="On"
				elif value == "00" :
					state="Off"
				Update(x,int(value),str(state))
			if Type=="Switch" and Dtypename=="Water" : # detecteur d eau
				if value == "01" :
					state="On"
				elif value == "00" :
					state="Off"
				Update(x,int(value),str(state))
			if Type=="Switch" and Dtypename=="Smoke" : # detecteur de fume
				if value == "01" :
					state="On"
				elif value == "00" :
					state="Off"
				Update(x,int(value),str(state))
			if Type=="Switch" and Dtypename=="MSwitch" : # multi lvl switch
				if value == "01" :
					state="10"
				elif value == "02" :
					state="20"
				elif value == "03" :
					state="30"
				elif value == "04" :
					state="40"
				else :
					state="0"
				Update(x,int(value),str(state))
			if Type=="Switch" and Dtypename=="DSwitch" : # double switch avec EP different
				if Ep == "01" :
					if value == "01" :
						state="10"
						data="01"
				elif Ep == "02" :
					if value == "01" :
						state="20"
						data="02"
				elif Ep == "03" :
					if value == "01" :
						state="30"
						data="03"
				Update(x,int(data),str(state))
			if Type==Dtypename=="XCube" :  # cube xiaomi
				if Ep == "02" :
					if value == "0000" : #shake
						state="10"
						data="01"
					elif value == "0204" or value == "0200" or value == "0203" or value == "0201" or value == "0202" or value == "0205": #tap
						state="50"
						data="05"
					elif value == "0103" or value == "0100" or value == "0104" or value == "0101" or value == "0102" or value == "0105": #Slide
						state="20"
						data="02"
					elif value == "0003" : #Free Fall
						state="70"
						data="07"
					elif value >= "0004" and value <= "0059": #90°
						state="30"
						data="03"
					elif value >= "0060" : #180°
						state="90"
						data="09"
					Update(x,int(data),str(state))
			if Type==Dtypename=="Lux" :
				Update(x,0,str(value))
			if Type==Dtypename=="Motion" :
				if value == "01" :
					state="On"
				elif value == "00" :
					state="Off"
				Update(x,int(value),str(state))


def ResetDevice(Type,HbCount) :
	x=0
	for x in Devices: 
		try :
			LUpdate=Devices[x].LastUpdate
			LUpdate=time.mktime(time.strptime(LUpdate,"%Y-%m-%d %H:%M:%S"))
			current = time.time()
			DOptions = Devices[x].Options
			Dtypename=DOptions['TypeName']
			if (current-LUpdate)> 30 :
				if Dtypename=="Motion":
					value = "00"
					state="Off"
					#Devices[x].Update(nValue = int(value),sValue = str(state))
					Update(x,int(value),str(state))	
		except :
			return
			
def DeviceExist(self, Addr) :
	#check in ListOfDevices
	if Addr in self.ListOfDevices :
		return True
	else :  # devices inconnu ds listofdevices et ds db
		self.ListOfDevices[Addr]={}
		self.ListOfDevices[Addr]['Status']="004d"
		self.ListOfDevices[Addr]['Heartbeat']="0"
		self.ListOfDevices[Addr]['RIA']="0"
		self.ListOfDevices[Addr]['Battery']={}
		self.ListOfDevices[Addr]['Model']={}
		self.ListOfDevices[Addr]['Ep']={}
		self.ListOfDevices[Addr]['MacCapa']={}
		self.ListOfDevices[Addr]['IEEE']={}
		self.ListOfDevices[Addr]['Type']={}
		return False		
