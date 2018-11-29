#!/bin/bash

# Usage: benchmark.sh <NUMBER_OF_CARDS_TO_CREATE_AND_TEST> <CACHE_MODE>
# Example: benchmark.sh 100 name

cards_count=$1
cache_mode=$2
card_url="https://swtcgidc.files.wordpress.com/2018/08/card-of-the-week-bosb029_starkiller_base_b.jpg"
card_sha512_remote="74971777d8955323c97ae095735c0fc4542aa0f63cf3a9b8ad788a2fce43e3b296c6c80173a14a43a30f098675488732b60625583b90a9f63701dc0bd00c00cd"

mkdir /tmp/cards/
cd /tmp/cards/

if [[ -f 1.jpg ]]; then
    card_sha512_local=$(sha512sum /tmp/cards/1.jpg | awk {'print $1'})
fi

# Check to see if the card needs to be downloaded.
if [[ "$card_sha512_local" != "$card_sha512_remote" ]] || [[ ! -f 1.jpg ]]; then
    wget $card_url -O 1.jpg
fi

cards_count_current=$(ls -1 | wc -l)

# Check to see if the card needs to be copied.
if [[ "$cards_count_current" -gt "$cards_count" ]]; then
    echo "There are currently more cards than expected in /tmp/cards/. Please mnaually clean this up."
    exit 1
fi;

if [[ "$cards_count_current" -ne "$cards_count" ]]; then

    for i in $(seq 2 ${cards_count}); do
        cp 1.jpg $i.jpg
    done

fi

# The Linux kernel I/O cache is first flushed before starting to test to prevent inaccurate and faster-than-expected results.
echo 3 | sudo tee /proc/sys/vm/drop_caches && sync && time cgc-cli.py --cache ${cache_mode}
cd -
