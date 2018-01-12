# Zigate Python Plugin
#
# Author: zaraki673
#

"""
<plugin key="Zigate" name="Zigate plugin" author="zaraki673" version="1.1.1" wikilink="http://www.domoticz.com/wiki/plugins/zigate.html" externallink="https://www.zigate.fr/">
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
		<param field="Mode3" label="Full reset ( !!! réassociation de tous les devices obligatoirs !!! ): " width="75px">
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

class BasePlugin:
	enabled = False

	def __init__(self):
		return

	def onStart(self):
		Domoticz.Log("onStart called")
		global ReqRcv
		global ZigateConn
		if Parameters["Mode6"] == "Debug":
			Domoticz.Debugging(1)
		if Parameters["Mode1"] == "USB":
			ZigateConn = Domoticz.Connection(Name="ZiGate", Transport="Serial", Protocol="None", Address=Parameters["SerialPort"], Baud=115200)
			ZigateConn.Connect()
		if Parameters["Mode1"] == "Wifi":
			ZigateConn = Domoticz.Connection(Name="Zigate", Transport="TCP/IP", Protocol="None", Address=Parameters["Address"], Port=Parameters["Port"])
			ZigateConn.Connect()
		ReqRcv=''


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
#		Domoticz.Log("onMessage called")
		global Tmprcv
		global ReqRcv
		Tmprcv=binascii.hexlify(Data).decode('utf-8')
		if Tmprcv.find('03') != -1 and len(ReqRcv+Tmprcv[:Tmprcv.find('03')+2])%2==0 :### fin de messages detecter dans Data
			ReqRcv+=Tmprcv[:Tmprcv.find('03')+2] #
			try :
				if ReqRcv.find("0301") == -1 : #verifie si pas deux messages coller ensemble
					ZigateDecode(ReqRcv) #demande de decodage de la trame recu
					ReqRcv=Tmprcv[Tmprcv.find('03')+2:]  # traite la suite du tampon
				else : 
					ZigateDecode(ReqRcv[:ReqRcv.find("0301")+2])
					ZigateDecode(ReqRcv[ReqRcv.find("0301")+2:])
					ReqRcv=Tmprcv[Tmprcv.find('03')+2:]
			except :
				Domoticz.Debug("onMessage - effacement de la trame suite a une erreur de decodage : " + ReqRcv)
				ReqRcv = Tmprcv[Tmprcv.find('03')+2:]  # efface le tampon en cas d erreur
		else : # while end of data is receive
			ReqRcv+=Tmprcv
		return

	def onCommand(self, Unit, Command, Level, Hue):
		Domoticz.Log("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))

	def onDisconnect(self, Connection):
		Domoticz.Log("onDisconnect called")

	def onHeartbeat(self):
#		Domoticz.Log("onHeartbeat called")
		ResetDevice("lumi.sensor_motion.aq2")
		ResetDevice("lumi.sensor_motion")
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
	return

def ZigateConf():

	################### ZiGate - set channel 11 ##################
	sendZigateCmd("0021","0004", "00000800")

	################### ZiGate - Set Type COORDINATOR#################
	sendZigateCmd("0023","0001","00")
	
	################### ZiGate - start network##################
	sendZigateCmd("0024","0000","")

	################### ZiGate - discover mode 255sec ##################
	sendZigateCmd("0049","0004","FFFC" + hex(int(Parameters["Mode2"]))[2:4] + "00")

def ZigateDecode(Data):  # supprime le transcodage
	Domoticz.Debug("ZigateDecode - decodind data : " + Data)
	Out=""
	Outtmp=""
	Transcode = False
	for c in Data :
		Outtmp+=c
		if len(Outtmp)==2 :
			if Outtmp == "02" :
				Transcode=True
			else :
				if Transcode == True:
					Transcode = False
					if Outtmp[0]=="1" :
						Out+="0"
					else :
						Out+="1"
					Out+=Outtmp[1]
					#Out+=str(int(str(Outtmp)) - 10)
				else :
					Out+=Outtmp
			Outtmp=""
	Zigate.Read(Out)

def ZigateEncode(Data):  # ajoute le transcodage
	Domoticz.Debug("ZigateDecode - Encodind data : " + Data)
	Out=""
	Outtmp=""
	Transcode = False
	for c in Data :
		Outtmp+=c
		if len(Outtmp)==2 :
			if Outtmp[0] == "1" :
				if Outtmp[1] == "0" :
					Outtmp="0200"
					Out+=Outtmp
				else :
					Out+=Outtmp
			elif Outtmp[0] == "0" :
				Out+="021" + Outtmp[1]
			else :
				Out+=Outtmp
			Outtmp=""
	Domoticz.Debug("Transcode in : " + str(Data) + "  / out :" + str(Out) )
	return Out

def sendZigateCmd(cmd,length,datas) :
	if datas =="" :
		checksumCmd=getChecksum(cmd,length,"0")
		if len(checksumCmd)==1 :
			strchecksum="0" + str(checksumCmd)
		else :
			strchecksum=checksumCmd
		lineinput="01" + str(ZigateEncode(cmd)) + str(ZigateEncode(length)) + str(strchecksum) + "03" 
	else :
		checksumCmd=getChecksum(cmd,length,datas)
		if len(checksumCmd)==1 :
			strchecksum="0" + str(checksumCmd)
		else :
			strchecksum=checksumCmd
		lineinput="01" + str(ZigateEncode(cmd)) + str(ZigateEncode(length)) + str(strchecksum) + str(ZigateEncode(datas)) + "03"   
	Domoticz.Debug("sendZigateCmd - Comand send : " + str(lineinput))
	if Parameters["Mode1"] == "USB":
		ZigateConn.Send(bytes.fromhex(str(lineinput)))	
	if Parameters["Mode1"] == "Wifi":
		ZigateConn.Send(bytes.fromhex(str(lineinput))+bytes("\r\n",'utf-8'),1)
	
def CreateDomoDevice(nbrdevices,Addr,Ep,Type) :
	DeviceID=Addr #int(Addr,16)
	Domoticz.Debug("CreateDomoDevice - Device ID : " + str(DeviceID) + " Device EP : " + str(Ep) + " Type : " + str(Type) )
	if Type=="lumi.weather" :  # Detecteur temp/hum/baro xiaomi (v2)
		typename="Temp+Hum+Baro"
		Domoticz.Device(DeviceID=str(DeviceID),Name=str(typename) + " - " + str(DeviceID), Unit=nbrdevices, TypeName=typename, Options={"EP":str(Ep), "devices_type": str(Type), "typename":str(typename)}).Create()
		typename="Temp+Hum"
		Domoticz.Device(DeviceID=str(DeviceID),Name=str(typename) + " - " + str(DeviceID), Unit=nbrdevices+1, TypeName=typename, Options={"EP":str(Ep), "devices_type": str(Type), "typename":str(typename)}).Create()
		typename="Temperature"
		Domoticz.Device(DeviceID=str(DeviceID),Name=str(typename) + " - " + str(DeviceID), Unit=nbrdevices+2, TypeName=typename, Options={"EP":str(Ep), "devices_type": str(Type), "typename":str(typename)}).Create()
		typename="Humidity"
		Domoticz.Device(DeviceID=str(DeviceID),Name=str(typename) + " - " + str(DeviceID), Unit=nbrdevices+3, TypeName=typename, Options={"EP":str(Ep), "devices_type": str(Type), "typename":str(typename)}).Create()
		typename="Barometer"
		Domoticz.Device(DeviceID=str(DeviceID),Name=str(typename) + " - " + str(DeviceID), Unit=nbrdevices+4, TypeName=typename, Options={"EP":str(Ep), "devices_type": str(Type), "typename":str(typename)}).Create()
		
	if Type=="lumi.sensor_ht" : # Detecteur temp/humi xiaomi (v1)
		typename="Temp+Hum"
		Domoticz.Device(DeviceID=str(DeviceID),Name=str(typename) + " - " + str(DeviceID), Unit=nbrdevices, TypeName=typename, Options={"EP":str(Ep), "devices_type": str(Type), "typename":str(typename)}).Create()
		typename="Temperature"
		Domoticz.Device(DeviceID=str(DeviceID),Name=str(typename) + " - " + str(DeviceID), Unit=nbrdevices+1, TypeName=typename, Options={"EP":str(Ep), "devices_type": str(Type), "typename":str(typename)}).Create()
		typename="Humidity"
		Domoticz.Device(DeviceID=str(DeviceID),Name=str(typename) + " - " + str(DeviceID), Unit=nbrdevices+2, TypeName=typename, Options={"EP":str(Ep), "devices_type": str(Type), "typename":str(typename)}).Create()
		
	if Type=="lumi.sensor_magnet.aq2" or Type=="lumi.sensor_magnet": # capteur ouverture/fermeture xiaomi  (v1 et v2)
		typename="Switch"
		Domoticz.Device(DeviceID=str(DeviceID),Name=str(typename) + " - " + str(DeviceID), Unit=nbrdevices, Type=244, Subtype=73 , Switchtype=2 , Options={"EP":str(Ep), "devices_type": str(Type), "typename":str(typename)}).Create()
		
	if Type=="lumi.sensor_motion" :  # detecteur de presence (v1) xiaomi
		typename="Switch"
		Domoticz.Device(DeviceID=str(DeviceID),Name=str(typename) + " - " + str(DeviceID), Unit=nbrdevices, Type=244, Subtype=73 , Switchtype=8 , Options={"EP":str(Ep), "devices_type": str(Type), "typename":str(typename)}).Create()

	if Type=="lumi.sensor_switch.aq2" or Type=="lumi.sensor_switch"  :  # petit inter rond ou carre xiaomi (v1)
		typename="Switch"		
		Options = {"LevelActions": "||||", "LevelNames": "Off|1 Click|2 Clicks|3 Clicks|4 Clicks", "LevelOffHidden": "true", "SelectorStyle": "0","EP":str(Ep), "devices_type": str(Type), "typename":str(typename)}
		Domoticz.Device(DeviceID=str(DeviceID),Name="lumi.sensor_switch.aq2" + " - " + str(DeviceID), Unit=nbrdevices, Type=244, Subtype=62 , Switchtype=18, Options = Options).Create()
		
	if Type=="lumi.sensor_86sw2"  :  #inter sans fils 2 touches 86sw2 xiaomi
		typename="Switch"		
		Options = {"LevelActions": "|||", "LevelNames": "Off|Left Click|Right Click|Both Click", "LevelOffHidden": "true", "SelectorStyle": "0","EP":str(Ep), "devices_type": str(Type), "typename":str(typename)}
		Domoticz.Device(DeviceID=str(DeviceID),Name="lumi.sensor_86sw2" + " - " + str(DeviceID), Unit=nbrdevices, Type=244, Subtype=62 , Switchtype=18, Options = Options).Create()
		
	if Type=="lumi.sensor_smoke" :  # detecteur de fumee (v1) xiaomi
		typename="Switch"
		Domoticz.Device(DeviceID=str(DeviceID),Name=str(typename) + " - " + str(DeviceID), Unit=nbrdevices, Type=244, Subtype=73 , Switchtype=5 , Options={"EP":str(Ep), "devices_type": str(Type), "typename":str(typename)}).Create()

	if Type=="lumi.sensor_wleak.aq1" :  # detecteur d'eau (v1) xiaomi
		typename="Switch"
		Domoticz.Device(DeviceID=str(DeviceID),Name=str(typename) + " - " + str(DeviceID), Unit=nbrdevices, Type=244, Subtype=73 , Switchtype=0 , Options={"EP":str(Ep), "devices_type": str(Type), "typename":str(typename)}).Create()

	if Type=="lumi.sensor_motion.aq2" :  # Lux sensors + detecteur xiaomi v2
		typename="Lux"
		Domoticz.Device(DeviceID=str(DeviceID),Name=str(typename) + " - " + str(DeviceID), Unit=nbrdevices, Type=246, Subtype=1 , Switchtype=0 , Options={"EP":str(Ep), "devices_type": str(Type), "typename":str(typename)}).Create()
		typename="Switch"
		Domoticz.Device(DeviceID=str(DeviceID),Name=str(typename) + " - " + str(DeviceID), Unit=nbrdevices+1, Type=244, Subtype=73 , Switchtype=8 , Options={"EP":str(Ep), "devices_type": str(Type), "typename":str(typename)}).Create()

	if Type=="lumi.sensor_86sw1":  # inter sans fils 1 touche 86sw1 xiaomi
		typename="Switch"
		Domoticz.Device(DeviceID=str(DeviceID),Name=str(typename) + " - " + str(DeviceID), Unit=nbrdevices, Type=244, Subtype=73 , Switchtype=9 , Options={"EP":str(Ep), "devices_type": str(Type), "typename":str(typename)}).Create()
		
	if Type=="lumi.sensor_cube" :  # Xiaomi Magic Cube
		#typename="Text"
		#Domoticz.Device(DeviceID=str(DeviceID),Name="lumi.sensor_cube-text" + " - " + str(DeviceID), Unit=nbrdevices, Type=243, Subtype=19 , Switchtype=0 , Options={"EP":str(Ep), "devices_type": str(Type), "typename":str(typename)}).Create()
		typename="Switch"		
		Options = {"LevelActions": "||||||||", "LevelNames": "Off|Shake|Slide|90°|Clockwise|Tap|Move|Free Fall|Anti Clockwise|180°", "LevelOffHidden": "true", "SelectorStyle": "0","EP":str(Ep), "devices_type": str(Type), "typename":str(typename)}
		Domoticz.Device(DeviceID=str(DeviceID),Name="lumi.sensor_cube" + " - " + str(DeviceID), Unit=nbrdevices+1, Type=244, Subtype=62 , Switchtype=18, Options = Options).Create()
		
def MajDomoDevice(Addr,Ep,Type,value) :
	Domoticz.Debug("MajDomoDevice - Device ID : " + str(Addr) + " - Device EP : " + str(Ep) + " - Type : " + str(Type)  + " - Value : " + str(value) )
	x=0
	nbrdevices=1
	DeviceID=Addr #int(Addr,16)
	for x in Devices:
		if Devices[x].DeviceID == str(DeviceID) : 
			DOptions = Devices[x].Options
			DType=DOptions['devices_type']
			Dtypename=DOptions['typename']
			if DType=="lumi.weather" : #temp+hum+baro xiaomi
				if Type==Dtypename=="Temperature" :  # temperature
					#Devices[x].Update(nValue = 0,sValue = str(value))	
					UpdateDevice(x,0,str(value))				
				if Type==Dtypename=="Humidity" :   # humidite
					#Devices[x].Update(nValue = int(value), sValue = "0")	
					UpdateDevice(x,int(value),"0")				
				if Type==Dtypename=="Barometer" :  # barometre
					CurrentnValue=Devices[x].nValue
					CurrentsValue=Devices[x].sValue
					Domoticz.Debug("MajDomoDevice baro CurrentsValue : " + CurrentsValue)
					SplitData=CurrentsValue.split(";")
					valueBaro='%s;%s' % (value,SplitData[0])
					#Devices[x].Update(nValue = 0,sValue = str(valueBaro))	
					UpdateDevice(x,0,str(valueBaro))				
				if Dtypename=="Temp+Hum+Baro" :
					if Type=="Temperature" :
						CurrentnValue=Devices[x].nValue
						CurrentsValue=Devices[x].sValue
						Domoticz.Debug("MajDomoDevice temp CurrentsValue : " + CurrentsValue)
						SplitData=CurrentsValue.split(";")
						NewSvalue='%s;%s;%s;%s;%s'	% (str(value) ,  SplitData[1] , SplitData[2] , SplitData[3] , SplitData[4])
						Domoticz.Debug("MajDomoDevice temp NewSvalue : " + NewSvalue)
						#Devices[x].Update(nValue = 0,sValue = str(NewSvalue))		
						UpdateDevice(x,0,str(NewSvalue))									
					if Type=="Humidity" :
						CurrentnValue=Devices[x].nValue
						CurrentsValue=Devices[x].sValue
						Domoticz.Debug("MajDomoDevice hum CurrentsValue : " + CurrentsValue)
						SplitData=CurrentsValue.split(";")
						NewSvalue='%s;%s;%s;%s;%s'	% (SplitData[0], str(value) , SplitData[2] , SplitData[3] , SplitData[4])
						Domoticz.Debug("MajDomoDevice hum NewSvalue : " + NewSvalue)
						#Devices[x].Update(nValue = 0,sValue = str(NewSvalue))		
						UpdateDevice(x,0,str(NewSvalue))									
					if Type=="Barometer" :
						CurrentnValue=Devices[x].nValue
						CurrentsValue=Devices[x].sValue
						Domoticz.Debug("MajDomoDevice baro CurrentsValue : " + CurrentsValue)
						SplitData=CurrentsValue.split(";")
						NewSvalue='%s;%s;%s;%s;%s'	% (SplitData[0], SplitData[1] , SplitData[2] , str(value) , SplitData[3])
						Domoticz.Debug("MajDomoDevice bar NewSvalue : " + NewSvalue)
						#Devices[x].Update(nValue = 0,sValue = str(NewSvalue))		
						UpdateDevice(x,0,str(NewSvalue))									
				if Dtypename=="Temp+Hum" : #temp+hum xiaomi
					if Type=="Temperature" :
						CurrentnValue=Devices[x].nValue
						CurrentsValue=Devices[x].sValue
						Domoticz.Debug("MajDomoDevice temp CurrentsValue : " + CurrentsValue)
						SplitData=CurrentsValue.split(";")
						NewSvalue='%s;%s;%s'	% (str(value), SplitData[1] , SplitData[2])
						Domoticz.Debug("MajDomoDevice temp NewSvalue : " + NewSvalue)
						#Devices[x].Update(nValue = 0,sValue = str(NewSvalue))			
						UpdateDevice(x,0,str(NewSvalue))								
					if Type=="Humidity" :
						CurrentnValue=Devices[x].nValue
						CurrentsValue=Devices[x].sValue
						Domoticz.Debug("MajDomoDevice hum CurrentsValue : " + CurrentsValue)
						SplitData=CurrentsValue.split(";")
						NewSvalue='%s;%s;%s'	% (SplitData[0], str(value) , SplitData[2])
						Domoticz.Debug("MajDomoDevice hum NewSvalue : " + NewSvalue)
						#Devices[x].Update(nValue = 0,sValue = str(NewSvalue))	
						UpdateDevice(x,0,str(NewSvalue))				
	
			if DType=="lumi.sensor_ht" :
				if Type==Dtypename=="Temperature" :
					#Devices[x].Update(nValue = 0,sValue = str(value))
					UpdateDevice(x,0,str(value))
				if Type==Dtypename=="Humidity" :
					#Devices[x].Update(nValue = int(value), sValue = "0")
					UpdateDevice(x,int(value),"0")
				#if Dtypename=="Temp+Hum" :
					#Domoticz.Device(DeviceID=str(DeviceID),Name=str(typename) + " - " + str(DeviceID), Unit=nbrdevices, TypeName=typename, options={"EP":Ep, "devices_type": str(Type), "typename":str(typename)}).Create()				
				if Dtypename=="Temp+Hum" :
					if Type=="Temperature" :
						CurrentnValue=Devices[x].nValue
						CurrentsValue=Devices[x].sValue
						Domoticz.Debug("MajDomoDevice temp CurrentsValue : " + CurrentsValue)
						SplitData=CurrentsValue.split(";")
						NewSvalue='%s;%s;%s'	% (str(value), SplitData[1] , SplitData[2])
						Domoticz.Debug("MajDomoDevice temp NewSvalue : " + NewSvalue)
						#Devices[x].Update(nValue = 0,sValue = str(NewSvalue))		
						UpdateDevice(x,0,str(NewSvalue))				
					if Type=="Humidity" :
						CurrentnValue=Devices[x].nValue
						CurrentsValue=Devices[x].sValue
						Domoticz.Debug("MajDomoDevice hum CurrentsValue : " + CurrentsValue)
						SplitData=CurrentsValue.split(";")
						NewSvalue='%s;%s;%s'	% (SplitData[0], str(value) , SplitData[2])
						Domoticz.Debug("MajDomoDevice hum NewSvalue : " + NewSvalue)
						#Devices[x].Update(nValue = 0,sValue = str(NewSvalue))
						UpdateDevice(x,0,str(NewSvalue))		

			if DType=="lumi.sensor_magnet.aq2" or DType=="lumi.sensor_magnet" :  # detecteur ouverture/fermeture Xiaomi
				if Type==Dtypename :
					if value == "01" :
						state="Open"
					elif value == "00" :
						state="Closed"
					#Devices[x].Update(nValue = int(value),sValue = str(state))
					UpdateDevice(x,int(value),str(state))
				

			if DType=="lumi.sensor_86sw1" or DType=="lumi.sensor_smoke" or DType=="lumi.sensor_motion" or DType=="lumi.sensor_wleak.aq1" :  # detecteur de presence / interrupteur / detecteur de fumée
				if Type==Dtypename=="Switch" :
					if value == "01" :
						state="On"
					elif value == "00" :
						state="Off"
					#Devices[x].Update(nValue = int(value),sValue = str(state))
					UpdateDevice(x,int(value),str(state))
					
					
			if DType=="lumi.sensor_switch" or DType=="lumi.sensor_switch.aq2"  :  # interrupteur xiaomi rond et carre
				if Type==Dtypename :
					if Type=="Switch" :
						if value == "01" :
							state="10"
						elif value == "02" :
							state="20"
						elif value == "03" :
							state="30"
						elif value == "04" :
							state="40"
						#Devices[x].Update(nValue = int(value),sValue = str(state))
						UpdateDevice(x,int(value),str(state))
						
						
			if DType=="lumi.sensor_86sw2"   :  # inter 2 touches xiaomi 86sw2
				if Type==Dtypename :
					if Type=="Switch" :
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
						#Devices[x].Update(nValue = int(data),sValue = str(state))
						UpdateDevice(x,int(data),str(state))
						
						
						
			if DType=="lumi.sensor_cube"   :  # Xiaomi Magic Cube
				if Type==Dtypename :
					if Type=="Switch" :
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
					# elif Type=="Switch" : #rotation
						# elif MsgClusterId=="000c":
							# if Ep == "03" :
								# if value == "40404040" or value=="41414141" or value=="42424242" or value=="43434343" : #clockwise
								  # state="40"
								  # data="04"
						
							# # elif value == "0204" or value == "0200": #tap
								# # state="50"
								# # data="05"
								
							#Devices[x].Update(nValue = int(data),sValue = str(state))
							UpdateDevice(x,int(data),str(state))

			if DType=="lumi.sensor_motion.aq2":  # detecteur de luminosite
				if Type==Dtypename :
					if Type=="Lux" :
						#Devices[x].Update(nValue = 0 ,sValue = str(value))
						UpdateDevice(x,0,str(value))
					if Type=="Switch" :
						if value == "01" :
							state="On"
						elif value == "00" :
							state="Off"
						#Devices[x].Update(nValue = int(value),sValue = str(state))
						UpdateDevice(x,int(value),str(state))
			
def ResetDevice(Type) :
	x=0
	for x in Devices: 
		try :
			LUpdate=Devices[x].LastUpdate
			LUpdate=time.mktime(time.strptime(LUpdate,"%Y-%m-%d %H:%M:%S"))
			current = time.time()
			DOptions = Devices[x].Options
			DType=DOptions['devices_type']
			Dtypename=DOptions['typename']
			if (current-LUpdate)> 30 :
				if DType==Type :
					if Dtypename=="Switch":
						value = "00"
						state="Off"
						#Devices[x].Update(nValue = int(value),sValue = str(state))
						UpdateDevice(x,int(value),str(state))	
		except :
			return
			
			
	

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
	for x in Devices:
		if Devices[x].DeviceID == str(DeviceID):
			Domoticz.Log("Devices already exist. Unit=" + str(x))
			CurrentnValue=Devices[x].nValue
			Domoticz.Log("CurrentnValue = " + str(CurrentnValue))
			CurrentsValue=Devices[x].sValue
			Domoticz.Log("CurrentsValue = " + str(CurrentsValue))
			Domoticz.Log("BatteryLvl = " + str(BatteryLvl))
			Devices[x].Update(nValue = int(CurrentnValue),sValue = str(CurrentsValue), BatteryLevel = BatteryLvl )
	#####################################################################################################################

def UpdateDevice(Unit, nValue, sValue):
	# Make sure that the Domoticz device still exists (they can be deleted) before updating it 
	if (Unit in Devices):
		if (Devices[Unit].nValue != nValue) or (Devices[Unit].sValue != sValue):
			Devices[Unit].Update(nValue=nValue, sValue=str(sValue))
			Domoticz.Log("Update "+str(nValue)+":'"+str(sValue)+"' ("+Devices[Unit].Name+")")
	return



	

