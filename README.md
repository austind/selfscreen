# selfscreen
Automate COVID-19 self-screening

## crontab
Run `crontab -e` then add:
```bash
55 7 * * 1-5 /usr/bin/python3 /home/shared/selfscreen/selfscreen.py -i 123456 -l Doe -m 6 -d 23 -r -q -o /home/shared/selfscreen/selfscreen.log
```
Every M-F tarting at 7:55am, randomize assessment over a 12 minute interval

## bash
Add this to `~/.bash_profile`:

```bash
alias selfscreen='ssh sharedhost "/usr/bin/python3 /home/shared/selfscreen/selfscreen.py -i 123456 -l Doe -m 6 -d 23"'
```

then `source ~/.bash_profile` and run `selfscreen`
