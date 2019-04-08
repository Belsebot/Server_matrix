import datetime
import time
import socket

from matrix_client.client import MatrixClient

username="matrix username"              #your matrix username
password="matrix password"              #and password
host="https://matrix.org"               #matrix server
room="matrix room id:matrix.org"        #matrix room id

client=MatrixClient(host)               #connects to matrix
token=client.login(username,password)   #and
huone=client.join_room(room)            #joins chosen room

serversocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)         #starts server
serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)       #in 
serversocket.bind(('192.168.0.101',10000))                              #ip 192.168.0.101
serversocket.listen(5)                                                  #and port 10000

log = open('lampotila.log','a')                                         #makes log file where to store temperature information
log2 = open('muut_tapahtumat.log','a')                                  #makes log file where to storo other events
etsi='therm'                                                            #specific word to look for

now=datetime.datetime.now()                                             #gets current date and time
paiva=now.strftime("%d")                                                #current date

log.write(now.strftime("%d-%m-%Y %H:%M"))                               #writes current date to log file
log.write(' serveri kaynnistettiin\n')                                  #writes server started to log file
log.flush()                                                             #saves log file

log2.write(now.strftime("%d-%m-%Y %H:%M"))                              #writes current date to log file
log2.write(' serveri kaynnistettiin\n')                                 #writes server started to log file
log2.flush()                                                            #saves log file

huone.send_text("Serveri kaynnistyi")                                   #sends server started string to matrix room

try:                                                                    #main loop
        print "Waiting connection"                                      #
        while True:                                                     #loop
                connection, address = serversocket.accept()             #waiting connections
                buf = connection.recv(1024)
                if len(buf) > 0:                                        #if something is send to server then
                        now=datetime.datetime.now()                     #gets dates

                        if paiva != now.strftime("%d"):                                 #if date has changed 
                                print "---Paiva:",now.strftime("%d-%m"),"---"           #then print screen new date
                                log.write(now.strftime("%d-%m-%Y"))                     #and writes date to log file
                                log.write('\n')                                         #end of line
                                paiva=now.strftime("%d")                                #stores new date to variable
                                log.flush()                                             #saves log file

                        if etsi in buf:                                                 #if finds word in message
                                try:
                                        arvo,kello,deg_in,max_in,min_in,deg_out,max_out,min_out=buf.split()                                    #splits string to different variables
                                        local_kello=now.strftime("%H:%M")                                                                       #gets time
                                        print "Local kello:",local_kello,"Kello:",kello,"Sisalampo:",deg_in,"Max:",max_in,"Min:",min_in         #prints time and temperature information
                                        print "Ulkolampotila:",deg_out,"Max:",max_out,"Min:",min_out                                            #prints outside temperature information
                                        temp_matrix="Kello:%s Sisalampo:%s Ulkolampo:%s" % (kello,deg_in,deg_out)                               #gets inside and outside temperature information to variable
                                        huone.send_text(temp_matrix)                                                                            #and then send it to matrix room
                                        log.write(buf)                                                                                          #writes temperature information to log file
                                        log.write('\n')
                                        log.flush()                                                                                             #and saves log file
                                except ValueError:
                                        print "error occured ",buf
                        else:                                                                                                                   #gets other information than temperature information
                                print 'Connected by:',address[0],buf                                                                            #prints given message to screen
                                huone.send_text(buf)                                                                                            #and send it to matrix room
                                log2.write(buf)                                                                                                 #writes it to log file
                                log2.write('\n')
                                log2.flush()                                                                                                    #and saves log file


except KeyboardInterrupt:                                                       #when server is shutdown by user
        log.write(now.strftime("%d-%m-%Y %H:%M"))                               #writes date to log file
        log.write(' serveri sammutettiin\n')                                    #writes server shutdown to log file

        log2.write(now.strftime("%d-%m-%Y %H:%M"))                              #same to to the other log file
        log2.write(' serveri sammutettiin\n')

        huone.send_text("serveri sammui")                                       #send message server shutdown to matrix

        print "Serveri sammutetaan"
        serversocket.close()                                                    #closes socket

print "Serveri sammui"
log.close()                                                                     #closes 
log2.close()                                                                    #and saves log files
