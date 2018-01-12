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
					CreateDomoDevice(self, key)


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


def ZigateConf():

	################### ZiGate - set channel 11 ##################
	sendZigateCmd("0021","0004", "00000B00")

	################### ZiGate - Set Type COORDINATOR#################
	sendZigateCmd("0023","0001","00")
	
	################### ZiGate - start network##################
	sendZigateCmd("0024","0000","")

	################### ZiGate - discover mode 255sec ##################
	sendZigateCmd("0049","0004","FFFC" + hex(int(Parameters["Mode2"]))[2:4] + "00")

def ZigateDecode(self, Data):  # supprime le transcodage
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
	Zigate.Read(self, Out)

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
		ZigateConn.Send(bytes.fromhex(str(lineinput))+bytes("\r\n",'utf-8'))


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
			Type+=TypeFromCluster(cluster)
		self.ListOfDevices[Addr]['Type']=Type
	return Type

def TypeFromCluster(cluster):
	if cluster=="0405" :
		TypeFromCluster="Humi"
	elif cluster=="0406" :
		TypeFromCluster="Motion"
	elif cluster=="0400" :
		TypeFromCluster="Lux"
	elif cluster=="0403" :
		TypeFromCluster="Baro"
	elif cluster=="0402" :
		TypeFromCluster="Temp"
	elif cluster=="0006" :
		TypeFromCluster="Switch"
	elif cluster=="0500" :
		TypeFromCluster="Door"
	elif cluster=="0012" :
		TypeFromCluster="XCube"
	elif cluster=="000c" :
		TypeFromCluster="XCube"
	else :
		TypeFromCluster=""
	return TypeFromCluster
