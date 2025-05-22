# ssh-copy-id before doing below
# split file --> split -n 10 ../debuglogs.20240927-144416_26f6f713.tar.gz 27.
# ls | grep 27 | xargs -n 1 -P 10 ~/parallel_ssh.sh $(pwd) "aviuser@10.80.30.175:~/testing/AV-219088/"
# rm 27.*
# join files ---> cat 27.?? > debuglogs.20240927-144416_26f6f713.tar.gz

rsync -avz --progress $1/$3 $2
