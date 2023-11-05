import asyncio
import datetime
import time
import socket

from nio import AsyncClient,SyncResponse,MatrixRoom,RoomMessageText

username="matrix user"					#your Matrix username
password="matrix password"				#your Matrix password
host="https://matrix.org"				#matrix server
room="matrix room:matrix.org"				#matrix room id


async def send_message(asiakas,text):			#Send text to matrix room function

	await asiakas.room_send(
		room_id=room,
		message_type="m.room.message",
		content={"msgtype": "m.text", "body": text},
	)

async def palvelin(ss):					#Waiting connections function

	connection,address=ss.accept()			#Waiting connection
	buffer = connection.recv(1024)	
	buf=buffer.decode("utf-8")			#Decodes data to utf-8

	return (buf,address)				#Returns data and connection address

async def kello_f():					#Local time function

	nyt=datetime.datetime.now()			#Gets time
	kello=nyt.strftime("%H:%M")			#in Hour and Minutes

	return(kello)					#Returns time

async def paiva_f():					#Local date function

	nyt=datetime.datetime.now()			#Gets date

	return(nyt)					#Return date

async def main():					#Main funcion

	client = AsyncClient(host,username)		#Connects to Matrix server

	response = await client.login(password)		#and Logins in
	print (response)				#prints connection token

	ssocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)	#Starts server
	ssocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)	#in
	ssocket.bind(('192.168.0.100', 10000))				#ip 192.168.0.100 and port 10000
	ssocket.listen(5)						#and starts listing connections

	log = open('lampotila.log','a')					#Opens log file where it stores temperature data
	log2 = open('muut_tapahtumat.log','a')				#Opens log file where it stores other events
	etsi='therm'							#specific word to look for

	now=await paiva_f()						#Gets current date and time
	paiva=now.strftime("%d")					#Current date

	log.write(now.strftime("%d-%m-%Y %H:%M"))			#Writes current date and time to log file
	log.write(' uusi serveri kaynnistettiin\n')			#Writes server started to log file
	log.flush()							#Saves log file

	log2.write(now.strftime("%d-%m-%Y %H:%M"))			#Writes current date and time to log file
	log2.write(' uusi serveri kaynnistettiin\n')			#Writes server started to log file
	log2.flush()							#Saves log file

	await send_message(client,"Uusi Serveri kaynnistyi")		#Sends server started info to matrix room

	try:

		print ("Waiting connection")
		while True:						#Main loop

			buf,address=await palvelin(ssocket)		#waits connections

			if len(buf) > 0:				#if something is send to server then
				now=await paiva_f()			#Gets date

				if paiva != now.strftime("%d"):					#If date has changed
					print("---Paiva:",now.strftime("%d-%m"),"---")		#Then print screen new date
					log.write(now.strftime("%d-%m-%Y"))			#and writes date to log file
					log.write('\n')						#end of line
					paiva=now.strftime("%d")				#stores new date to variable
					log.flush()						#saves log file

				if etsi in buf:														#if specified word is in data stream
					arvo,kello,deg_in,max_in,min_in,deg_out,max_out,min_out=buf.split()						#split string to different variables
					local_kello=await kello_f()											#gets time
					print("Local Kello:",local_kello,"Kello:",kello,"Sisalampo:",deg_in,"Max:",max_in,"Min:",min_in)		#prints local time,time from client and temperature
					print("Ulkolampotila:",deg_out,"Max:",max_out,"Min:",min_out)							#prints outside temperature
					temp_matrix="Kello:%s Sisalampo:%s Ulkolampo:%s" % (kello,deg_in,deg_out)					#creates temperoral variable which hold time and inside and outside temperature
					await send_message(client,temp_matrix)										#sends that data to matrix room
					log.write(buf)													#writes data to log file
					log.write('\n')													#end of line
					log.flush()													#saves log file
			else:																#Else
				print ("Connected by:",address[0],buf)											#prints connected address and data to screen
				await send_message(client,buf)												#and sends it matrix room
				log2.write(buf)														#and saves that to log file
				log2.write('\n')													#end of line
				log2.flush()														#saves log file



	except KeyboardInterrupt:											#Keyboard interrupt
		now=await paiva_f()											#gets date

		log.write(now.strftime("%d-%m-%Y %H:%M"))								#writes date to log file
		log.write(' uusi serveri sammutettiin\n')								#and server is closed

		log2.write(now.strftime("%d-%m-%Y %H:%M"))								#writes date to log file
		log2.write(' uusi serveri sammutettiin\n')								#and server is closed

		print("Serveri sammutettiin")										#prints server closed
		ssocket.close()												#closes socket

	log.close()													#close and saves log file
	log2.close()													#close and saves log file



asyncio.run(main())				#Asyncio runs main loop
