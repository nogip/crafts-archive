# -*- coding: windows-1251 -*-
import os, sys, base64
from winreg import *
import socket
import time
from test_imports import print_me
import win32gui
import threading

host, port = '192.168.0.1', 80

sock = socket.socket()
sock.connect((host, port))

def alive(socket, msg):
    while True:
        socket.send(msg.encode('utf-8'))
        time.sleep(1)
        print_me()

alive(sock, 'IAM ALIVE\n')
# proc = threading.Thread(target=alive, args=(sock, ))
# proc.start()
# proc.join()

