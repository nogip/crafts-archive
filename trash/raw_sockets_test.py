import socket
from proto.ip import *

from send_to import send_to

local_port = 56757
local_host = '192.168.0.3'

proto = socket.IPPROTO_TCP
sniff = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sniff.connect((local_host, local_port))
# sniff.bind((local_host, local_port))
# sniff.setsockopt(proto, socket.IP_HDRINCL, 1)
# sniff.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

send_to(local_host, local_port, 'TEST')
# raw_packet = sniff.recvfrom(65565)[0]
# pack = IPPack(raw_packet)
# print(pack)

# while True:
#     raw_packet = sniff.recvfrom(1024)[0]
#     packet = IPPack(raw_packet)
#     packet.set_requirements(HIGH_RELIABILITY, LOW_DELAY)
#     packet.set_precedence(PRECEDENCE_FLASH)
#     packet.set_dst((192, 168, 0, 1))
#     print(raw_packet.hex())
#     print('+'*80)
#     print(packet.generate_binary())
#     # sniff.sendall(b"22F400205A220000801100007F0000017F000001")
#     # break

# 22F400205A220000801100007F0000017F000001
# 450000205a160000801100007f0000017f000001e48c0000000c75ad54455354

