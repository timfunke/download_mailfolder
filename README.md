# `download_mailfolder.py`

The Python script `download_mailfolder.py` downloads mails from mailboxes and stores them locally as `.eml` files.

The downloads are configured in a JSON file like `configurations.json`.
The name of the configuration file needs to be passed as first argument when calling the script:
```
python3 download_mailfilder.py configurations.json
```
Here's an example of a `configurations.json` file. Inactive configurations can be marked by setting `active` to `false`.
```

[
  {
    "active": true,
    "imapserver": "outlook.office365.com",
    "username": "timfunke@nixinux.com",
    "password": "mysecretpassword",
    "imapfolder": "INBOX/personal",
    "directory": "/home/tim/archives/email/tim/nixinux/personal",
    "deleteAfterDownload": false,
    "numberOfMessages": 10000
  },
  {
    "active": false,
    "imapserver": "sslmail.myisp.io",
    "username": "1324",
    "password": "yetanotherpassword",
    "imapfolder": "INBOX.private.timmy",
    "directory": "/home/tim/archives/email/tim/private",
    "deleteAfterDownload": true,
    "numberOfMessages": 1000
  }
]
```
