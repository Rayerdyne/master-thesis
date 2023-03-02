#!/bin/sh

if [ "$#" -lt 3 ]; then
    echo "Not enough arguments (Got $#)."
    echo "Usage: $0 <input> <output_dir> <output_basename>"
    exit 0
fi

file="$1"
out_dir="$2"
out_name="$3"

# create output directory if not exists
mkdir -p $out_dir

i=0
# delete first line then read them
sed 1,1d $file | while read line; do
    echo $line > "$out_dir/$out_name$i.txt"
    i=$((i+1))
done 