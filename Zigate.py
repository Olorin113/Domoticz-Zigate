## ----
## Initialisation 
## ----
## Définition : Initialisation de tous les messages envoyé à Zigate.Read() de 0x0000 à 0xFFFF
## IN : Data
## OUT: Message pour debug
## ----
for num in range(0x0,0x10000):
	Dict_MsgData={str(hex(num))[2:6]:Unknow_Message_Type} # 

## Initaliser par défaut tous les messages 

Dict_MsgData={"004d":Device_Announce} # Device announce
Dict_MsgData={"00d1":Touchlink_Status}  #
Dict_MsgData={"8000":Status}  # Status
Dict_MsgData={"8001":Log}  # Log
Dict_MsgData={"8002":Data_indication}  #
Dict_MsgData={"8003":List_Cluster_Object}  #
Dict_MsgData={"8004":List_Attributs} #
Dict_MsgData={"8005":List_Command} #
Dict_MsgData={"8006":No_FactoryNewRestart} #
Dict_MsgData={"8007":FactoryNewRestart} #
Dict_MsgData={"8010":Version_List}  # Version
Dict_MsgData={"8014":Permit_Join_Status} #
Dict_MsgData={"8024":Network_Joined_Formed} #
Dict_MsgData={"8028":Authenticate_Response} #
Dict_MsgData={"8029":OutOfBand_Commissioning_Data} #
Dict_MsgData={"802b":User_Descriptor_Notify} #
Dict_MsgData={"802c":User_Descriptor} #
Dict_MsgData={"8030":Bind} #
Dict_MsgData={"8031":Unbind} #
Dict_MsgData={"8034":Coplex_Descriptor} #
Dict_MsgData={"8040":Network_Address} #
Dict_MsgData={"8041":IEEE_Address} #
Dict_MsgData={"8042":Node_Descriptor} #
Dict_MsgData={"8043":Simple_Descriptor}  # Simple Descriptor Response
Dict_MsgData={"8044":Power_Descriptor}  #
Dict_MsgData={"8045":Active_Endpoints}  # Active Endpoints Response
Dict_MsgData={"8046":Match_Descriptor}  #
Dict_MsgData={"8047":Management_Leave}  #
Dict_MsgData={"8048":Leave_Indication}  #
Dict_MsgData={"804a":Management_Network_Update}  #
Dict_MsgData={"804b":System_Server_Discovery}  #
Dict_MsgData={"804e":Management_LQI}  #
Dict_MsgData={"8060":Add_Group}  #
Dict_MsgData={"8061":View_Group}  #Dict_MsgData={"8062":Get_Group}  #
Dict_MsgData={"8063":Remove_Group}  #
Dict_MsgData={"80a0":View_Scene}  #
Dict_MsgData={"80a1":Add_Scene}  #
Dict_MsgData={"80a2":Remove_Scene}  #
Dict_MsgData={"80a3":Remove_All_Scene}  #
Dict_MsgData={"80a4":Store_Scene}  #
Dict_MsgData={"80a6":Scene_Membership}  #
Dict_MsgData={"8100":Real_Individual_Attribute}  # Real Individual Attribute response
Dict_MsgData={"8101":Default_Response}  # Default Response
Dict_MsgData={"8102":Report_Individual_Attribute}  # Report Individual Attribute response
Dict_MsgData={"8110":Write_Attribute}  #
Dict_MsgData={"8120":Configure_Reporting}  #
Dict_MsgData={"8140":Attribute_Discovery }  #
Dict_MsgData={"8401":Zone_Status_Change_Notification}  #
Dict_MsgData={"8701":Router_Discovery_Confirm}  # reception Router discovery confirm
Dict_MsgData={"8702":APS_Data_Confirm_Fail}  # APS Data Confirm Fail

## Pour sous-programme Status
for num in range(0x0,0x100):
	MsgDataStatus={str(hex(num))[2:6]:"ZigBee Error Code "+str(hex(num))[2:6]} # 	
	
MsgDataStatus={"00":"Success"}
MsgDataStatus={"01":"Incorrect Parameters"}
MsgDataStatus={"02":"Unhandled Command"}
MsgDataStatus={"03":"Command Failed"}
MsgDataStatus={"04":"Busy"}
MsgDataStatus={"05":"Stack Already Started"}


## ---------
## Read
## ---------
## Definition : Lire les données que la Zigate nous renvois
## IN : Données brut => Data
## OUT : N/A
## ---------
def Read(Data):
	Domoticz.Debug("Zigate.Read - decoded data : " + Data)
	
	#Trame serie
	#
	#0	 1	 2	 3	 4 	 5 	 6	 7	 8 	 9	 10	 11	 12	14 16 18 20 22 24 26 28 30 32 34 36 38 ...
	#1		|2		|3		|4		|5		|6		|7  											|n+8	|n+9
	#0x01	|		|		|n				|		|												|		|0x03
	#Start	| MSG TYPE		|LENGTH			|CHKSM	|DATA											|RSSI	|STOP
	#
	#01		 81		 02		 00		 0f		 06		 b9 cd 4d 01 04 03 00 10 00 29 00 02 27 3a		 93		 03
	#01		 81		 02		 00		 0f		 89		 50 2a 61 01 04 02 00 00 00 29 00 02 07 fa		 cf 	 03
	#01		 81		 02		 00		 0e		 c6		 c0 cd 4d 01 04 03 00 14 00 28 00 01 ff 		 cf 	 03
	#01		 81		 02		 00		 0f		 f9		 d6 cd 4d 01 04 05 00 00 00 21 00 02 16 d9 		 cf	 	 03
	#01		 81		 02		 00		 32		 c3		 bd cd 4d 01 00 00 ff 01 00 42 00 25 01 21 bd 0b 04 21 a8 13 05 21 06 00 06 24 01 00 00 00 00 64 29 75 07 65 21 22 16 66 2b b0 89 01 00 0a 21 00 00 	 cf		 03
	#01		 81		 02		 00		 0e		 98		 c7	cd 4d 01 04 03 00 14 00 28 00 01 ff 		 96		 03
	#01		 81		 02		 00		 0F		 AB		 02 6F 2F 01 04 02 00 00 00 29 00 02 09 89 		 C9		 03
	#01		 80		 45		 00		 07		 23		 290007780101									 b7		 03
	#01		 80		 43		 02		 10		 1e		 021f3302106a0217160211021102145f0211021102140210021002100213ffff0210021602130210021002100213ffff02100216	 c6		 03
	#01		 80		 43		 00	 	 1e		 8c		 42008439160101045f01010400000003ffff00060300000003ffff0006				e4 		03

	Dict_Data={"MsgType":Data[2:6]}
	Dict_Data={"MsgData":Data[12:len(Data)-4]}
	Dict_Data={"MsgRSSI":Data[len(Data)-4:len(Data)-2]}
	Dict_Data={"MsgLength":Data[6:10]}
	Dict_Data={"MsgCRC":Data[10:12]}
	Dict_Data={"Data":Data}
	
	Domoticz.Debug("ZigateRead - Message Type : " + Dict_Data[MsgType] + ", Data : " + Dict_Data[MsgData] + ", RSSI : " + Dict_Data[MsgRSSI] + ", Length : " + Dict_Data[MsgLength] + ", Checksum : " + Dict_Data[MsgCRC])

	MsgRetour=Dict_MsgData[str(MsgType)](Dict_Data)
   	Domoticz.Debug("ZigateRead - MsgType "+ str(Dict_Data["MsgType"]) + " - " + MsgRetour )
    
## -----
## Unknow_Message_Type
## -----
## Definition :
## IN : Data dictionnary
## OUT: message for debug
## -----
def Unknow_Message_Type(Dict_Data):
	return("Unknow Message Type for : " + Dict_Data["Data"])

## -----
## Device_Announce
## -----
## Definition :
## IN : Data dictionnary
## OUT: message for debug
## -----
def Device_Announce(self,Dict_Data):
	MsgSrcAddr=Dict_Data[MsgData][0:4]
	MsgIEEE=Dict_Data[MsgData]MsgData[4:20]
	MsgMacCapa=Dict_Data[MsgData]MsgData[20:22]
		
	if DeviceExist(self, MsgSrcAddr)==False :
		self.ListOfDevices[MsgSrcAddr]['MacCapa']=MsgMacCapa
		self.ListOfDevices[MsgSrcAddr]['IEEE']=MsgIEEE
		
	return("reception Device announce : Source :" + MsgSrcAddr + ", IEEE : "+ MsgIEEE + ", Mac capa : " + MsgMacCapa)
	
## -----
## Touchlink_Status
## -----
## Definition :
## IN : Data dictionnary
## OUT: message for debug
## -----
def Touchlink_Status(self,Dict_Data):
	return("reception Touchlink status : " + Dict_Data["Data"])

## -----
## Status
## -----
## Definition :
## IN : Data dictionnary
## OUT: message for debug
## -----
def Status(self,Dict_Data):
	MsgDataLenght=Dict_Data{"MsgType":MsgData[0:4]}
	MsgDataStatus=Dict_Data{"MsgType":MsgData[4:6]}
	MsgDataSQN=Dict_Data{"MsgType":MsgData[6:8]}

	if int(MsgDataLenght,16) > 2 :
		MsgDataMessage=Dict_Data{"MsgType":MsgData[8:len(MsgData)]}
	else :
		MsgDataMessage=""

	return("Reception status : " + MsgDataStatus + ", SQN : " + MsgDataSQN + ", Message : " + MsgDataMessage)
	
## -----
## Log
## -----
## Definition :
## IN : Data dictionnary
## OUT: message for debug
## -----
def Log(self,Dict_Data):
	MsgLogLvl=MsgData[0:2]
	MsgDataMessage=MsgData[2:len(MsgData)]
	
	return("Reception log Level 0x: " + MsgLogLvl + "Message : " + MsgDataMessage)

## -----
## Data_indication
## -----
## Definition :
## IN : Data dictionnary
## OUT: message for debug
## -----
def Data_indication(self,Dict_Data):
	return("Reception Data indication : " + Dict_Data["Data"])

## -----
## List_Cluster_Object
## -----
## Definition :
## IN : Data dictionnary
## OUT: message for debug
## -----
def List_Cluster_Object(self,Dict_Data):
	return("Reception Liste des cluster de l'objet : " + Dict_Data["Data"])

## -----
## List_Attributs
## -----
## Definition :
## IN : Data dictionnary
## OUT: message for debug
## -----
def List_Attributs(self,Dict_Data):
	return("Reception Liste des attributs de l'objet : " + Dict_Data["Data"])

## -----
## List_Command
## -----
## Definition :
## IN : Data dictionnary
## OUT: message for debug
## -----
def List_Command(self,Dict_Data):
	return("Reception Liste des commandes de l'objet : " + Dict_Data["Data"])
	
## -----
## No_FactoryNewRestart
## -----
## Definition :
## IN : Data dictionnary
## OUT: message for debug
## -----
def No_FactoryNewRestart(self,Dict_Data):
	return("Reception Non factory new restart : " + Dict_Data["Data"])

## -----
## FactoryNewRestart
## -----
## Definition :
## IN : Data dictionnary
## OUT: message for debug
## -----
def FactoryNewRestart(self,Dict_Data):
	return("Reception Factory new restart : " + Dict_Data["Data"])

## -----
## Version_List
## -----
## Definition :
## IN : Data dictionnary
## OUT: message for debug
## -----
def Version_List(self,Dict_Data):
	MsgDataApp=Dict_Data["Data"][0:4]
	MsgDataSDK=Dict_Data["Data"][4:8]
	
	return("Reception Version list : " + Dict_Data["Data"])

## -----
## Permit_Join_Status
## -----
## Definition :
## IN : Data dictionnary
## OUT: message for debug
## -----
def Permit_Join_Status(self,Dict_Data):
	return("Reception Permit join status response : " + Dict_Data["Data"])

## -----
## Network_Joined_Formed
## -----
## Definition :
## IN : Data dictionnary
## OUT: message for debug
## -----
def Network_Joined_Formed(self,Dict_Data):
	return("Reception Network joined /formed : " + Dict_Data["Data"])

## -----
## Authenticate_Response
## -----
## Definition :
## IN : Data dictionnary
## OUT: message for debug
## -----
def Authenticate_Response(self,Dict_Data):
	return("Reception Authenticate response : " + Dict_Data["Data"])

## -----
## OutOfBand_Commissioning_Data
## -----
## Definition :
## IN : Data dictionnary
## OUT: message for debug
## -----
def OutOfBand_Commissioning_Data(self,Dict_Data):
	return("Reception Out of band commissioning data response : " + Dict_Data["Data"])

## -----
## User_Descriptor_Notify
## -----
## Definition :
## IN : Data dictionnary
## OUT: message for debug
## -----
def User_Descriptor_Notify(self,Dict_Data):
	return("Reception User descriptor notify : " + Dict_Data["Data"])

## -----
## User_Descriptor
## -----
## Definition :
## IN : Data dictionnary
## OUT: message for debug
## -----
def User_Descriptor(self,Dict_Data):
	return("Reception User descriptor response : " + Dict_Data["Data"])

## -----
## Bind
## -----
## Definition :
## IN : Data dictionnary
## OUT: message for debug
## -----
def Bind(self,Dict_Data):
	return("Reception Bind response : " + Dict_Data["Data"])

## -----
## Unbind
## -----
## Definition :
## IN : Data dictionnary
## OUT: message for debug
## -----
def Unbind(self,Dict_Data):
	return("Reception Unbind response : " + Dict_Data["Data"])

## -----
## Coplex_Descriptor
## -----
## Definition :
## IN : Data dictionnary
## OUT: message for debug
## -----
def Coplex_Descriptor(self,Dict_Data):
	return("Reception Coplex Descriptor response : " + Dict_Data["Data"])

## -----
## Network_Address
## -----
## Definition :
## IN : Data dictionnary
## OUT: message for debug
## -----
def Network_Address(self,Dict_Data):
	return("Reception Network address response : " + Dict_Data["Data"])
	
## -----
## IEEE_Address
## -----
## Definition :
## IN : Data dictionnary
## OUT: message for debug
## -----
def IEEE_Address(self,Dict_Data):
	return("Reception IEEE address response : " + Dict_Data["Data"])

## -----
## Node_Descriptor
## -----
## Definition :
## IN : Data dictionnary
## OUT: message for debug
## -----
def Node_Descriptor(self,Dict_Data):
	return("Reception Node descriptor response : " + Dict_Data["Data"])
	
## -----
## Simple_Descriptor
## -----
## Definition :
## IN : Data dictionnary
## OUT: message for debug
## -----
def Simple_Descriptor(self,Dict_Data):
MsgDataSQN=Dict_Data["MsgData"][0:2]
	MsgDataStatus=Dict_Data["MsgData"][2:4]
	MsgDataShAddr=Dict_Data["MsgData"][4:8]
	MsgDataLenght=Dict_Data["MsgData"][8:10]
	
	if self.ListOfDevices[MsgDataShAddr]['Status']!="inDB" :
		self.ListOfDevices[MsgDataShAddr]['Status']="8043"
	if int(MsgDataLenght,16)>0 :
		MsgDataEp=Dict_Data["MsgData"][10:12]
		MsgDataProfile=Dict_Data["MsgData"][12:16]
		MsgDataDeviceId=Dict_Data["MsgData"][16:20]
		MsgDataBField=Dict_Data["MsgData"][20:22]
		MsgDataInClusterCount=Dict_Data["MsgData"][22:24]
		Domoticz.Debug("Decode8043 - Reception Simple descriptor response : EP : " + MsgDataEp + ", Profile : " + MsgDataProfile + ", Device Id : " + MsgDataDeviceId + ", Bit Field : " + MsgDataBField)
		Domoticz.Debug("Decode8043 - Reception Simple descriptor response : In Cluster Count : " + MsgDataInClusterCount)
		i=1
		if int(MsgDataInClusterCount,16)>0 :
			while i <= int(MsgDataInClusterCount,16) :
				MsgDataCluster=Dict_Data["MsgData"][24+((i-1)*4):24+(i*4)]
				if MsgDataCluster not in self.ListOfDevices[MsgDataShAddr]['Ep'][MsgDataEp] :
					self.ListOfDevices[MsgDataShAddr]['Ep'][MsgDataEp][MsgDataCluster]={}
				Domoticz.Debug("Decode8043 - Reception Simple descriptor response : Cluster in: " + MsgDataCluster)
				MsgDataCluster=""
				i=i+1
		MsgDataOutClusterCount=Dict_Data["MsgData"][24+(int(MsgDataInClusterCount,16)*4):26+(int(MsgDataInClusterCount,16)*4)]
		Domoticz.Debug("Decode8043 - Reception Simple descriptor response : Out Cluster Count : " + MsgDataOutClusterCount)
		i=1
		if int(MsgDataOutClusterCount,16)>0 :
			while i <= int(MsgDataOutClusterCount,16) :
				MsgDataCluster=Dict_Data["MsgData"][24+((i-1)*4):24+(i*4)]
				if MsgDataCluster not in self.ListOfDevices[MsgDataShAddr]['Ep'][MsgDataEp] :
					self.ListOfDevices[MsgDataShAddr]['Ep'][MsgDataEp][MsgDataCluster]={}
				Domoticz.Debug("Decode8043 - Reception Simple descriptor response : Cluster out: " + MsgDataCluster)
				MsgDataCluster=""
				i=i+1
				
	return("Reception Simple descriptor response :  SQN : " + MsgDataSQN + ", Status : " + MsgDataStatus + ", short Addr : " + MsgDataShAddr + ", Lenght : " + MsgDataLenght)

## -----
## Power_Descriptor
## -----
## Definition :
## IN : Data dictionnary
## OUT: message for debug
## -----
def Power_Descriptor(self,Dict_Data):
	return("Reception Power descriptor response : " + Dict_Data["Data"])

## -----
## Active_Endpoints
## -----
## Definition :
## IN : Data dictionnary
## OUT: message for debug
## -----
def Active_Endpoints(self,Dict_Data):
	MsgDataSQN=Dict_Data["MsgData"][0:2]
	MsgDataStatus=Dict_Data["MsgData"][2:4]
	MsgDataShAddr=Dict_Data["MsgData"][4:8]
	MsgDataEpCount=Dict_Data["MsgData"][8:10]
	MsgDataEPlist=Dict_Data["MsgData"][10:len(MsgData)]
	
	OutEPlist=""
	DeviceExist(self, MsgDataShAddr)
	if self.ListOfDevices[MsgDataShAddr]['Status']!="inDB" :
		self.ListOfDevices[MsgDataShAddr]['Status']="8045"
	for i in MsgDataEPlist :
		OutEPlist+=i
		if len(OutEPlist)==2 :
			if OutEPlist not in self.ListOfDevices[MsgDataShAddr]['Ep'] :
				self.ListOfDevices[MsgDataShAddr]['Ep'][OutEPlist]={}
				OutEPlist=""
	return("Reception Active endpoint response : SQN : " + MsgDataSQN + ", Status " + MsgDataStatus + ", short Addr " + MsgDataShAddr + ", EP count " + MsgDataEpCount + ", Ep list " + MsgDataEPlist)

## -----
## Match_Descriptor
## -----
## Definition :
## IN : Data dictionnary
## OUT: message for debug
## -----
def Match_Descriptor(self,Dict_Data):
	return("Reception Match descriptor response : " + Dict_Data["Data"])

## -----
## Management_Leave
## -----
## Definition :
## IN : Data dictionnary
## OUT: message for debug
## -----
def Management_Leave(self,Dict_Data):
	return("Reception Management leave response : " + Dict_Data["Data"])

## -----
## Leave_Indication
## -----
## Definition :
## IN : Data dictionnary
## OUT: message for debug
## -----
def Leave_Indication(self,Dict_Data):
	return("Reception Leave indication : " + Dict_Data["Data"])

## -----
## Management_Network_Update
## -----
## Definition :
## IN : Data dictionnary
## OUT: message for debug
## -----
def Management_Network_Update(self,Dict_Data):
	return("Reception Management Network Update response : " + Dict_Data["Data"])

## -----
## System_Server_Discovery
## -----
## Definition :
## IN : Data dictionnary
## OUT: message for debug
## -----
def system_Server_Discovery(self,Dict_Data):
	return("Reception System server discovery response : " + Dict_Data["Data"])

## -----
## Management_LQI
## -----
## Definition :
## IN : Data dictionnary
## OUT: message for debug
## -----
def Management_LQI(self,Dict_Data):
	return("Reception Management LQI response : " + Dict_Data["Data"])

## -----
## Add_Group
## -----
## Definition :
## IN : Data dictionnary
## OUT: message for debug
## -----
def Add_Group(self,Dict_Data):
	return("Reception Add group response : " + Dict_Data["Data"])

## -----
## View_Group
## -----
## Definition :
## IN : Data dictionnary
## OUT: message for debug
## -----
def View_Group(self,Dict_Data):
	return("Reception View group response : " + Dict_Data["Data"])

## -----
## Get_Group
## -----
## Definition :
## IN : Data dictionnary
## OUT: message for debug
## -----
def Get_Group(self,Dict_Data):
	return("Reception Get group response : " + Dict_Data["Data"])

	
## -----
## Remove_Group
## -----
## Definition :
## IN : Data dictionnary
## OUT: message for debug
## -----
def Remove_Group(self,Dict_Data):
	return("Reception Remove group respons : " + Dict_Data["Data"])

## -----
## View_Scene
## -----
## Definition :
## IN : Data dictionnary
## OUT: message for debug
## -----
def View_Scene(self,Dict_Data):
	return("Reception View scene response : " + Dict_Data["Data"])

## -----
## Add_Scene
## -----
## Definition :
## IN : Data dictionnary
## OUT: message for debug
## -----
def Add_Scene(self,Dict_Data):
	return("Reception Add scene response : " + Dict_Data["Data"])

## -----
## Remove_Scene
## -----
## Definition :
## IN : Data dictionnary
## OUT: message for debug
## -----
def Remove_Scene(self,Dict_Data):
	return("Reception Remove scene response : " + Dict_Data["Data"])

## -----
## Remove_All_Scene
## -----
## Definition :
## IN : Data dictionnary
## OUT: message for debug
## -----
def Remove_All_Scene(self,Dict_Data):
	return("Reception Remove all scene response : " + Dict_Data["Data"])

## -----
## Store_Scene
## -----
## Definition :
## IN : Data dictionnary
## OUT: message for debug
## -----
def Store_Scene(self,Dict_Data):
	return("Reception Store scene response : " + Dict_Data["Data"])

## -----
## Scene_Membership
## -----
## Definition :
## IN : Data dictionnary
## OUT: message for debug
## -----
def Scene_Membership(self,Dict_Data):
	return("Reception Scene membership response : " + Dict_Data["Data"])

## -----
## Real_Individual_Attribute
## -----
## Definition :
## IN : Data dictionnary
## OUT: message for debug
## -----
def Real_Individual_Attribute(self,Dict_Data):
	return("Reception Real individual attribute response : " + Dict_Data["Data"])

## -----
## Default_Response
## -----
## Definition :
## IN : Data dictionnary
## OUT: message for debug
## -----
def Default_Response(self,Dict_Data):
	MsgDataSQN=Dict_Data["MsgData"][0:2]
	MsgDataEp=Dict_Data["MsgData"][2:4]
	MsgClusterId=Dict_Data["MsgData"][4:8]
	MsgDataCommand=Dict_Data["MsgData"][8:10]
	MsgDataStatus=Dict_Data["MsgData"][10:12]
	
	return(" reception Default response : SQN : " + MsgDataSQN + ", EP : " + MsgDataEp + ", Cluster ID : " + MsgClusterId + " , Command : " + MsgDataCommand+ ", Status : " + MsgDataStatus)

## -----
## Report_Individual_Attribute
## -----
## Definition :
## IN : Data dictionnary
## OUT: message for debug
## -----
def Report_Individual_Attribute(self,Dict_Data):
	MsgSQN=Dict_Data["MsgData"][0:2]
	MsgSrcAddr=Dict_Data["MsgData"][2:6]
	MsgSrcEp=Dict_Data["MsgData"][6:8]
	MsgClusterId=Dict_Data["MsgData"][8:12]
	MsgAttrID=Dict_Data["MsgData"][12:16]
	MsgAttType=Dict_Data["MsgData"][16:20]
	MsgAttSize=Dict_Data["MsgData"][20:24]
	MsgClusterData=Dict_Data["MsgData"][24:len(MsgData)]
	ReadCluster(self, Dict_Data["MsgData"])
	
	return("Report Individual Attribute response : data : " + MsgClusterData + " ClusterID : " + MsgClusterId + " Attribut ID : " + MsgAttrID + " Src Addr : " + MsgSrcAddr + " Scr Ep: " + MsgSrcEp)	
	
## -----
## Write_Attribute
## -----
## Definition :
## IN : Data dictionnary
## OUT: message for debug
## -----
def Write_Attribute(self,Dict_Data):
	return("Reception Write attribute response : " + Dict_Data["Data"])
	
## -----
## Zone_Status_Change_Notification
## -----
## Definition :
## IN : Data dictionnary
## OUT: message for debug
## -----		
def Zone_Status_Change_Notification(self,Dict_Data):
	MsgSrcAddr=Dict_Data["MsgData"][10:14]
	MsgSrcEp=Dict_Data["MsgData"][2:4]
	MsgClusterData=Dict_Data["MsgData"][16:18]
	
	return("Reception Zone status change notification : " + Dict_Data["MsgData"])
	
## -----
## Router_Discovery_Confirm
## -----
## Definition :
## IN : Data dictionnary
## OUT: message for debug
## -----		
def Router_Discovery_Confirm(self,Dict_Data):
	return("Reception Router discovery confirm : " + Dict_Data["Data"])

## -----
## APS_Data_Confirm_Fail
## -----
## Definition :
## IN : Data dictionnary
## OUT: message for debug
## -----	
def APS_Data_Confirm_Fail(self,Dict_Data):
	MsgDataStatus=Dict_Data["MsgData"][0:2]
	MsgDataSrcEp=Dict_Data["MsgData"][2:4]
	MsgDataDestEp=Dict_Data["MsgData"][4:6]
	MsgDataDestMode=Dict_Data["MsgData"][6:8]
	MsgDataDestAddr=Dict_Data["MsgData"][8:12]
	MsgDataSQN=Dict_Data["MsgData"][12:14]
	
	return("Reception APS Data confirm fail : Status : " + MsgDataStatus + ", Source Ep : " + MsgDataSrcEp + ", Destination Ep : " + MsgDataDestEp + ", Destination Mode : " + MsgDataDestMode + ", Destination Address : " + MsgDataDestAddr + ", SQN : " + MsgDataSQN)
