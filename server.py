import datetime
import time
import socket

from matrix_client.client import MatrixClient

username="matrix username"
password="matrix password"
host="https://matrix.org"
room="matrix room id:matrix.org"

client=MatrixClient(host)
token=client.login(username,password)
huone=client.join_room(room)

serversocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
serversocket.bind(('192.168.0.101',10000))
serversocket.listen(5)

log = open('lampotila.log','a')
log2 = open('muut_tapahtumat.log','a')
etsi='therm'

now=datetime.datetime.now()
paiva=now.strftime("%d")

log.write(now.strftime("%d-%m-%Y %H:%M"))
log.write(' serveri kaynnistettiin\n')
log.flush()

log2.write(now.strftime("%d-%m-%Y %H:%M"))
log2.write(' serveri kaynnistettiin\n')
log2.flush()

huone.send_text("Serveri kaynnistyi")

try:
        print "Waiting connection"
        while True:
                connection, address = serversocket.accept()
                buf = connection.recv(1024)
                if len(buf) > 0:
                        now=datetime.datetime.now()

                        if paiva != now.strftime("%d"):
                                print "---Paiva:",now.strftime("%d-%m"),"---"
                                log.write(now.strftime("%d-%m-%Y"))
                                log.write('\n')
                                paiva=now.strftime("%d")
                                log.flush()

                        if etsi in buf:
                                try:
                                        arvo,kello,deg_in,max_in,min_in,deg_out,max_out,min_out=buf.split()
                                        local_kello=now.strftime("%H:%M")
                                        print "Local kello:",local_kello,"Kello:",kello,"Sisalampo:",deg_in,"Max:",max_in,"Min:",min_in
                                        print "Ulkolampotila:",deg_out,"Max:",max_out,"Min:",min_out
                                        temp_matrix="Kello:%s Sisalampo:%s Ulkolampo:%s" % (kello,deg_in,deg_out)
                                        huone.send_text(temp_matrix)
                                        log.write(buf)
                                        log.write('\n')
                                        log.flush()
                                except ValueError:
                                        print "error occured ",buf
                        else:
                                print 'Connected by:',address[0],buf
                                huone.send_text(buf)
                                log2.write(buf)
                                log2.write('\n')
                                log2.flush()


except KeyboardInterrupt:
        log.write(now.strftime("%d-%m-%Y %H:%M"))
        log.write(' serveri sammutettiin\n')

        log2.write(now.strftime("%d-%m-%Y %H:%M"))
        log2.write(' serveri sammutettiin\n')

        huone.send_text("serveri sammui")

        print "Serveri sammutetaan"
        serversocket.close()

print "Serveri sammui"
log.close()
log2.close()
