# Zigate Python Plugin
#
# Author: zaraki673
#

"""
<plugin key="Zigate" name="Zigate plugin" author="zaraki673" version="1.2.0" wikilink="http://www.domoticz.com/wiki/plugins/zigate.html" externallink="https://www.zigate.fr/">
	<params>
		<param field="Mode1" label="Type" width="75px">
			<options>
				<option label="USB" value="USB" default="true" />
				<option label="Wifi" value="Wifi"/>
			</options>
		</param>
		<param field="Address" label="IP" width="150px" required="true" default="0.0.0.0"/>
		<param field="Port" label="Port" width="150px" required="true" default="9999"/>
		<param field="SerialPort" label="Serial Port" width="150px" required="true" default="/dev/ttyUSB0"/>
		<param field="Mode2" label="Duree association (entre 0 et 255) au demarrage : " width="75px" required="true" default="254" />
		<param field="Mode3" label="Erase Persistent Data ( !!! réassociation de tous les devices obligatoirs !!! ): " width="75px">
			<options>
				<option label="True" value="True"/>
				<option label="False" value="False"  default="true" />
			</options>
		</param>
		<param field="Mode6" label="Debug" width="75px">
			<options>
				<option label="True" value="Debug"/>
				<option label="False" value="Normal"  default="true" />
			</options>
		</param>
	</params>
</plugin>
"""

import Domoticz
import binascii
import time
import Zigate
import DevicesDomo

##---
## Initialisation du dictionnaire TypeFromCluster

for num in range(0x0,0x10000):
	TypeFromCluster={str(hex(num))[2:6]:""} # 		
TypeFromCluster={"0405":"Humi"}
TypeFromCluster={"0406":"Motion"}
TypeFromCluster={"0400":"Lux"}
TypeFromCluster={"0403":"Baro"}
TypeFromCluster={"0402":"Temp"}
TypeFromCluster={"0006":"Switch"}
TypeFromCluster={"0500":"Door"}
TypeFromCluster={"0012":"XCube"}
TypeFromCluster={"000c":"XCube"}


class BasePlugin:
	enabled = False

	def __init__(self):
		self.ListOfDevices = {}  # {DevicesAddresse : { status : status_de_detection, data : {ep list ou autres en fonctions du status}}, DevicesAddresse : ...}
		return

	def onStart(self):
		Domoticz.Log("onStart called")
		global ReqRcv
		global ZigateConn
		if Parameters["Mode6"] == "Debug":
			Domoticz.Debugging(1)
			DumpConfigToLog()
			#Domoticz.Log("Debugger started, use 'telnet 0.0.0.0 4444' to connect")
			#import rpdb
			#rpdb.set_trace()
		if Parameters["Mode1"] == "USB":
			ZigateConn = Domoticz.Connection(Name="ZiGate", Transport="Serial", Protocol="None", Address=Parameters["SerialPort"], Baud=115200)
			ZigateConn.Connect()
		if Parameters["Mode1"] == "Wifi":
			ZigateConn = Domoticz.Connection(Name="Zigate", Transport="TCP/IP", Protocol="None ", Address=Parameters["Address"], Port=Parameters["Port"])
			ZigateConn.Connect()
		ReqRcv=''
		for x in Devices : # initialise listeofdevices avec les devices en bases domoticz
			ID = Devices[x].DeviceID
			self.ListOfDevices[ID]={}
			self.ListOfDevices[ID]=eval(Devices[x].Options['Zigate'])
		
		#Import DeviceConf.txt
		with open(Parameters["HomeFolder"]+"DeviceConf.txt", 'r') as myfile:
			tmpread=myfile.read().replace('\n', '')
			self.DeviceConf=eval(tmpread)
			Domoticz.Debug("DeviceConf.txt = " + str(self.DeviceConf))
		#Import DeviceList.txt
		with open(Parameters["HomeFolder"]+"DeviceList.txt", 'r') as myfile2:
			tmpread2=myfile2.read().replace('\n', '')
			self.DeviceList=eval(tmpread2)
			Domoticz.Debug("DeviceList.txt = " + str(eval(tmpread2)))
			
	def onStop(self):
		Domoticz.Log("onStop called")

	def onConnect(self, Connection, Status, Description):
		Domoticz.Log("onConnect called")
		global isConnected
		if (Status == 0):
			isConnected = True
			Domoticz.Log("Connected successfully")
			if Parameters["Mode3"] == "True":
			################### ZiGate - ErasePD ##################
				sendZigateCmd("0012","0000", "")
			ZigateConf()
		else:
			Domoticz.Log("Failed to connect ("+str(Status)+")")
			Domoticz.Debug("Failed to connect ("+str(Status)+") with error: "+Description)
		return True

	def onMessage(self, Connection, Data):
		Domoticz.Log("onMessage called")
		global Tmprcv
		global ReqRcv
		Tmprcv=binascii.hexlify(Data).decode('utf-8')
		if Tmprcv.find('03') != -1 and len(ReqRcv+Tmprcv[:Tmprcv.find('03')+2])%2==0 :### fin de messages detecter dans Data
			ReqRcv+=Tmprcv[:Tmprcv.find('03')+2] #
			#try :
			if ReqRcv.find("0301") == -1 : #verifie si pas deux messages coller ensemble
				ZigateDecode(self, ReqRcv) #demande de decodage de la trame recu
				ReqRcv=Tmprcv[Tmprcv.find('03')+2:]  # traite la suite du tampon
			else : 
				ZigateDecode(self, ReqRcv[:ReqRcv.find("0301")+2])
				ZigateDecode(self, ReqRcv[ReqRcv.find("0301")+2:])
				ReqRcv=Tmprcv[Tmprcv.find('03')+2:]
			#except :
			#	Domoticz.Debug("onMessage - effacement de la trame suite a une erreur de decodage : " + ReqRcv)
			#	ReqRcv = Tmprcv[Tmprcv.find('03')+2:]  # efface le tampon en cas d erreur
		else : # while end of data is receive
			ReqRcv+=Tmprcv
		return

	def onCommand(self, Unit, Command, Level, Hue):
		Domoticz.Log("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))

	def onDisconnect(self, Connection):
		with open(Parameters["HomeFolder"]+"DeviceList.txt", 'w') as myfile2:
			myfile2.write(self.ListOfDevices)
			Domoticz.Debug("Write DeviceList.txt = " + str(self.ListOfDevices))
		Domoticz.Log("onDisconnect called")

	def onHeartbeat(self):
		#Domoticz.Log("onHeartbeat called")
		Domoticz.Debug("ListOfDevices : " + str(self.ListOfDevices))
		for key in self.ListOfDevices :
			status=self.ListOfDevices[key]['Status']
			RIA=int(self.ListOfDevices[key]['RIA'])
			self.ListOfDevices[key]['Heartbeat']=str(int(self.ListOfDevices[key]['Heartbeat'])+1)
			# Envoi une demande Active Endpoint request
			if status=="004d" and self.ListOfDevices[key]['Heartbeat']=="1":
				sendZigateCmd("0045","0002", str(key))
				self.ListOfDevices[key]['Status']="0045"
				self.ListOfDevices[key]['Heartbeat']="0"
			if status=="004d" and self.ListOfDevices[key]['Heartbeat']>="10":
				self.ListOfDevices[key]['Heartbeat']="0"
			if status=="0045" and self.ListOfDevices[key]['Heartbeat']>="10":
				self.ListOfDevices[key]['Heartbeat']="0"
				self.ListOfDevices[key]['Status']="004d"
			# Envoie une demande Simple Descriptor request par EP
			if status=="8045" and self.ListOfDevices[key]['Heartbeat']=="1":
				for cle in self.ListOfDevices[key]['Ep']:
					Domoticz.Debug("Envoie une demande Simple Descriptor request pour avoir les informations du EP :" + cle + ", du device adresse : " + key)
					sendZigateCmd("0043","0004", str(key)+str(cle))
				self.ListOfDevices[key]['Status']="0043"
				self.ListOfDevices[key]['Heartbeat']="0"
			if status=="8045" and self.ListOfDevices[key]['Heartbeat']>="10":
				self.ListOfDevices[key]['Heartbeat']="0"
			if status=="0043" and self.ListOfDevices[key]['Heartbeat']>="10":
				self.ListOfDevices[key]['Heartbeat']="0"
				self.ListOfDevices[key]['Status']="8045"
		
			if (RIA>=10 or self.ListOfDevices[key]['Model']!= {}) and status != "inDB" :
				#creer le device ds domoticz en se basant sur les clusterID ou le Model si il est connu
				IsCreated=False
				x=0
				nbrdevices=0
				for x in Devices:
					if Devices[x].DeviceID == str(key) :
						IsCreated = True
						Domoticz.Debug("HearBeat - Devices already exist. Unit=" + str(x))
				if IsCreated == False :
					Domoticz.Debug("HearBeat - creating device id : " + str(key))
					DevicesDomo.Create(self, key)


		ResetDevice("Motion",5)


		if (ZigateConn.Connected() != True):
			ZigateConn.Connect()
		return True


global _plugin
_plugin = BasePlugin()

def onStart():
	global _plugin
	_plugin.onStart()

def onStop():
	global _plugin
	_plugin.onStop()

def onConnect(Connection, Status, Description):
	global _plugin
	_plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
	global _plugin
	_plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
	global _plugin
	_plugin.onCommand(Unit, Command, Level, Hue)

def onDisconnect(Connection):
	global _plugin
	_plugin.onDisconnect(Connection)

def onHeartbeat():
	global _plugin
	_plugin.onHeartbeat()

	# Generic helper functions
def DumpConfigToLog():
	for x in Parameters:
		if Parameters[x] != "":
			Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
	Domoticz.Debug("Device count: " + str(len(Devices)))
	for x in Devices:
		Domoticz.Debug("Device:		   " + str(x) + " - " + str(Devices[x]))
		Domoticz.Debug("Device ID:	   '" + str(Devices[x].ID) + "'")
		Domoticz.Debug("Device Name:	 '" + Devices[x].Name + "'")
		Domoticz.Debug("Device nValue:	" + str(Devices[x].nValue))
		Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
		Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
		Domoticz.Debug("Device options: " + str(Devices[x].Options))
	return	

def MajDomoDevice(self,DeviceID,Ep,clusterID,value) :
	Domoticz.Debug("MajDomoDevice - Device ID : " + str(DeviceID) + " - Device EP : " + str(Ep) + " - Type : " + str(clusterID)  + " - Value : " + str(value) )
	x=0
	Type=TypeFromCluster(clusterID)
	for x in Devices:
		if Devices[x].DeviceID == str(DeviceID) :
			DOptions = Devices[x].Options
			Dtypename=DOptions['TypeName']
			if Type==Dtypename=="Temp" :  # temperature
				UpdateDevice(x,0,str(value))				
			if Type==Dtypename=="Humi" :   # humidite
				UpdateDevice(x,int(value),"0")				
			if Type==Dtypename=="Baro" :  # barometre
				CurrentnValue=Devices[x].nValue
				CurrentsValue=Devices[x].sValue
				Domoticz.Debug("MajDomoDevice baro CurrentsValue : " + CurrentsValue)
				SplitData=CurrentsValue.split(";")
				valueBaro='%s;%s' % (value,SplitData[0])
				UpdateDevice(x,0,str(valueBaro))
			if Type=="Switch" and Dtypename=="Door" :  # porte / fenetre
				if value == "01" :
					state="Open"
				elif value == "00" :
					state="Closed"
				UpdateDevice(x,int(value),str(state))
			if Type==Dtypename=="Switch" : # switch simple
				if value == "01" :
					state="On"
				elif value == "00" :
					state="Off"
				UpdateDevice(x,int(value),str(state))
			if Type=="Switch" and Dtypename=="Water" : # detecteur d eau
				if value == "01" :
					state="On"
				elif value == "00" :
					state="Off"
				UpdateDevice(x,int(value),str(state))
			if Type=="Switch" and Dtypename=="Smoke" : # detecteur de fume
				if value == "01" :
					state="On"
				elif value == "00" :
					state="Off"
				UpdateDevice(x,int(value),str(state))
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
				UpdateDevice(x,int(value),str(state))
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
				UpdateDevice(x,int(data),str(state))
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
					UpdateDevice(x,int(data),str(state))
			if Type==Dtypename=="Lux" :
				UpdateDevice(x,0,str(value))
			if Type==Dtypename=="Motion" :
				if value == "01" :
					state="On"
				elif value == "00" :
					state="Off"
				UpdateDevice(x,int(value),str(state))


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
					UpdateDevice(x,int(value),str(state))	
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

def getChecksum(msgtype,length,datas) :
	temp = 0 ^ int(msgtype[0:2],16) 
	temp ^= int(msgtype[2:4],16) 
	temp ^= int(length[0:2],16) 
	temp ^= int(length[2:4],16)
	for i in range(0,len(datas),2) :
		temp ^= int(datas[i:i+2],16)
		chk=hex(temp)
	Domoticz.Debug("getChecksum - Checksum : " + str(chk))
	return chk[2:4]


def UpdateBattery(DeviceID,BatteryLvl):
	x=0
	found=False
	for x in Devices:
		if Devices[x].DeviceID == str(DeviceID):
			found==True
			Domoticz.Log("Devices exist in DB. Unit=" + str(x))
			CurrentnValue=Devices[x].nValue
			Domoticz.Log("CurrentnValue = " + str(CurrentnValue))
			CurrentsValue=Devices[x].sValue
			Domoticz.Log("CurrentsValue = " + str(CurrentsValue))
			Domoticz.Log("BatteryLvl = " + str(BatteryLvl))
			Devices[x].Update(nValue = int(CurrentnValue),sValue = str(CurrentsValue), BatteryLevel = BatteryLvl )
	if found==False :
		self.ListOfDevices[DeviceID]['Status']="004d"
		self.ListOfDevices[DeviceID]['Battery']=BatteryLvl
		
		
	#####################################################################################################################

def UpdateDevice(Unit, nValue, sValue):
	# Make sure that the Domoticz device still exists (they can be deleted) before updating it 
	if (Unit in Devices):
		if (Devices[Unit].nValue != nValue) or (Devices[Unit].sValue != sValue):
			Devices[Unit].Update(nValue=nValue, sValue=str(sValue))
			Domoticz.Log("Update "+str(nValue)+":'"+str(sValue)+"' ("+Devices[Unit].Name+")")
	return		

def ReadCluster(self, MsgData):
	MsgSQN=MsgData[0:2]
	MsgSrcAddr=MsgData[2:6]
	MsgSrcEp=MsgData[6:8]
	MsgClusterId=MsgData[8:12]
	MsgAttrID=MsgData[12:16]
	MsgAttType=MsgData[16:20]
	MsgAttSize=MsgData[20:24]
	MsgClusterData=MsgData[24:len(MsgData)]
	tmpEp=""
	tmpClusterid=""
	if DeviceExist(self, MsgSrcAddr)==False :
		self.ListOfDevices[MsgSrcAddr]['Ep'][MsgSrcEp]={}
		self.ListOfDevices[MsgSrcAddr]['Ep'][MsgSrcEp][MsgClusterId]={}

	else :
		self.ListOfDevices[MsgSrcAddr]['RIA']=str(int(self.ListOfDevices[MsgSrcAddr]['RIA'])+1)
		try : 
			tmpEp=self.ListOfDevices[MsgSrcAddr]['Ep'][MsgSrcEp]
			try :
				tmpClusterid=self.ListOfDevices[MsgSrcAddr]['Ep'][MsgSrcEp][MsgClusterId]
			except : 
				self.ListOfDevices[MsgSrcAddr]['Ep'][MsgSrcEp][MsgClusterId]={}
		except :
			self.ListOfDevices[MsgSrcAddr]['Ep'][MsgSrcEp]={}
			self.ListOfDevices[MsgSrcAddr]['Ep'][MsgSrcEp][MsgClusterId]={}

	if MsgClusterId=="0000" :  # (General: Basic)
		if MsgAttrID=="ff01" :  # xiaomi battery lvl
			MsgBattery=MsgClusterData[4:8]
			try :
				ValueBattery='%s%s' % (str(MsgBattery[2:4]),str(MsgBattery[0:2]))
				ValueBattery=round(int(ValueBattery,16)/10/3)
				Domoticz.Debug("ReadCluster (8102) - ClusterId=0000 - MsgAttrID=ff01 - reception batteryLVL : " + str(ValueBattery) + " pour le device addr : " +  MsgSrcAddr)
				if self.ListOfDevices[MsgSrcAddr]['Status']=="inDB":
					UpdateBattery(MsgSrcAddr,ValueBattery)
				self.ListOfDevices[MsgSrcAddr]['Battery']=ValueBattery
			except :
				Domoticz.Debug("ReadCluster (8102) - ClusterId=0000 - MsgAttrID=ff01 - reception batteryLVL : erreur de lecture pour le device addr : " +  MsgSrcAddr)
		elif MsgAttrID=="0005" :  # Model info Xiaomi
			MType=binascii.unhexlify(MsgClusterData).decode('utf-8')
			Domoticz.Debug("ReadCluster (8102) - ClusterId=0000 - MsgAttrID=0005 - reception Model de Device : " + MType)
			self.ListOfDevices[MsgSrcAddr]['Model']=MType
			if self.ListOfDevices[MsgSrcAddr]['Model']!= {} and self.ListOfDevices[MsgSrcAddr]['Model'] in self.DeviceConf : # verifie que le model existe ds le fichier de conf des models
				Modeltmp=str(self.ListOfDevices[MsgSrcAddr]['Model'])
				for Ep in self.DeviceConf[Modeltmp]['Ep'] :
					if Ep in self.ListOfDevices[MsgSrcAddr]['Ep'] :
						for cluster in self.DeviceConf[Modeltmp]['Ep'][Ep] :
							if cluster not in self.ListOfDevices[MsgSrcAddr]['Ep'][Ep] :
								self.ListOfDevices[MsgSrcAddr]['Ep'][Ep][cluster]={}
					else :
						self.ListOfDevices[MsgSrcAddr]['Ep'][Ep]={}
						for cluster in self.DeviceConf[Modeltmp]['Ep'][Ep] :
							self.ListOfDevices[MsgSrcAddr]['Ep'][Ep][cluster]={}
				self.ListOfDevices[MsgSrcAddr]['Type']=self.DeviceConf[Modeltmp]['Type']
		else :
			Domoticz.Debug("ReadCluster (8102) - ClusterId=0000 - reception heartbeat - Message attribut inconnu : " + MsgData)
	
	elif MsgClusterId=="0006" :  # (General: On/Off) xiaomi
		MajDomoDevice(self, MsgSrcAddr, MsgSrcEp, MsgClusterId, MsgClusterData)
		self.ListOfDevices[MsgSrcAddr]['Ep'][MsgSrcEp][MsgClusterId]=MsgClusterData
		Domoticz.Debug("ReadCluster (8102) - ClusterId=0006 - reception General: On/Off : " + str(MsgClusterData) )
	
	elif MsgClusterId=="0402" :  # (Measurement: Temperature) xiaomi
		#MsgValue=Data[len(Data)-8:len(Data)-4]
		MajDomoDevice(self, MsgSrcAddr, MsgSrcEp, MsgClusterId,round(int(MsgClusterData,16)/100,1))
		self.ListOfDevices[MsgSrcAddr]['Ep'][MsgSrcEp][MsgClusterId]=round(int(MsgClusterData,16)/100,1)
		Domoticz.Debug("ReadCluster (8102) - ClusterId=0402 - reception temp : " + str(int(MsgClusterData,16)/100) )
				
	elif MsgClusterId=="0403" :  # (Measurement: Pression atmospherique) xiaomi   ### a corriger/modifier http://zigate.fr/xiaomi-capteur-temperature-humidite-et-pression-atmospherique-clusters/
		if MsgAttType=="0028":
			#MajDomoDevice(self, MsgSrcAddr,MsgSrcEp,"Barometer",round(int(MsgClusterData,8))
			self.ListOfDevices[MsgSrcAddr]['Ep'][MsgSrcEp][MsgClusterId]=MsgClusterData
			Domoticz.Debug("ReadCluster (8102) - ClusterId=0403 - reception atm : " + str(MsgClusterData) )
			
		if MsgAttType=="0029" and MsgAttrID=="0000":
			#MsgValue=Data[len(Data)-8:len(Data)-4]
			MajDomoDevice(self, MsgSrcAddr, MsgSrcEp, MsgClusterId,round(int(MsgClusterData,16)/100,1))
			self.ListOfDevices[MsgSrcAddr]['Ep'][MsgSrcEp][MsgClusterId]=round(int(MsgClusterData,16)/100,1)
			Domoticz.Debug("ReadCluster (8102) - ClusterId=0403 - reception atm : " + str(round(int(MsgClusterData,16),1)))
			
		if MsgAttType=="0029" and MsgAttrID=="0010":
			#MsgValue=Data[len(Data)-8:len(Data)-4]
			MajDomoDevice(self, MsgSrcAddr, MsgSrcEp, MsgClusterId,round(int(MsgClusterData,16)/10,1))
			self.ListOfDevices[MsgSrcAddr]['Ep'][MsgSrcEp][MsgClusterId]=round(int(MsgClusterData,16)/10,1)
			Domoticz.Debug("ReadCluster (8102) - ClusterId=0403 - reception atm : " + str(round(int(MsgClusterData,16)/10,1)))

	elif MsgClusterId=="0405" :  # (Measurement: Humidity) xiaomi
		#MsgValue=Data[len(Data)-8:len(Data)-4]
		MajDomoDevice(self, MsgSrcAddr, MsgSrcEp, MsgClusterId,round(int(MsgClusterData,16)/100,1))
		self.ListOfDevices[MsgSrcAddr]['Ep'][MsgSrcEp][MsgClusterId]=round(int(MsgClusterData,16)/100,1)
		Domoticz.Debug("ReadCluster (8102) - ClusterId=0405 - reception hum : " + str(int(MsgClusterData,16)/100) )

	elif MsgClusterId=="0406" :  # (Measurement: Occupancy Sensing) xiaomi
		MajDomoDevice(self, MsgSrcAddr, MsgSrcEp, MsgClusterId,MsgClusterData)
		self.ListOfDevices[MsgSrcAddr]['Ep'][MsgSrcEp][MsgClusterId]=MsgClusterData
		Domoticz.Debug("ReadCluster (8102) - ClusterId=0406 - reception Occupancy Sensor : " + str(MsgClusterData) )

	elif MsgClusterId=="0400" :  # (Measurement: LUX) xiaomi
		MajDomoDevice(self, MsgSrcAddr, MsgSrcEp, MsgClusterId,str(int(MsgClusterData,16) ))
		self.ListOfDevices[MsgSrcAddr]['Ep'][MsgSrcEp][MsgClusterId]=MsgClusterData
		Domoticz.Debug("ReadCluster (8102) - ClusterId=0400 - reception LUX Sensor : " + str(MsgClusterData) )
		
	elif MsgClusterId=="0012" :  # Magic Cube Xiaomi
		MajDomoDevice(self, MsgSrcAddr, MsgSrcEp, MsgClusterId,MsgClusterData)
		self.ListOfDevices[MsgSrcAddr]['Ep'][MsgSrcEp][MsgClusterId]=MsgClusterData
		Domoticz.Debug("ReadCluster (8102) - ClusterId=0012 - reception Xiaomi Magic Cube Value : " + str(MsgClusterData) )
		
	elif MsgClusterId=="000c" :  # Magic Cube Xiaomi rotation
		MajDomoDevice(self, MsgSrcAddr, MsgSrcEp, MsgClusterId,MsgClusterData)
		self.ListOfDevices[MsgSrcAddr]['Ep'][MsgSrcEp][MsgClusterId]=MsgClusterData
		Domoticz.Debug("ReadCluster (8102) - ClusterId=000c - reception Xiaomi Magic Cube Value Vert Rot : " + str(MsgClusterData) )
		
	else :
		Domoticz.Debug("ReadCluster (8102) - Error/unknow Cluster Message : " + MsgClusterId)

def CheckType(self, MsgSrcAddr) :
	Domoticz.Debug("CheckType of device : " + MsgSrcAddr)
	x=0
	found=False
	for x in Devices:
		if Devices[x].DeviceID == str(MsgSrcAddr) :
			found=True
	
	if found==False :
		#check type with domoticz device type then add or del then re add device
		self.ListOfDevices[MsgSrcAddr]['Status']="inDB"
		
def GetType(self, Addr, Ep) :
	if self.ListOfDevices[Addr]['Model']!={} and self.ListOfDevices[Addr]['Model'] in self.DeviceConf :  # verifie si le model a été détecté et est connu dans le fichier DeviceConf.txt
		Type = self.DeviceConf[self.ListOfDevices[Addr]['Model']]['Type']
	else :
		Type=""
		for cluster in self.ListOfDevices[Addr]['Ep'][Ep] :
			if Type != "" and Type[:1]!="/" :
				Type+="/"
			Type+=TypeFromCluster[cluster]
		self.ListOfDevices[Addr]['Type']=Type
	return Type
