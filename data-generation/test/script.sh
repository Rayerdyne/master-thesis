sed -n -E "s/.*job id ([0-9]+).*/\1/p" finished.txt | head -n 5 > ids.tmp.txt
cat ids.tmp.txt | xargs -n1 -d'\n' -- seff | sed -n -E "s/CPU Utilized: ([0-9]+):([0-9]+).*/\1:\2/p" > times.tmp.txt
sort -g -r times.tmp.txt | uniq