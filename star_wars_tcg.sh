#!/bin/bash
# Version: 2017.01.05

# this script is designed to automatically create printable sheets of eight 3.5 inch and 2.5 inch cards

source_dir="sw_tcg_print"
# count from 0 to 3 (4 total) before appending images together
append_card_count=0
# count what card number is currently being processed
current_card_count=0
# the total number of cards to be processed
total_card_count=$(\ls ${source_dir} | wc -l)
# create a build directory for processing
rm -rf /tmp/sw_tcg_build_append
rm -rf /tmp/sw_tcg_build_finish
mkdir /tmp/sw_tcg_build_append
mkdir /tmp/sw_tcg_build_finish

declare -a cards_to_combine

for card in $(\ls ${source_dir})
    do
    append_card_count=$(expr ${append_card_count} + 1)
    current_card_count=$(expr ${current_card_count} + 1) 
    cards_to_combine[${append_card_count}]="${source_dir}/${card}"

    # if there is a total of 4 cards, or if this loop is on the very last card
    # merge all of the cards together into one combined picture.
    if [ ${append_card_count} -eq 4 ] || [ ${current_card_count} -gt ${total_card_count} ];
        then echo "DEBUG: convert ${cards_to_combine[*]} +append /tmp/sw_tcg_build_append/${current_card_count}.jpg"
        # append the images, horizontally
        convert ${cards_to_combine[*]} +append /tmp/sw_tcg_build_append/${current_card_count}.jpg
        append_card_count=0
    fi


done

declare -a cards_to_combie_finish
append_card_count=0
loop_count=0

for appended_card in $(\ls /tmp/sw_tcg_build_append)
    do
    append_card_count=$(expr ${append_card_count} + 1)
    loop_count=$(expr ${loop_count} + 1)
    cards_to_combine_finish[${append_card_count}]="/tmp/sw_tcg_build_append/${appended_card}"

    if [ ${append_card_count} -eq 2 ];
        then echo "DEBUG: convert ${cards_to_combine_finish[*]} -append -page A4 /tmp/sw_tcg_build_finish/${loop_count}.jpg"
        # append the images, vertically
        convert ${cards_to_combine_finish[*]} -append -page A4 /tmp/sw_tcg_build_finish/${loop_count}.jpg
        append_card_count=0
        echo Checkpoint
    fi

done

