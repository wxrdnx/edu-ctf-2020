with open('magic.dat', 'rb') as magic_f:
    magic = magic_f.read()
with open('solution.dat', 'rb') as solution_f:
    solution = solution_f.read()

action = b'decrypt_the_document_of_SCP-2521'
flag = b''
num = 0
for k in range(6015):
    flag += bytes([magic[k] ^ solution[k % 81] ^ action[k % len(action)]])
    num += flag[k]

print(flag.decode())
