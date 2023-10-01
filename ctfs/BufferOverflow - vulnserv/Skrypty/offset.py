#!/usr/bin/python

import sys, socket

offset = "<output from above command>"

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('192.168.201.128', 9999))
        s.send(('TRUN /.:/' + offset))
        s.close()
except:
    print "Error occured while connecting to server"
    sys.exit()