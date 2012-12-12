git add .
git commit -a -m "$1"
git push
ssh admin@dev.webiken.net "cd ~/reverse-dns/;git pull"
