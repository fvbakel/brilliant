#
# Just some examples on how to work with bytes in python
from random import randbytes, randrange
import sys

def bytes_to_string(buffer: bytes) ->str:
    return bytes.hex()
    
def random_bytes(size:int) ->bytes:
    return randbytes(size)


def dump_bytes(buffer: bytes) -> None:
    int_value = int.from_bytes(buffer,byteorder=sys.byteorder)
    bin_value = bin(int_value)
    print(f"""
        buffer: {buffer} 
        hex: {buffer.hex(sep=' ', bytes_per_sep=2)} 
        int {int_value} 
        bin {bin_value}"""
    )

def main():
    buffer = random_bytes(4)
    print(buffer.hex())

    buffer = bytes.fromhex('FF')
    dump_bytes(buffer)

    buffer = bytes.fromhex('FFFF')
    dump_bytes(buffer)

    a_string = 'k'
    buffer = str.encode(a_string)
    dump_bytes(buffer)

    buffer = bytes.fromhex('FFFF FFFF')
    dump_bytes(buffer)

    print("Start count")
    for i in range(0,255):
        as_bytes = i.to_bytes(length=2,byteorder=sys.byteorder)
        bin_value = bin(i)
        print(f"i : {i} hex: {as_bytes.hex(sep=' ', bytes_per_sep=2)} bin {bin_value}")

    i = 0
    print(bin(i))
    i ^= 1 << 3
    print(bin(i))

    buffer = bytes.fromhex('FF FF FF FF')
    int_value = int.from_bytes(buffer,byteorder=sys.byteorder)
    dump_bytes(buffer)
    int_value ^= 1 << randrange(31)
    dump_bytes(int_value.to_bytes(4,byteorder=sys.byteorder))

    buffer = bytes.fromhex('FF FF FF FF')
    

    print('Ready')


if __name__ == '__main__':
    main()