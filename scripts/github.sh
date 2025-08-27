eval "$(ssh-agent -s)" > /dev/null
ssh-add ~/.ssh/devcybiko_github
ssh -T git@github.com
