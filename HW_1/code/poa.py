import pwn
import sys
import binascii
from Crypto.Cipher import AES

def unpad(data):
    for i in range(len(data) - 1, len(data) - 1 - 16, -1):
        if data[i] == 0x80:
            return data[:i]
        elif data[i] != 0x00:
            raise PaddingError
    raise PaddingError

if __name__ == '__main__':
    io = pwn.remote('140.112.31.97', 30000)
    io.recvuntil('cipher = ')
    cipher = io.recvline().strip()
    cipher = binascii.unhexlify(cipher)

    blocks = [cipher[i : i + 16] for i in range(0, len(cipher), 16)]
    
    plaintext = b''
    for b in range(len(blocks) - 1, 0, -1):
        iv = blocks[b - 1][:]
        for i in range(15, -1, -1):
            found = []
            for c in range(256):
                io.recvuntil('cipher = ')
                cipher_send = iv[:i] + bytes([c]) + iv[i + 1:] + blocks[b]
                cipher_send = binascii.hexlify(cipher_send)
                io.sendline(cipher_send)
                message = io.recvline().strip()
                if message == b'YESSSSSSSS':
                    found.append(c)
            if len(found) != 1:
                assert len(found) == 2
                found.remove(blocks[b - 1][i])
            plaintext = bytes([found[0] ^ 0x80 ^ blocks[b - 1][i]]) + plaintext
            print(plaintext)
            iv = iv[:i] + bytes([found[0] ^ 0x80]) + iv[i + 1:]

    print(unpad(plaintext))
