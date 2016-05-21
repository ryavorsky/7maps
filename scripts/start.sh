#!/bin/bash

count_accs=5
count_members=$(python3 count_group_members.py 2>&1)

count_members_per_acc=$((($count_members+$count_accs-1)/$count_accs))

for ((i=0;i<($count_accs);i++)); do
    nohup python3 members_info.py $((i*count_members_per_acc)) $((($i+1)*$count_members_per_acc)) $i > "$i.out" &
done
