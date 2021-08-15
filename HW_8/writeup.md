# HW8 Writeup
## WishMachine
### Description
First run the program in Linux environment:

![](https://i.imgur.com/IxqCdAl.png)

Let’s examine this binary with IDA Pro:

![](https://i.imgur.com/N0C9LBH.png)

We can see that the program first asks us for 1000 serials. Then, it validate these serials one by one. The flag is the result of xoring these 1000 serials.

## Anti-Anti-Debugging
If we examine this process with GDB, it will exit immediately. It seems that there is an anti-debugging mechanism hidden somewhere in the code. The most commonly used anti-debugging trickery in Linux is by exploiting the `ptrace` system call. ([reference](https://0x00sec.org/t/bypass-linux-basic-anti-debugging/22799))

```c=
#include <sys/ptrace.h>
#include <stdio.h>
int main()
{
    if (ptrace(PTRACE_TRACEME, 0, 0, 0) < 0 ) {
        printf("Debugger Found.\n");
        exit(0);
    }
    printf("No debugger, continuing\n");
    return 0;
}
```
Now search for ptrace system call in the binary using `strace`:

![](https://i.imgur.com/ZEL5iKO.png)

The program calls `ptrace(PTRACE_TRACEME)`, and the return value is -1. Indeed, anti-debugging mechanism is shown in this binary. We can use gdb command `catch syscall 101` to catch the ptrace system call:

![](https://i.imgur.com/GbFpKxK.png)

Afterwards, we analyze the function that contains 0x44a35f, which is 0x44a300:

![](https://i.imgur.com/8hk6vB6.png)

The function first retrieves several structures at 0x6d5100. A structure contains several fields listed below:

1. Validation function base pointer
2. Validation function offset (function address = base pointer + offset)
3. The character index to check.
4. The number of characters to check.
5. Validation value.

The function calls a validation function first. The validation function then performs some specific calculations on some input string characters. If the result matches the validation value, the validation function will return gracefully. Otherwise, the process complains and exits normally.

There are five different validation functions. Each of them is listed below:
1. 0x400fbe: check if $value = 135 \cdot char$

![](https://i.imgur.com/FmYTqJG.png)

2. 0x40102d: check if $value = 11 \cdot \lfloor \frac{char + 1}{2} \rfloor + 2 \cdot \lfloor \frac{char}{2} \rfloor$

![](https://i.imgur.com/sRjxTZ0.png)

3. 0x4011d6: check if $value = Fibonacci[char]$

![](https://i.imgur.com/O4Zdr8e.png)

4. 0x4010c8: check if $value = char \oplus \text{0x52756279}$

![](https://i.imgur.com/zeian1e.png)

5. 0x401138: check if $value = -88035316 - 30600 \cdot \lfloor \frac{char + 1}{2} \rfloor - 120 \cdot \lfloor \frac{char}{2} \rfloor$

![](https://i.imgur.com/vVaKkb4.png)

Since each of them is a one to one function, we can calculate the serial by extracting the structure in the binary and performing its reverse function on the character.

The calculation detail can be found in `wishMachine.py`.

Eventually, after sending the 1000 serials, the binary will undoubtly print the flag on the screen.

![](https://i.imgur.com/z5CiwQg.png)

# Curse
## Description
This binary is a windows 32-bit PE binary. First, throw this executable into IDA.

For `main` function:

![](https://i.imgur.com/aSyuLpg.png)

For `getAddress`:

![](https://i.imgur.com/kTmI3Si.png)

For `sub_4015C4`:

![](https://i.imgur.com/0p4P0Ha.png)

We can see that the main function calls `VirtualAlloc`, and calls `getAddresses` which invokes lots of `LoadLibraryA` and GetProcAddress. Then, the main function calls sub_4015C4 and performs an intricate calculation. Finally, the program ends...?

## Solution
According to my experience, the program seems to load some packed data-possably involving some important instructions- into a virtual allocated memory, resolve some necessary functions, and unpack the obfuscated instructions. So, let’s dynamically debug the program using x64dbg:

![](https://i.imgur.com/NhrQhF4.png)

After several trial and error, I finally figured out the real entry point of the main function is 0x319D0. Accordingly, I dump all the instructions in 0x319D0 to a temporary PE file called `unpack.exe` and analyze it using IDA:

![](https://i.imgur.com/gDHjc6A.png)

Here, we can see that the main function encodes your input and compares your input with a fix string. If these two string matches, the program will trigger `sub_2764`. According to my experience, the input string must be the final flag.

Let’s examine the encryption part. The encryption code is as follows:

![](https://i.imgur.com/gW5qWyj.png)

The encryption is basically a dictionary lookup. We can therefore obtain the flag by creating a reverse dictionary and using that dictionary to decode the encrypted string. The script `curse.py` contains the detailed implementation.

# SecureContainProtect
## Description
The binary is a 64-bit ELF binary. If we run it in Linux environment:

![](https://i.imgur.com/A5ZE8Qm.png)

So basically, it is a Sudoku solving challenge ?!

Unfornuately, I suck at Sudoku. So let’s solve it online!

![](https://i.imgur.com/0i4NUzN.png)

Enter the solution and we can see a secret panel:

![](https://i.imgur.com/IRCU935.png)

Let’s reverse this program with IDA:

![](https://i.imgur.com/DQFJfML.png)

So basically, if we provide the correct message, it will print magic which contains the ascii art of the flag. So we have to somehow guess the secret message.

The method I used to guess the secret message is to assume that the flag is `b'\0' * 32`. The, we can see some spooky hidden message:

![](https://i.imgur.com/Zx4GJZG.png)

It seems that the flag contains something like
`DECRYPT_THE_DOCUMENT_OF_...`. But after some investigation, I began to realize that the flag should be lowercases because if the secret message consists of uppercases, `v6` will be too small to fit in. Next, the `scp` field might have something to do with `SecureContainProtect`. Eventually, I looked up what secure container protect is and realized that maybe one of the SCP document name will be the suffix of the secret message

![](https://i.imgur.com/SqEkvsn.png)

After hours of trial and error, I finally got the correct secret message. It is `decrypt_the_document_of_SCP-2521`.

![](https://i.imgur.com/FGqwy9g.png)

The file `SecureContainProtect.py` contains the prove of concept script to get the flag.
