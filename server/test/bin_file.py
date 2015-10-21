#-*- coding: utf-8 -*-

f = open('model.png', 'rb')
filesize = f.tell()
# filedata2 = bytearray(filedata)
f2 = open('model_copy.png','wb')

def do_something_with(chunk, f2):
    print 'hello'
    print bytearray(chunk)
    try:
        f2.write(chunk)
    except IOError:
        raise IOError


def read_file(f, f2):
    try:
        while True:
            chunk = f.read(64)
            if not chunk:
                break
            do_something_with(chunk, f2)
    finally:
        f.close()


if __name__ == '__main__':
    read_file(f, f2)
