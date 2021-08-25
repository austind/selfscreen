# selfscreen
Automate COVID-19 self-screening

## crontab
Run `crontab -e` then add:
```bash
55 7 * * 1-5 /usr/bin/python3 /home/shared/selfscreen/selfscreen.py -r -q -o /home/shared/selfscreen/selfscreen.log
```
Every M-F tarting at 7:55am, randomize assessment over a 12 minute interval

## bash
Add this to `~/.bash_profile`:

```bash
alias selfscreen='ssh sharedhost "/usr/bin/python3 /home/shared/selfscreen/selfscreen.py"'
```

then `source ~/.bash_profile` and run `selfscreen`
