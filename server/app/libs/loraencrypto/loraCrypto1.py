# -*- coding: utf-8 -*-
from ctypes import CDLL, c_uint8, c_uint32,  create_string_buffer,byref
from binascii import hexlify, unhexlify
import os

Buffer = unhexlify("5b481368a8f69bc0df35b57e5a2775bb746be181274ef26947c3400fb9beb50326e4b3eb58627df9a75187a5d74d17c8b92e")
AppSKey = unhexlify("2b7e151628aed2a6abf7158809cf4f3c")
address = 0x00AA1174
dir = 0
sequenceCounter = 1

basedir = os.path.abspath(os.path.dirname(__file__))

class LoRaCrypto():
    def __init__(self):
        try:
            self.Crypto = CDLL(os.path.join(basedir, "loraCrypto.dll"))
        except Exception, e:
            print 'load dll failed'
            raise e

    def payload_encrypt(self, buffer, key, address, dir, sequenceCounter):
        '''
        buffer：需要加密的数据，小于50个字节的十六进制字符串
        key：加密所用密钥，16个字节的十六进制字符串
        address：终端设备地址，4字节设备地址
        dir：数据方向，下行是1， 上行是0
        sequenceCounter：数据帧序号
        '''
        enBuffer = (c_uint8 * 64)()
        self.Crypto.LoRaMacPayloadEncrypt(create_string_buffer(bytes(buffer)),
                                          c_uint8(len(buffer)),
                                          create_string_buffer(bytes(key)),
                                          c_uint32(address),
                                          c_uint8(dir),
                                          c_uint32(sequenceCounter),
                                          byref(enBuffer))
        return hexlify(bytes(enBuffer)[:len(buffer)]).decode()

    def payload_decrypt(self, buffer, key, address, dir, sequenceCounter):
        decbuffer = (c_uint8 * 64)()
        self.Crypto.LoRaMacPayloadDecrypt(create_string_buffer(bytes(buffer)),
                                          c_uint8(len(buffer)),
                                          create_string_buffer(bytes(key)),
                                          c_uint32(address),
                                          c_uint8(dir),
                                          c_uint32(sequenceCounter),
                                          byref(decbuffer))

        return hexlify(bytes(decbuffer)[:len(buffer)]).decode()

def main():
    lc = LoRaCrypto()
    eb = LoRaCrypto().payload_encrypt(Buffer, AppSKey, address, dir, sequenceCounter)
    print(eb)

if __name__ == "__main__":
    main()

