#!/usr/bin/env bash
PRE_FOLDER=$1
POST_FOLDER=$2
cd $PRE_FOLDER || exit 1
for i in *.csv; do
    if [[ -e "$i" ]]; then
        if [ ! -f sorted/"$i".sorted ]; then
                sort <"$i" > sorted/"$i".sorted
        fi
        if [ ! -f $POST_FOLDER/sorted/"$i".sorted ]; then
                sort <$POST_FOLDER/"$i"> $POST_FOLDER/sorted/"$i".sorted
        fi
        if ! cmp -s sorted/"$i".sorted $POST_FOLDER/sorted/"$i".sorted; then
             echo $PRE_FOLDER/files sorted/"$i".sorted and $POST_FOLDER/sorted/"$i".sorted are different
             echo "the following lines are not in both files"
             comm -3 sorted/"$i".sorted $POST_FOLDER/sorted/"$i".sorted
        else
             echo files "$i" and $POST_FOLDER/"$i" are identical
             echo
        fi
    else
         echo "$POST_FOLDER/$i: not found" >&2
    fi
done
