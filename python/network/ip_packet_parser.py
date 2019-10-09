LOW_DELAY = 0b10000
HIGH_TROUGHPUT = 0b01000
HIGH_RELIABILITY = 0b00100

PRECEDENCE_NCTL = 0b111
PRECEDENCE_INCTL = 0b110
PRECEDENCE_CRITIC = 0b101
PRECEDENCE_FLASH_OVRD = 0b100
PRECEDENCE_FLASH = 0b011
PRECEDENCE_IMMEDIATE = 0b010
PRECEDENCE_PRIORITY = 0b001
PRECEDENCE_ROUTINE = 0b000

class IPPack:

    __fields_sizes__ = {
        "version": 4,
        "hdr_len": 4,
        "precedence": 3,
        "requirements": 5,
        "total_len": 16,
        "id": 16,
        "flags": 3,
        "fragment_offset": 13,
        "ttl": 8,
        "proto": 8,
        "checksum": 16,
        "src": 32,
        "dst": 32,
        "options": 32,
    }

    def __init__(self, data):
        self.header = bytearray(data[:20])
        self.data = bytearray(data[20:])
        self.analyze(self.header)

    def analyze(self, data):
        row = ''
        for block in self.hex2bin(data):
            row += block

        for key in IPPack.__fields_sizes__:
            size = IPPack.__fields_sizes__.get(key)

            value, row = self._trunc(row, size)

            self.__setattr__(key, value)

    def hex2bin(self, bin_seq):
        row = []
        for byte in bin_seq:
            fix = self._fix_bin(byte)
            row.append(fix)
        return row

    def _trunc(self, row, byte_count):
        truncated = row[:byte_count]
        row = row[byte_count:]
        return truncated, row

    def _fix_bin(self, value, fill=True):
        str_num = str(bin(value)).lstrip('0b')

        if fill:
            if len(str_num) < 8:
                str_num = "{}{}".format('0' * (8 - len(str_num)), str_num)
        return str_num

    def decode_ip(self, binary_row):
        if isinstance(binary_row, tuple):
            return binary_row

        ip = []
        block_count = len(binary_row) // 8
        for i in range(block_count):
            trunc_result = self._trunc(binary_row, 8)
            ip.append(int(trunc_result[0], 2))
            binary_row = trunc_result[1]
        return tuple(ip)

    def encode_ip(self, address_tuple):
        encoded_ip = ''
        for byte in address_tuple:
            encoded_ip += self._fix_bin(byte)
        return encoded_ip

    def try_decode(self, binary_row):
        if isinstance(binary_row, str):
            return int(binary_row, 2)
        return binary_row

    def decode_proto(self, proto_num):
        protos = {
            6: 'TCP', 17: 'UDP', 1: 'ICMP', 4: 'IP', 5: 'ST'
        }
        if proto_num in protos:
            return protos.get(proto_num)
        return proto_num

    def set_requirements(self, *args):
        result = 0b00000
        for option in args:
            result |= option
        self.requirements = self._fix_bin(result, fill=False)

    def set_precedence(self, precedence=PRECEDENCE_ROUTINE):
        self.precedence = self._fix_bin(precedence, fill=False)

    def set_src(self, address):
        if isinstance(address, tuple):
            self.src = address
        else:
            raise ValueError('IP addres must be in tuple')

    def set_dst(self, address):
        if isinstance(address, tuple):
            self.dst = address
        else:
            raise ValueError('IP addres must be in tuple')

    def generate_binary(self):
        bin_packet = ''
        for key in self.__dict__:
            if key in ['header', 'data']:
                continue
            value = self.__dict__.get(key)
            if key in ['src', 'dst']:
                value = self.encode_ip(value)
            bin_packet += value
        return bin_packet

    def __str__(self):
        self.src = self.decode_ip(self.src)
        self.dst = self.decode_ip(self.dst)

        res = '-' * 20 + '\n'
        for key in self.__dict__:
            value = (self.__dict__.get(key))
            res += "{} = {}\n".format(key, (value))
        res += '-' * 20 + '\n'
        return res
