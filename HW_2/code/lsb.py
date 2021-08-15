from Crypto.Util.number import long_to_bytes, bytes_to_long
from pwn import *

e = 65537
while True:
    io = remote('140.112.31.97', 30001)
    #io = remote('127.0.0.1', 1234)

    io.recvuntil(b'n = ')
    n = int(io.recvlineS(keepends = False))
    io.recvuntil(b'c = ')
    c = int(io.recvlineS(keepends = False))

    if n % 3 != 1:
        io.close()
        continue

    else:
        io.sendline(str(c))
        io.recvuntil(b'm % 3 = ')
        mod = int(io.recvlineS(keepends = False))
        if mod != 0:
            continue
        
        # guess m mod 3 == 0 and n % 3 == 1
        left, right = 0, 1
        query = c
        for i in range(1024):
            query = (query * pow(2, e, n)) % n
            io.sendline(str(query))
            io.recvuntil(b'm % 3 = ')
            m = int(io.recvlineS(keepends = False))
            if m == (3 - left * 2) % 3:
                left, right = left * 2, right * 2 - 1
            elif m == (3 - left * 2 - 1) % 3:
                left, right = left * 2 + 1, right * 2
            else:
                print('impossible')
                continue

        print(long_to_bytes(left * n // (1 << 1024)), long_to_bytes(right * n // (1 << 1024)))
        io.close()
        break
