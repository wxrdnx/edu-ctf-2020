# HW1 writeup

## POA
本題的使用 AES 的 CBC mode 加密 flag，使用的 padding 方法是 ISO/IEC 7816，亦即 `'\x80' + '\x00' * (padding_length - 1)`。本題有很明顯的 Padding Oracle 漏洞：如果 padding 錯的話會回傳 `NOOOOOOOOO`，正確會回傳`YESSSSSSSS`。

Padding Oracle 原理課堂上提過了，這裏就不綴術了。[參考](https://www.youtube.com/watch?v=aH4DENMN_O4)

### script

參考 `poa.py`。大致的做法是猜最後一個 byte，如果是 '\x80' ，server 就會回傳 'YESSSSSSSS'，之後經過一些精密的 xor 後就能取得最後一個 byte 。然後，繼續猜倒數第二個 byte。依此類推就能取得整個 flag 。


## COR
本題的考點是 LFSR 的 Correlation Attack。概念是如果 "子 LFSR" 產生的 bitstream 和 output 的 bitstream 有極大的相關性（譬如 75%），那我們可以暴搜這個 "子 LFSR" 的所有可能的 feedback（本題的 feedback 是 16 個 bit，可以暴搜），如果猜測的 feedback 所產生的 bitstream 與 output bitstream 的 相關性大於某個值，那我們就能肯定這個 feedback 很有可能是對的 。

我使用的相關性公式如下：
```python
def corr(bits, bits_):
    return sum([(i == j) for i, j in zip(bits, bits_)]) / len(bits)
```
基本上就是看 output stream 之間互相 match 的比例。

本題的 LFSR3 和 output 的相關性約莫是 75%，LFSR2 和 output 的相關性約莫是 70%，LFSR1 $\oplus$ LFSR3 和 output 的相關性約莫是 68%。我沒有使用什麼神祕的技巧找到這些 相關性的，純粹是多試幾次就發現了。

### script

參考 `cor.py`。需要注意的是本題的 LFSR1 $\oplus$ LFSR3 與 output stream 之間的相關性有點難搞，有很多可能的 feedback 相關性都在 68% 左右。因此，找到最有可能 feedback 值的方法是過濾 printable 的 feedback，因為本提的三個 feedback 組成了本題的 flag ，所以猜測 `feedback.to_bytes(8, 'big').decode('latin1')` 的字串是 printable 是合理的。
