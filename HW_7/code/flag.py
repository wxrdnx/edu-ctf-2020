import ctypes

nums = [0xc8f9a829, 0xec83260e, 0xaf93c6f4, 0x5a1b89d9, 0x31e68d0d, 0xc38ce7e7, 0xc8f9a829, 0x4aee907b, 0xe0138a5f, 0x31e68d0d, 0x09975e45, 0xd129ea43, 0xc6830a2f, 0xc8f9a829, 0xec83260e, 0xec83260e, 0x13bf2b7f, 0xe0138a5f, 0xe419b183, 0xb2f1ddbb, 0xc38ce7e7, 0xc38ce7e7, 0x91639414, 0x5a1b89d9, 0x31e68d0d, 0x8c45c2b1, 0x0c76c360, 0x0876805b, 0x8d67dd2c, 0xc212d77c, 0xec83260e, 0x5a1b89d9, 0xe59d8403, 0x77244701, 0x1499761a, 0xeb6552fe]
pos = [0x0f, 0x20, 0x01, 0x1d, 0x17, 0x12, 0x0e, 0x1f, 0x1a, 0x08, 0x1b, 0x02, 0x10, 0x14, 0x15, 0x22, 0x13, 0x1c, 0x18, 0x16, 0x05, 0x07, 0x03, 0x19, 0x06, 0x00, 0x0d, 0x0c, 0x1e, 0x0b, 0x21, 0x09, 0x23, 0x0a, 0x11, 0x04]
prime = 0xfbc56a93
flag_len = 36
string = bytearray(flag_len)
for i in range(flag_len):
    n = pow(nums[i], -1, prime)
    string[pos[i]] = n
print(string)
