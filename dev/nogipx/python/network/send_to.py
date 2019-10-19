import socket

def scan_port_all_hosts(network, port, count=255):
    # param network: is first 3 bytes in ip addr separated with dots
    print('[~] Start scanning ...')
    scanner = socket.socket()
    scanner.settimeout(1)
    for i in range(1, count+1):
        addr = '{}.{}'.format(network, i)
        try:
            scanner.connect_ex((addr, port))
            print('[+] Успешно подключен к {}'.format(addr))
        except socket.error as err:
            if str(err) != 'timed out':
                print('[+] Ошибка от {} - {}'.format(addr, err))
            continue

def send_to(addr, port, message, count=1):
    sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    dest = (addr, port)
    # sender.connect(dest)
    if isinstance(message, bytes):
        sender.sendto(message, dest)
    else:
        for i in range(count):
            sender.sendto(message.encode('utf-8'), dest)


row = b'E\x00\x004\x0fS@\x00\x80\x06\x00\x00\x7f\x00\x00\x01\x7f\x00\x00\x01\xeb\xc6\x158S!t\xeb\x00\x00\x00\x00\x80\x02\xfa\xf0\xb2\xed\x00\x00\x02\x04\xff\xd7\x01\x03\x03\x08\x01\x01\x04\x02'

# send_to('localhost', 5432, 'TEEEST')
send_to('localhost', 0, 'Test')
# send_to(sys.argv[1], int(sys.argv[2]), sys.argv[3], int(sys.argv[4]))