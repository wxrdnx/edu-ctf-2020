#!/bin/bash
gzip_file="gift.gz"
binary="gift"
while [ $key != ";*3$" ]; do
    gunzip -f $gzip_file
    chmod 755 $binary
    key=$(strings gift | grep "wrong" -A 1 | tail -n 1)
    echo "$key" | ./$binary > $gzip_file
done
echo "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@terrynini@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@" | ./gift
