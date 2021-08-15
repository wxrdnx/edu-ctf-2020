# HW 0xC Writeup

## Gift
本題是一個 gzip 檔。解完壓縮後可以看到名為 gift 的 binary。程式邏輯很簡單：輸入一串 key，比較如果 key 一樣的話，他會寫一串 binary 到 stdout。

![](https://i.imgur.com/s34DSNl.png)

![](https://i.imgur.com/Mr53iTM.png)

將輸出的那一大串 binary 經過 file 指令的檢驗後，是 gzip 檔。於是，將輸出資料存成 `gift2.gz`。然後，一樣解壓縮它。

![](https://i.imgur.com/ABnANEo.png)

把 binary 丟到 IDA，發現它一樣也是輸入 key，比較，吐資料。

![](https://i.imgur.com/JF3feet.png)

![](https://i.imgur.com/OtDzZvF.png)

一樣將輸出的那一大坨資料經過 file 指令的檢驗後，發現它仍舊是 gzip 檔。

![](https://i.imgur.com/7Qti3go.png)

基本猜想是這題很有可能用 gzip 將一大堆 binary 經過層層的壓縮，因此我覺得
寫 script 比手動解來的快許多。POC 的 script 在 code/gift/solution.sh 可以看
到，用法是 ./solution.sh。

不過，最後一個 binary 的 key 似乎有點怪怪的。

![](https://i.imgur.com/ZWJZFJv.png)

丟到 IDA 看看：

![](https://i.imgur.com/TgsDDMb.png)

發現 key 其實是
`@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@terrynini@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@`。

把這串字串送給./gift 後，就得到 flag 了。

![](https://i.imgur.com/Sk7r5ab.png)

## JustOnLinux

IDA 分析：

![](https://i.imgur.com/FvanLkp.png)

![](https://i.imgur.com/XMRDGvw.png)

本題是送分題，本質上就是 base64，只是字符被換掉而已。基本上寫 script 把字符換掉，做 base64 decode 後就行了。

![](https://i.imgur.com/Zyd6fCO.png)

POC script: code/solution.py
Usage: python3 solution.py

