# HW7 writeup

## Solution

Let’s examine the go binary in IDA Pro:

![](https://i.imgur.com/A5tZLcf.png)

We can see that the functions are stripped, and there are 1258 functions found. Hence, it is difficult for us to find the main function. Luckily, there are several plugins that help us to rename the stripped function, and one of them is
[IDAGolangHelper](https://github.com/sibears/IDAGolangHelper).

After applying IDAGolangHelper, we can recover all of the
function names:

![](https://i.imgur.com/KknCQV4.png)

Now, we find the `main.main` function. Decompile it by pressing `<F5>`:

![](https://i.imgur.com/YtUdLXB.png)


The binary first read an input string from stdin, then it
checks whether the string length is greater that 3 and whether the initial and last characters are ‘x’. After that, it split your input into an array using ‘,’ as separator. Finally, it checks the validity of the string in main_check_input function. It’s reasonable to guess that the input string has something to do with the flag.

Let’s examine main_check_input:

![](https://i.imgur.com/qz2B7a6.png)

First, the function reads thirty-six 64 bit integers from unk_4D22A0 to v22, and thirty-six 64 bit integers from unk_4D23C0 to v20. Then, for each iteration in the for loop, it takes the (`16 * v20[i]`)’th entry from your input array, generates an integer from the main_bezu function, and compares it with `v22[i]`. If they are not the same, the loop ends and the function returns, which indicates that the verification process failed.

Now let’s check the `main_bezu` function:

![](https://i.imgur.com/gr170UO.png)

We can clearly see that the function calls `main_rchvf` and conduct some operations when it returns 1. The disassembly of `main_rchvf` is as follows: 

![](https://i.imgur.com/TXrDeWV.png)


Function main_rchvf is not easy to understand at first. But after some deep investigation, it reminds me of algorithm that I have learned in a cryptography course, that is the **Extended Euclidean algorithm**. `main_rchvf` behaves exactly the same as EE algorithm, and `main_bezu` seems to look for the modulo inverse in $Z_{4224019091}$

All in all, it seems that we can generate the flag by
calculating the modulo inverse of `v22[i]` and rearrange it
using the indices in `v20[i]`. The script can be examined in
`flag.py`.

## Script
```bash
python3 flag.py
```
