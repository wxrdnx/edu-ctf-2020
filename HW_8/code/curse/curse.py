with open('unpack.exe', 'rb') as f:
    f.seek(0x3020)
    encrypt_table = f.read(0x2f8)
    f.seek(0x3320)
    cipher = f.read(0x4e)

decrypt_table = {}
for i in range(256):
    for j in range(0, 0x2f8, 2):
        result = encrypt_table[j]
        if i == result:
            decrypt_table[encrypt_table[j + 1]] = i

text = b''
for c in cipher:
    text += bytes([decrypt_table[c]])
print(text)
