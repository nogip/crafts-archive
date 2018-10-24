from subprocess import PIPE, Popen, TimeoutExpired
from multiprocessing import Pipe, Process
import os, sys
import time
from threading import Timer


def shell(pipe, timeout=60.0):
    start = time.time()
    while time.time() - start <= timeout:
        cmd = pipe.recv()
        os.system(cmd)
        output = sys.stdin.read()
        pipe.send(output.encode('cp866'))
    return "TIMEOUT"



if __name__ == '__main__':
    parent, child = Pipe()
    proc = Process(target=shell, args=(child,))
    proc.start()
    while True:
        cmd = parent.send(input('>> '))
        symbol = parent.recv()
        print(symbol.decode('cp866'))
