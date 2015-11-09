# -*- cpdomg: utf-8 -*-
from ctypes import CDLL, c_uint8, c_uint32,  create_string_buffer, byref, c_ubyte
from binascii import hexlify, unhexlify
import os

Buffer = "5b481368a8f69bc0df35b57e5a2775bb746be181274ef26947c3400fb9beb50326e4b3eb58627df9a75187a5d74d17c8b92e"
AppSKey = "2b7e151628aed2a6abf7158809cf4f3c"

address = "6d609574"
dir = 0
sequenceCounter = 1
basedir = os.path.abspath(os.path.dirname(__file__))

from ctypes import CDLL, c_uint8, c_uint32,  create_string_buffer, byref, c_ubyte
from binascii import hexlify, unhexlify
import os
from server.app.config import LORIOT_BUFFER, LORIOT_APP_SKEY, LORIOT_ADDRESS
from json import dumps
Buffer = LORIOT_BUFFER
AppSKey = LORIOT_APP_SKEY

address = LORIOT_ADDRESS
dir = 0
sequenceCounter = 1
basedir = os.path.abspath(os.path.dirname(__file__))

def HexToByte(hexStr):
    bytes = []
    hexStr = ''.join(hexStr.split(" "))
    for i in range(0, len(hexStr), 2):
        bytes.append(chr(int(hexStr[i:i+2], 16)))
    return ''.join(bytes)

class LoRaCrypto():
    def __init__(self):
        self.Crypto = CDLL(os.path.join(basedir, "loraCrypto.dll"))

    def PayloadEncrypt(self, strBuffer, AppSKey, address, dir, sequenceCounter):
        rawBuffer = HexToByte(strBuffer)
        rawKey = HexToByte(AppSKey)

        addressInt = int(address, 16)
        enBuffer = (c_uint8 * 64)()
        self.Crypto.LoRaMacPayloadEncrypt(create_string_buffer(rawBuffer),
                                            c_uint8(len(rawBuffer)),
                                            create_string_buffer(rawKey),
                                            c_uint32(addressInt),
                                            c_uint8(dir),
                                            c_uint32(sequenceCounter),
                                            byref(enBuffer))
        return "".join(("%02x" % i) for i in enBuffer[:len(rawBuffer)])


def wrap_data(data, eui, sequence, direction=1):
    send_data = dict()
    send_data["cmd"] = "tx"
    send_data["EUI"] = eui
    send_data["port"] = 1
    packetStr = hexlify(data).decode()

    lc = LoRaCrypto()
    packetEncStr = lc.PayloadEncrypt(packetStr, AppSKey, address, direction, sequence)
    send_data["encdata"] = packetEncStr
    send_data["seqno"] = sequence

    return dumps(send_data)

def main():
    lc = LoRaCrypto()
    result = lc.payload_encrypt(Buffer, AppSKey, address, dir, sequenceCounter)
    print(result)
    
if __name__ == "__main__":
    print wrap_data('helloworld', 'BX300294', 20)


