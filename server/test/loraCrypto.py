
from ctypes import CDLL, c_uint8, c_uint32,  create_string_buffer,byref
from binascii import hexlify, unhexlify
import os

Buffer = "5b481368a8f69bc0df35b57e5a2775bb746be181274ef26947c3400fb9beb50326e4b3eb58627df9a75187a5d74d17c8b92e"
AppSKey = "2b7e151628aed2a6abf7158809cf4f3c"

# Buffer = [0x5b,0x48,0x13,0x68,0xa8,0xf6,0x9b,0xc0,0xdf,0x35,0xb5,0x7e,0x5a,0x27,0x75,0xbb,0x74,0x6b,0xe1,0x81,0x27,0x4e,0xf2,0x69,0x47,0xc3,0x40,0x0f,0xb9,0xbe,0xb5,0x03,0x26,0xe4,0xb3,0xeb,0x58,0x62,0x7d,0xf9,0xa7,0x51,0x87,0xa5,0xd7,0x4d,0x17,0xc8,0xb9,0x2e]
# AppSKey = [0x2b,0x7e,0x15,0x16,0x28,0xae,0xd2,0xa6,0xab,0xf7,0x15,0x88,0x09,0xcf,0x4f,0x3c]

address = "6d609574"
dir = 0
sequenceCounter = 1

basedir = os.path.abspath(os.path.dirname(__file__))
class LoRaCrypto():
    def __init__(self):
        self.Crypto = CDLL(os.path.join(basedir, "loraCrypto.dll"))

    def PayloadEncrypt(self, buf, key, address, dir, sequenceCounter):
        bufferBin = unhexlify(buf)
        keyBin = unhexlify(key)
        addressInt = int(address, 16)
        enBuffer = (c_uint8 * 64)()
        self.Crypto.LoRaMacPayloadEncrypt(create_string_buffer(bytes(bufferBin)),
                                            c_uint8(len(bufferBin)),
                                            create_string_buffer(bytes(keyBin)),
                                            c_uint32(addressInt),
                                            c_uint8(dir),
                                            c_uint32(sequenceCounter),
                                            byref(enBuffer))
        return hexlify(bytes(enBuffer)[:len(bufferBin)]).decode()

def main():
    lc = LoRaCrypto()
    result = lc.PayloadEncrypt(Buffer, AppSKey, address, dir, sequenceCounter)
    print(result)
    
if __name__ == "__main__":
    main()



