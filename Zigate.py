def read(Data):
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

	Dict_Data=[MsgType:Data[2:6]]
	Dict_Data=[MsgData:Data[12:len(Data)-4]]
	Dict_Data=[MsgRSSI:Data[len(Data)-4:len(Data)-2]]
	Dict_Data=[MsgLength:Data[6:10]]
	Dict_Data=[MsgCRC:Data[10:12]]
	Domoticz.Debug("ZigateRead - Message Type : " + Dict_Data[MsgType] + ", Data : " + Dict_Data[MsgData] + ", RSSI : " + Dict_Data[MsgRSSI] + ", Length : " + Dict_Data[MsgLength] + ", Checksum : " + Dict_Data[MsgCRC])

	MsgRetour=Zigate.Read[MsgType](Dict_Data)
   	Domoticz.Debug(MsgRetour)
    
 
